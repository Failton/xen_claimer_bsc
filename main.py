from web3 import Web3
from loguru import logger
from sys import stderr
from threading import Thread

gas_price = 7 # ОТРЕДАЧЬ GAZ PRICE ЕСЛИ ХОЧЕШЬ

# SETTINGS
file_accounts = 'files/accounts.txt'
file_abi = 'files/abi.txt'
file_config = 'config.txt'
web3_http_provider = 'https://bsc-dataseed.binance.org/'
contract_address = '0x2AB0e9e4eE70FFf1fB9D67031E44F6410170d00e'


# LOGGING SETTING
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")

def parse_accounts(file):
    with open(file, 'r') as file:
        accounts = [row.strip().split(':') for row in file]
    return accounts

def claim_mint_reward_and_share(account, contract, main_account):
    address = web3.toChecksumAddress(account[0])
    private_key = account[1]

    try:

        transaction = contract.functions.claimMintRewardAndShare(
            main_account, 100).buildTransaction({
            'chainId': 56,
            'gas': 180000,
            'gasPrice': web3.toWei(gas_price, 'gwei'),
            'nonce': web3.eth.getTransactionCount(Web3.toChecksumAddress(web3.toChecksumAddress(address.lower()))),
        })

        signed_txn = web3.eth.account.signTransaction(transaction, private_key=private_key)

        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        logger.info(f'TX id: {web3.toHex(tx_hash)}')
        tx_status = web3.eth.waitForTransactionReceipt(tx_hash).status
        if tx_status == 1:
            logger.success(f'TX status: {tx_status}')
        else:
            logger.error(f'TX status: {tx_status}')

    except Exception as error:
        logger.error(f'{address} - {str(error)}')

if (__name__ == '__main__'):
    accounts = parse_accounts(file_accounts)
    web3 = Web3(Web3.HTTPProvider(web3_http_provider))
    with open(file_abi, 'r') as file:
        abi = file.read().replace('\n', '')
    with open(file_config, 'r') as file:
        main_account = web3.toChecksumAddress(file.read().replace('\n', ''))
    contract = web3.eth.contract(address=web3.toChecksumAddress(contract_address), abi=abi)
    for account in accounts:
        Thread(target=claim_mint_reward_and_share, args=(account, contract, main_account)).start()
