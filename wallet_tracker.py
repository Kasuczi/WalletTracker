import requests
import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
            logging.info(f"Wallet data feached for {self.wallet_address}")
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
        utc_time = datetime.utcfromtimestamp(int(timestamp))
        local_time = utc_time + timedelta(hours=1)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

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


class CurrentDayCryptoTransactionTracker(CryptoTransactionTracker):
    def fetch_eth_transactions(self):
        start_block = self.calculate_start_block_for_today()
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={self.wallet_address}&startblock={start_block}&endblock=99999999&sort=asc&apikey={self.api_key}"
        return self.fetch_data_from_url(url)

    def fetch_token_transactions(self):
        start_block = self.calculate_start_block_for_today()
        url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={self.wallet_address}&startblock={start_block}&endblock=99999999&sort=asc&apikey={self.api_key}"
        return self.fetch_data_from_url(url)

    def calculate_start_block_for_today(self):
        avg_block_time = 14  # in seconds

        now = datetime.utcnow()
        midnight_utc = datetime(now.year, now.month, now.day)
        seconds_since_midnight = (now - midnight_utc).total_seconds()
        blocks_since_midnight = int(seconds_since_midnight / avg_block_time)

        url = f"https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            current_block = int(response.json()['result'], 16)
            start_block = current_block - blocks_since_midnight
            return max(start_block, 0)
        else:
            logging.error("Error fetching the latest block number")
            return 0


if __name__ == "__main__":
    api_key = "AKHAMYBR2CHS5GYRU8PYAK1S19GKAVPYD4"
    wallet_addresses = ["0x618d6c2a6cc1aa17f411e2b2000ee00895334d87",
                        "0x4322fd98f95a219d2aae2bba6664e3574b4c3708",
                        "0x6400f6ebf6e958ec1887c92f30515bbad3745073",
                        "0x4401fe38292256a2fc3b2054c44a2fae12b68ac1",
                        "0xbba84019aeaaa8b736e1d9c7c1c6074fd47d75db",
                        "0xa3737deca37c6d15c582309d766322bad789e6fa",
                        "0xea55c928c2549722a21541d3b6c20d845eb28c2c",
                        "0x8b94f9c38a6cacc49cbd48ad867c0a9c2f89eb11",
                        "0x390a7731bb3573617c59060c6b3764664f15dada",
                        "0x25cd302e37a69d70a6ef645daea5a7de38c66e2a",
                        "0x618d6c2a6cc1aa17f411e2b2000ee00895334d87",
                        "0xa2d18c5ca7170c55aed88793f1b06386d1e20a2d",
                        "0x287e2c76aab4720786076c3deedd7dd386092050",
                        "0x59220979d662bb96b40b5b47c5cc8939254f4d72",
                        "0x0b6a06c07c58d13b6c725dbdb9cd1e2f6bac5527",
                        "0x4823be7f266c5bca85b7dbd8e41f4710e1c49a7b",
                        "0x9bcb2c3cbf1073e47f3c5c31f8ae8c7b951bb016"]

    tracker = CryptoTransactionTracker(wallet_addresses, api_key)

    transactions = tracker.fetch_transactions()
    combined_transactions = tracker.filter_and_label_transactions(transactions)
    combined_transactions.to_csv(r'C:\Users\janik\OneDrive\Pulpit\coingecko\wallet_tracker.csv', sep='|', decimal=',',
                                 index=False)

    # current_day_tracker = CurrentDayCryptoTransactionTracker(wallet_addresses, api_key)
    # current_day_transactions = current_day_tracker.fetch_transactions()
    # current_day_combined_transactions = current_day_tracker.filter_and_label_transactions(current_day_transactions)

    # grouped = current_day_combined_transactions.groupby(['tokenSymbol', 'contractAddress', 'Type'])
    # filtered = grouped.filter(lambda x: x['walletAddress'].nunique() >= 3)
    # result = filtered.groupby(['tokenSymbol', 'contractAddress',  'Type']).agg({'timeStamp': 'max'}).reset_index()

    # previous_data = []
    # json_result = result.to_json(orient='records')
    # new_records = [item for item in json_result if item not in previous_data]
    # if new_records:
    #     message_str = "".join(format_message(record) for record in new_records)
    # previous_data = new_json_data

