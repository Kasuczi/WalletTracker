
# CryptoTransactionTracker

## Overview
CryptoTransactionTracker is a Python tool designed to track and analyze cryptocurrency transactions from Ethereum wallets. It fetches transaction data from the Etherscan API, processes it, and compiles detailed transaction histories for specified wallet addresses.

## Features
- Fetch Ethereum and token transactions from multiple wallet addresses.
- Identify and label transaction types (Buy/Sell).
- Convert Unix timestamps to human-readable dates.
- Cache token names to optimize performance.
- Export transaction data to a CSV file.

## Installation
To use CryptoTransactionTracker, you need Python 3 and the following packages:
- `requests`
- `pandas`

Install the required packages using pip:
```
pip install requests pandas
```

## Usage
1. **Set up API Key**: Obtain an API key from [Etherscan.io](https://etherscan.io/apis).
2. **Configure Wallet Addresses**: List the Ethereum wallet addresses you want to track.
3. **Run the Tracker**: Use the script to fetch and process transaction data.

Example:
```python
from CryptoTransactionTracker import CryptoTransactionTracker

api_key = "YOUR_ETHERSCAN_API_KEY"
wallet_addresses = ["Wallet1_Address", "Wallet2_Address"]
tracker = CryptoTransactionTracker(wallet_addresses, api_key)

transactions = tracker.fetch_transactions()
combined_transactions = tracker.filter_and_label_transactions(transactions)
combined_transactions.to_csv('path_to_your_csv_file.csv', sep='|', decimal=',', index=False)
```

## Contribution
Contributions to the CryptoTransactionTracker are welcome. Here are some ways you can contribute:
- Reporting bugs
- Suggesting enhancements
- Submitting pull requests for new features or bug fixes


Feel free to adjust the content according to your specific needs and preferences. For instance, if you have additional features, dependencies, or specific installation steps, make sure to include them. Also, choose an appropriate license for your project.
