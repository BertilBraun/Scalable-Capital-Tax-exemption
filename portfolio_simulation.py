import csv
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple

# Fixed current prices for your ETFs
FIXED_PRICES: Dict[str, float] = {
    'amundi msci world v (acc)': 18.80,
    'ishares core msci europe (acc)': 78.96,
    'amundi msci emerging markets ii (dist)': 47.12,
    # Add other ETFs and their fixed prices if needed
}


# Define your alias mapping here
ALIAS_MAPPING: Dict[str, List[str]] = {
    'amundi msci world v (acc)': [
        'amundi msci world v (acc)',
        'amundi msci world v ucits etf acc',
        'amundi msci world v',
        'lyxor core msci world (dr) ucits etf - acc',
        # Add other aliases if necessary
    ],
    'ishares core msci europe (acc)': [
        'ishares core msci europe (acc)',
        'ishares core msci europe ucits etf eur (acc)',
        'ishares core msci europe ucits etf eur',
        'ishares core msci europe',
        # Add other aliases if necessary
    ],
    'amundi msci emerging markets ii (dist)': [
        'amundi msci emerging markets ii (dist)',
        'amundi msci emerging markets ii ucits etf dist',
        'amundi msci emerging markets ii ucits etf',
        'amundi msci emerging markets ii',
        'lyxor msci emerging markets (lux) ucits etf',
        'lu2573966905',
        # Add other aliases if necessary
    ],
    # Include any other mappings if needed
}

# Create reverse mapping for quick lookup
INSTRUMENT_ALIAS: Dict[str, str] = {}
for canonical_name, aliases in ALIAS_MAPPING.items():
    for alias in aliases:
        INSTRUMENT_ALIAS[alias.lower()] = canonical_name


def get_canonical_name(instrument_name: str) -> str:
    """Get the canonical name for an instrument given its alias.

    Args:
        instrument_name (str): The instrument name or alias.

    Returns:
        str: The canonical name if found, otherwise returns the lowercased instrument name.
    """
    return INSTRUMENT_ALIAS.get(instrument_name.lower(), instrument_name.lower())


@dataclass
class Lot:
    date: str
    shares: float
    cost_per_share: float


@dataclass
class HoldingsData:
    lots: List[Lot]
    total_shares: float
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    total_cost: Optional[float] = None
    unrealized_pl: Optional[float] = None


def read_and_parse_transactions(filename: str) -> List[Dict[str, Any]]:
    """Read transactions from a CSV file, parse dates, and sort them chronologically.

    Args:
        filename (str): The path to the CSV file containing transactions.

    Returns:
        List[Dict[str, Any]]: A list of transaction dictionaries sorted by date.
    """
    transactions: List[Dict[str, Any]] = []

    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transactions.append(row)

    # Parse dates and sort transactions by date
    for row in transactions:
        date_str = row.get('Date', '').strip()
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            row['Date'] = date
        except ValueError:
            print(f'Warning: Invalid date format in transaction: {row}')
            row['Date'] = None  # Assign None to handle invalid dates

    # Sort transactions by date (oldest to newest)
    transactions.sort(key=lambda x: x['Date'] if x['Date'] is not None else datetime.min)

    return transactions


