# Scalable Capital Tax Exemption Tools

This repository contains two Python scripts designed to help German investors using Scalable Capital optimize their ETF portfolios by maximizing the use of the annual **Sparerpauschbetrag** (tax-free allowance on capital gains). The scripts are:

1. [`extract_transaction_history.py`](#1-extract_transaction_historypy)
2. [`portfolio_simulation.py`](#2-portfolio_simulationpy)

## Table of Contents

- [Scalable Capital Tax Exemption Tools](#scalable-capital-tax-exemption-tools)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Background](#background)
    - [German Taxation on ETFs](#german-taxation-on-etfs)
    - [Sparerpauschbetrag (Tax-Free Allowance)](#sparerpauschbetrag-tax-free-allowance)
  - [Scripts](#scripts)
    - [1. `extract_transaction_history.py`](#1-extract_transaction_historypy)
      - [Usage](#usage)
    - [2. `portfolio_simulation.py`](#2-portfolio_simulationpy)
      - [Usage](#usage-1)
  - [Calculating Shares to Sell](#calculating-shares-to-sell)
    - [Determining the Total Tax-Free Gain](#determining-the-total-tax-free-gain)
      - [Why the Script is Necessary](#why-the-script-is-necessary)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [License](#license)
  - [Disclaimer](#disclaimer)
  - [Contributions and Feedback](#contributions-and-feedback)
  - [Contact](#contact)

## Overview

The purpose of these scripts is to assist investors in:

- Parsing transaction history from text files exported from Scalable Capital and converting them into a structured CSV format.
- Simulating the current state of their ETF portfolio based on historical transactions.
- Calculating the number of shares that need to be sold to realize a specific amount of profit, aiming to maximize the use of the annual tax-free allowance.

## Background

### German Taxation on ETFs

In Germany, capital gains from the sale of ETFs (Exchange-Traded Funds) are subject to capital gains tax (**Abgeltungsteuer**) of 25%, plus a solidarity surcharge (**Solidaritätszuschlag**) and, if applicable, church tax (**Kirchensteuer**). However, certain ETFs benefit from a partial tax exemption (**Teilfreistellung**):

- **Equity ETFs**: 30% of the gains are tax-exempt, so only **70%** of the gains are taxable.
- **Other ETFs**: Different rates may apply.

### Sparerpauschbetrag (Tax-Free Allowance)

Every taxpayer in Germany is entitled to an annual tax-free allowance on capital gains, known as the **Sparerpauschbetrag**, which is currently **€1,000** for singles and **€2,000** for married couples filing jointly.

By strategically selling ETF shares to realize gains up to this allowance, investors can effectively earn profits without paying any capital gains tax.

## Scripts

### 1. `extract_transaction_history.py`

This script reads a transaction history from a text file (e.g., exported from your Scalable Capital account) and converts it into a structured CSV file for further processing.

#### Usage

1. **Prepare the Transaction History File**

   - Export your transaction history from Scalable Capital in text format (e.g., `transactions.txt`).
   - Ensure the file follows the expected format:

     ```
     Friday, 8 November 2024
     Buy
     ETF Name
     100 Shr.
     €5000

     Withdrawal
     Bank Account
     €1000
     ```

2. **Run the Script**

   ```bash
   python extract_transaction_history.py
   ```

3. **Output**

   - The script generates a `transactions.csv` file containing your transaction data in a structured format.

### 2. `portfolio_simulation.py`

This script processes the CSV file generated by `extract_transaction_history.py` to:

- Compute your current holdings.
- Calculate realized and unrealized profits/losses using the FIFO (First-In, First-Out) method.
- Simulate your portfolio based on fixed or current ETF prices.
- Determine the number of shares you need to sell to realize a desired amount of profit.

#### Usage

1. **Ensure `transactions.csv` is Available**

   - Make sure the `transactions.csv` file is in the same directory as the script.

2. **Configure Fixed Prices**

   - Update the `FIXED_PRICES` dictionary in the script with the current prices of your ETFs:

     ```python
     FIXED_PRICES = {
         'ETF Name A': 100.00,
         'ETF Name B': 50.00,
         # Add other ETFs and their prices
     }
     ```

3. **Run the Script**

   ```bash
   python portfolio_simulation.py
   ```

4. **Follow the Prompts**

   - The script will display your portfolio summary and prompt you to enter the desired profit amount (e.g., `1000` for €1,000).
   - It will then calculate and display the number of shares you need to sell for each ETF to realize that profit.

## Calculating Shares to Sell

Calculating the number of shares to sell to realize a specific amount of profit is complex due to:

- **FIFO Method**: Shares are sold in the order they were purchased. This affects the gain realized on each share since they may have been bought at different prices.
- **Partial Tax Exemption**: For equity ETFs, only **70%** of the gains are taxable due to the **30%** partial exemption.
- **Variable Purchase Prices**: If you bought shares at different times and prices, the gain per share varies.

### Determining the Total Tax-Free Gain

To fully utilize the **€1,000** annual tax-free allowance (**Sparerpauschbetrag**) with equity ETFs, you need to calculate the total amount of capital gains you can realize without incurring taxes.

**Since only 70% of your gains are taxable**, the total gain you can realize is:

\[
\text{Total Gain Required} = \frac{\text{Tax-Free Allowance}}{\text{Taxable Portion}} = \frac{1,000\,€}{0.70} \approx 1,428.57\,€
\]

**Therefore, you can realize approximately €1,428.57 in capital gains from equity ETFs without paying taxes.**

**Note:** This calculation assumes you have not used any portion of your tax-free allowance elsewhere.

#### Why the Script is Necessary

- **Complex Calculations**: If you've purchased shares at different times and prices, calculating the exact number of shares to sell to realize €1,428.57 in gains is not straightforward due to the FIFO accounting method.
- **Automated Processing**: The `portfolio_simulation.py` script automates these calculations, taking into account:
  - The purchase price of each lot of shares.
  - The order in which shares were bought (FIFO).
  - The current market price of the shares.
  - The partial tax exemption for equity ETFs.

By using the script, you can accurately determine how many shares you need to sell from your holdings to maximize your tax-free gains.

## Prerequisites

- **Python 3.7** or higher
- Required Python packages (listed in `requirements.txt`):

  ```text
  dataclasses
  ```

  - Note: The `dataclasses` module is included in Python 3.7 and higher. If you're using an older version, please upgrade Python.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/BertilBraun/Scalable-Capital-Tax-exemption.git
   cd Scalable-Capital-Tax-exemption
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Scripts**

   - Follow the usage instructions provided above for each script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is intended to assist with portfolio management and tax optimization strategies. It does **not** constitute financial or tax advice. Calculations are based on the information provided and may not account for all individual circumstances. Please consult with a financial advisor or tax professional to understand how these strategies apply to your personal situation.

## Contributions and Feedback

Feel free to open issues or pull requests if you find bugs or have suggestions for improvements.

## Contact

For any questions or feedback, you can reach out to the repository owner:

- **GitHub**: [BertilBraun](https://github.com/BertilBraun)
