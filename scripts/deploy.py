from scripts.helpful_scripts import get_account
from brownie import DappToken


def deploy_token_farm_and_dapp_token():
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})


def main():
    deploy_token_farm_and_dapp_token()