def process_transactions(transactions: List[Dict[str, Any]]) -> Tuple[Dict[str, HoldingsData], float]:
    """Process a list of transactions to compute holdings and realized profit/loss.

    Args:
        transactions (List[Dict[str, Any]]): A list of transaction dictionaries sorted by date.

    Returns:
        Tuple[Dict[str, HoldingsData], float]: A tuple containing the holdings dictionary and realized profit/loss.
    """
    holdings: Dict[str, HoldingsData] = {}
    realized_pl: float = 0.0

    # Process transactions in chronological order
    for row in transactions:
        transaction_type = row.get('Transaction Type', '').strip()
        instrument = row.get('Instrument Name', '').strip()
        amount_str = row.get('Amount', '').replace('€', '').replace(',', '').strip() or '0.0'
        shares_str = row.get('Shares', '').replace(',', '').strip() or '0.0'
        date = datetime.strftime(row['Date'], '%Y-%m-%d') if row['Date'] else 'Unknown'

        # Map instrument name to canonical name
        instrument_canonical = get_canonical_name(instrument)

        if transaction_type in ['Deposit', 'Withdrawal']:
            # Deposits and Withdrawals are ignored in holdings calculation
            continue

        if transaction_type == 'Distribution':
            try:
                amount = float(amount_str)
                realized_pl += amount
            except ValueError:
                print(f'Warning: Invalid amount in Distribution transaction: {row}')
            continue

        # Parse amount and shares
        try:
            amount = float(amount_str)
            shares = float(shares_str)
        except ValueError:
            print(f'Warning: Skipping invalid transaction: {row}')
            continue

        if transaction_type in ['Buy', 'Savings Plan', 'Swap in']:
            if instrument_canonical not in holdings:
                holdings[instrument_canonical] = HoldingsData(lots=[], total_shares=0.0)
            # Amount is negative for buys, so cost per share is -amount / shares
            cost_per_share = abs(amount / shares) if shares != 0 else 0.0
            holdings[instrument_canonical].lots.append(Lot(date=date, shares=shares, cost_per_share=cost_per_share))
            holdings[instrument_canonical].total_shares += shares

        elif transaction_type in ['Sell', 'Swap out']:
            if instrument_canonical in holdings:
                shares_to_sell = shares
                sale_price_per_share = amount / shares if shares != 0 else 0.0
                # Apply FIFO method to match sold shares with purchase lots
                while shares_to_sell > 0 and holdings[instrument_canonical].lots:
                    lot = holdings[instrument_canonical].lots[0]
                    lot_shares = lot.shares
                    if lot_shares <= shares_to_sell:
                        # Sell the entire lot
                        profit = (sale_price_per_share - lot.cost_per_share) * lot_shares
                        realized_pl += profit
                        shares_to_sell -= lot_shares
                        holdings[instrument_canonical].total_shares -= lot_shares
                        holdings[instrument_canonical].lots.pop(0)
                    else:
                        # Sell part of the lot
                        profit = (sale_price_per_share - lot.cost_per_share) * shares_to_sell
                        realized_pl += profit
                        lot.shares -= shares_to_sell
                        holdings[instrument_canonical].total_shares -= shares_to_sell
                        shares_to_sell = 0
                if shares_to_sell > 0:
                    print(f'Warning: Sold more shares than owned for {instrument_canonical}')
            else:
                print(f'Warning: Sold shares of {instrument_canonical} which is not in holdings')

    return holdings, realized_pl


def simulate_portfolio(
    holdings: Dict[str, HoldingsData], realized_pl: float
) -> Tuple[Dict[str, HoldingsData], float, float, float, float]:
    """Simulate the portfolio based on fixed prices and calculate total values and profits.

    Args:
        holdings (Dict[str, HoldingsData]): The holdings dictionary.
        realized_pl (float): The realized profit/loss.

    Returns:
        Tuple[Dict[str, HoldingsData], float, float, float, float]: A tuple containing the updated holdings,
        total current value, total profit, total unrealized profit/loss, and realized profit/loss.
    """
    total_current_value = 0.0
    total_unrealized_pl = 0.0

    for instrument, data in holdings.items():
        if data.total_shares > 0:
            # Use fixed price if available
            current_price = FIXED_PRICES.get(instrument)
            if current_price is None:
                print(f"Warning: No fixed price for '{instrument}'. Skipping.")
                continue

            total_cost = 0.0
            total_value = data.total_shares * current_price

            # Calculate total cost of remaining shares
            for lot in data.lots:
                total_cost += lot.shares * lot.cost_per_share

            unrealized_pl = total_value - total_cost

            # Update holdings data with current price and calculations
            data.current_price = current_price
            data.current_value = total_value
            data.total_cost = total_cost
            data.unrealized_pl = unrealized_pl

            total_current_value += total_value
            total_unrealized_pl += unrealized_pl

    total_profit = realized_pl + total_unrealized_pl

    return holdings, total_current_value, total_profit, total_unrealized_pl, realized_pl


