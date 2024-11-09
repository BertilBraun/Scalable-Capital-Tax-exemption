import csv
from typing import List, Dict
from datetime import datetime


def is_date(line: str) -> bool:
    """Check if a line is a date in the format 'Friday, 8 November 2024'.

    Args:
        line (str): The line to check.

    Returns:
        bool: True if the line is a date, False otherwise.
    """
    try:
        datetime.strptime(line, '%A, %d %B %Y')
        return True
    except ValueError:
        return False


def parse_date(line: str) -> str:
    """Parse a date line and return it in 'YYYY-MM-DD' format.

    Args:
        line (str): The date line to parse.

    Returns:
        str: The date in 'YYYY-MM-DD' format.
    """
    return datetime.strptime(line, '%A, %d %B %Y').strftime('%Y-%m-%d')


def read_transactions_file(filename: str) -> List[str]:
    """Read the transactions file and return a list of lines.

    Args:
        filename (str): The path to the transactions file.

    Returns:
        List[str]: A list of lines from the file.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines


def process_transactions(lines: List[str]) -> List[Dict[str, str]]:
    """Process a list of lines from a transactions file to extract transaction data.

    Args:
        lines (List[str]): The list of lines from the transactions file.

    Returns:
        List[Dict[str, str]]: A list of transaction dictionaries.
    """
    transactions: List[Dict[str, str]] = []
    current_date: str = '0000-00-00'
    current_transaction: Dict[str, str] = {}
    transaction_types = ['Deposit', 'Withdrawal', 'Savings Plan', 'Buy', 'Sell', 'Distribution', 'Swap in', 'Swap out']

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue  # Skip empty lines

        if is_date(line):
            current_date = parse_date(line)
            i += 1
            continue

        if line in transaction_types:
            transaction_type = line
            current_transaction = {'Date': current_date, 'Transaction Type': transaction_type}
            i += 1

            # Handle 'Rejected' transactions
            if i < len(lines) and lines[i].strip() == 'Rejected':
                # Skip the next lines until we find a new transaction or date
                i += 1
                while i < len(lines) and not is_date(lines[i].strip()) and lines[i].strip() not in transaction_types:
                    i += 1
                continue

            # Process the transaction details
            while i < len(lines):
                next_line = lines[i].strip()

                if is_date(next_line) or next_line in transaction_types:
                    # End of current transaction
                    break

                elif next_line.endswith('Shr.'):
                    shares = next_line[:-5].strip()  # Remove ' Shr.'
                    current_transaction['Shares'] = shares

                elif next_line.startswith('€'):
                    amount = next_line[1:].strip()  # Remove '€' and strip whitespace
                    current_transaction['Amount'] = amount

                    # Append the transaction and reset
                    transactions.append(current_transaction.copy())
                    current_transaction = {'Date': current_date, 'Transaction Type': transaction_type}

                else:
                    if transaction_type in ['Deposit', 'Withdrawal', 'Distribution']:
                        current_transaction['Description'] = next_line
                    else:
                        current_transaction['Instrument Name'] = next_line

                i += 1
        else:
            i += 1  # Skip unrecognized lines

    return transactions


def write_csv(transactions: List[Dict[str, str]], filename: str = 'transactions.csv') -> None:
    """Write the list of transactions to a CSV file.

    Args:
        transactions (List[Dict[str, str]]): The list of transaction dictionaries.
        filename (str, optional): The name of the CSV file to write to. Defaults to 'transactions.csv'.
    """
    # Determine the fieldnames based on all keys in transactions
    fieldnames = set()
    for tx in transactions:
        fieldnames.update(tx.keys())
    fieldnames = sorted(fieldnames)

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for tx in transactions:
            writer.writerow(tx)


def main() -> None:
    """Main function to process transactions from a text file and write them to a CSV file."""
    # Read the data from the text file
    lines = read_transactions_file('transactions.txt')

    # Process the transactions
    transactions = process_transactions(lines)

    # Write the transactions to a CSV file
    write_csv(transactions)

    print("Transactions have been successfully written to 'transactions.csv'.")


if __name__ == '__main__':
    main()
