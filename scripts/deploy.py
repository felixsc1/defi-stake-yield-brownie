from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm, config, network
from web3 import Web3

KEPT_BALANCE = Web3.toWei(100, 'ether')


def deploy_token_farm_and_dapp_token():
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    dapp_token.mint({"from": account})
    token_farm = TokenFarm.deploy(dapp_token.address, {
                                  "from": account}, publish_source=config["networks"][network.show_active()].get("verify"))
    # In order to pay rewards in DappTokens, we need to transfer them all to the TokenFarm contract
    # keep some for test purposes
    tx = dapp_token.transfer(
        token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE, {"from": account})
    tx.wait(1)
    # for now we allow 3 tokens: dapp_token, weth, fau_token (faucet token, we pretend it is dai)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    # we need to provide token address as well as its price feed
    dict_of_allowed_tokens = {dapp_token: get_contract("dai_usd_price_feed"),
                              fau_token: get_contract("dai_usd_price_feed"),
                              weth_token: get_contract("eth_usd_price_feed")}
    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)
    # we return the contract objects to use this script in the tests
    return token_farm, dapp_token


def add_allowed_tokens(token_farm, dict_of_allowed_tokens, account):
    # apparently not possible to add an entire dict? so we run one transaction for each token
    for token in dict_of_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token])
        set_tx.wait(1)
    return token_farm


def main():
    deploy_token_farm_and_dapp_token()
