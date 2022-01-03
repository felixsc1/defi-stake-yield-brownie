from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm, config, network
from web3 import Web3
import yaml
import json
import os
import shutil

KEPT_BALANCE = Web3.toWei(100, 'ether')


def deploy_token_farm_and_dapp_token(front_end_update=False):
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
    if front_end_update:
        update_front_end()
    # we return the contract objects to use this script in the tests
    return token_farm, dapp_token


def update_front_end():
    """
    Requires backend to be in same folder as front-ent.
    In real world would be separate repositories, but then all contracts would be fixed as well and hardcoded in front-end.
    """
    # copying the entire build folder:
    copy_folders_to_front_end("./build", "./front_end/src/chain-info")

    # we send the .yaml file as a json for typescript:
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        # rmtree will deleted everything in destination folder
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


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
    deploy_token_farm_and_dapp_token(front_end_update=True)