def calculate_shares_to_sell(holdings: Dict[str, HoldingsData], desired_profit: float) -> None:
    """Calculate and display the number of shares to sell to realize a desired profit.

    Args:
        holdings (Dict[str, HoldingsData]): The holdings dictionary.
        desired_profit (float): The desired profit amount.
    """
    print(f'\nCalculating shares to sell to realize a profit of €{desired_profit:.2f}...\n')
    for instrument, data in holdings.items():
        if data.total_shares > 0 and data.current_price:
            current_price = data.current_price
            shares_to_sell = 0.0
            realized_profit = 0.0
            total_proceeds = 0.0
            total_cost_basis = 0.0

            # Apply FIFO method to simulate selling shares
            for lot in data.lots:
                if realized_profit >= desired_profit:
                    break
                sellable_shares = lot.shares
                proceeds = sellable_shares * current_price
                cost_basis = sellable_shares * lot.cost_per_share
                profit = proceeds - cost_basis

                shares_to_sell += sellable_shares
                realized_profit += profit
                total_proceeds += proceeds
                total_cost_basis += cost_basis

            if realized_profit >= desired_profit:
                # Adjust the last lot to only sell the required number of shares
                excess_profit = realized_profit - desired_profit
                if current_price != lot.cost_per_share:
                    excess_shares = excess_profit / (current_price - lot.cost_per_share)
                else:
                    excess_shares = 0.0
                shares_to_sell -= excess_shares
                total_proceeds -= excess_shares * current_price
                total_cost_basis -= excess_shares * lot.cost_per_share
                realized_profit = desired_profit

                print(f"To realize a profit of €{desired_profit:.2f} from '{instrument}':")
                print(f'  Sell {shares_to_sell:.4f} shares at €{current_price:.2f} per share.')
                print(f'  Total Proceeds: €{total_proceeds:.2f}')
                print(f'  Cost Basis of Shares Sold: €{total_cost_basis:.2f}')
                print(f'  Realized Profit: €{realized_profit:.2f}\n')
            else:
                print(f"Not enough shares in '{instrument}' to realize a profit of €{desired_profit:.2f}.")
                print(
                    f'You would need to sell all {shares_to_sell:.4f} shares, resulting in a profit of €{realized_profit:.2f}.\n'
                )


def display_portfolio(
    holdings: Dict[str, HoldingsData],
    total_current_value: float,
    total_profit: float,
    total_unrealized_pl: float,
    realized_pl: float,
) -> None:
    """Display the portfolio summary and holdings details.

    Args:
        holdings (Dict[str, HoldingsData]): The holdings dictionary.
        total_current_value (float): The total current value of the portfolio.
        total_profit (float): The total profit/loss.
        total_unrealized_pl (float): The total unrealized profit/loss.
        realized_pl (float): The total realized profit/loss.
    """
    print('\nPortfolio Summary:')
    print(f'Total Current Value: €{total_current_value:.2f}')
    print(f'Total Realized Profit/Loss: €{realized_pl:.2f}')
    print(f'Total Unrealized Profit/Loss: €{total_unrealized_pl:.2f}')
    print(f'Total Profit/Loss: €{total_profit:.2f}\n')

    print('Holdings:')
    for instrument, data in holdings.items():
        if data.total_shares > 0:
            print(f'- {instrument}:')
            print(f'  Shares Held: {data.total_shares:.4f}')
            if data.current_price is not None:
                print(f'  Current Price: €{data.current_price:.2f}')
            if data.current_value is not None:
                print(f'  Current Value: €{data.current_value:.2f}')
            if data.total_cost is not None:
                print(f'  Total Cost: €{data.total_cost:.2f}')
            if data.unrealized_pl is not None:
                print(f'  Unrealized Profit/Loss: €{data.unrealized_pl:.2f}\n')


def main() -> None:
    """Main function to process transactions and simulate portfolio."""
    # Read and parse transactions from the CSV file
    transactions = read_and_parse_transactions('transactions.csv')

    # Process the transactions to get holdings and realized profit/loss
    holdings, realized_pl = process_transactions(transactions)

    # Save current holdings to a JSON file
    with open('current_holdings.json', 'w') as f:
        json.dump({k: asdict(v) for k, v in holdings.items()}, f, indent=4)

    # Simulate the portfolio based on fixed prices
    holdings, total_current_value, total_profit, total_unrealized_pl, realized_pl = simulate_portfolio(
        holdings, realized_pl
    )

    # Display the portfolio summary
    display_portfolio(holdings, total_current_value, total_profit, total_unrealized_pl, realized_pl)

    # Ask the user for the desired profit
    desired_profit_str = input(
        '\nEnter the desired profit amount (max free amount for equity etfs is 1429 (in 2024)): €'
    ).replace(',', '.')
    try:
        desired_profit = float(desired_profit_str)
        calculate_shares_to_sell(holdings, desired_profit)
    except ValueError:
        print('Invalid input for desired profit.')


if __name__ == '__main__':
    main()
