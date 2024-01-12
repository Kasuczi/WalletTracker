import requests
import pandas as pd
from datetime import datetime


class CryptoTransactionTracker:
    def __init__(self, wallet_addresses, api_key):
        self.wallet_addresses = wallet_addresses
        self.api_key = api_key
        self.token_name_cache = {}

    def fetch_transactions(self):
        all_transactions = []
        for address in self.wallet_addresses:
            self.wallet_address = address
            transactions = self.fetch_eth_transactions()
            token_transactions = self.fetch_token_transactions()
            combined = pd.concat([transactions, token_transactions], ignore_index=True)
            combined['WalletAddress'] = address
            all_transactions.append(combined)
        return pd.concat(all_transactions, ignore_index=True)

    def fetch_eth_transactions(self):
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={self.wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={self.api_key}"
        return self.fetch_data_from_url(url)

    def fetch_token_transactions(self):
        url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={self.wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={self.api_key}"
        return self.fetch_data_from_url(url)

    def fetch_data_from_url(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data['result'])
        else:
            print("Error fetching transactions")
            return pd.DataFrame()

    def convert_timestamp(self, timestamp):
        return datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

    def filter_and_label_transactions(self, transactions):

        transactions['timeStamp'] = transactions['timeStamp'].apply(self.convert_timestamp)
        transactions['Type'] = transactions.apply(self.determine_transaction_type, axis=1)

        if 'tokenName' not in transactions.columns:
            transactions['tokenName'] = transactions['contractAddress'].apply(self.identify_cryptocurrency)

        return transactions

    def determine_transaction_type(self, transaction):
        if transaction['from'].lower() == self.wallet_address.lower():
            return 'Sell'
        else:
            return 'Buy'

    def identify_cryptocurrency(self, contract_address):
        if not contract_address:  # If there's no contract address, it's an ETH transaction
            return "ETH"

        if contract_address in self.token_name_cache:
            return self.token_name_cache[contract_address]

        url = f"https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress={contract_address}&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['result']:
                token_name = data['result'][0]['tokenName']
                self.token_name_cache[contract_address] = token_name  # Update cache
                return token_name
        return "Unknown Token"


if __name__ == "__main__":
    api_key = "ETHERSCAN_API_KEY"
    wallet_addresses = ["Wallet1",
                        "Wallet2"]
    tracker = CryptoTransactionTracker(wallet_addresses, api_key)

    transactions = tracker.fetch_transactions()
    combined_transactions = tracker.filter_and_label_transactions(transactions)
    combined_transactions.to_csv(r'path_to_csv_which_is_optional.csv', sep='|', decimal=',',
                                 index=False)
