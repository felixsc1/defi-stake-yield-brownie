from brownie import network, config, accounts, LinkToken, VRFCoordinatorMock, Contract
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ['mainnet-fork', 'mainnet-fork-dev']
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development', 'local-ganache']

contract_to_mock = {"vrf_coordinator": VRFCoordinatorMock,
                    "link_token": LinkToken}


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


def deploy_mocks():
    """
    Use this function if you want to deploy mocks to a local developer chain.
    """
    print("Deploying mocks...")
    account = get_account()
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print('Deployed!')


def fund_with_link(contract_address, account=None, link_token=None, amount=Web3.toWei(0.3, "ether")):
    # default amount 0.1Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded contract!")
    return tx
