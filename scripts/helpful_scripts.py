from brownie import (network, config, accounts, Contract,
                     MockDAI, MockWETH, MockV3Aggregator)
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ['mainnet-fork', 'mainnet-fork-dev']
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development', 'local-ganache']


# here we simply use the same price feed for everything. could parameterize this further.
contract_to_mock = {"eth_usd_price_feed": MockV3Aggregator,
                    "dai_usd_price_feed": MockV3Aggregator,
                    "fau_token": MockDAI,
                    "weth_token": MockWETH}


def get_account(index=None, id=None):
    # accounts[index]
    # accounts.add('id') --> accounts.load('id')
    if index:
        account = accounts[index]
    if id:
        return accounts.load[id]
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
            or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    else:
        return accounts.add(config['wallets']['from_key'])


def get_contract(contract_name):
    """
    This function will grab the contract addresses from the brownie config, if defined,
    otherwise it will deploy a mock version of that contract and return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed version of this contract.
            e.g. MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config['networks'][network.show_active(
        )][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi)
        # all these contracts have attributes, e.g.  MockV3Aggregator._name,  MockV3Aggregator.abi
    return contract


def deploy_mocks(decimals=18, initial_value=2000):
    """
    Use this function if you want to deploy mocks to a local developer chain.
    """
    print("Deploying mocks...")
    account = get_account()
    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account})
    print(f"Deployed to {mock_price_feed.address}")
    print("Deploying Mock DAI/WETH...")
    dai_token = MockDAI.deploy({"from": account})
    weth_token = MockWETH.deploy({"from": account})
    print('Deployed!')
