from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, INITIAL_PRICE_FEED_VALUE)
from brownie import network, exceptions
import pytest
from scripts.deploy import deploy_token_farm_and_dapp_token


def test_set_price_feed_contract():
    # Arrange
    # since this stuff is probably done for most unit test, we could put this into "conftest"
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local unit test.")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    price_feed_address = get_contract("dai_usd_price_feed")
    token_farm.setPriceFeedContract(
        dapp_token.address, price_feed_address, {"from": account})
    # Assert
    assert token_farm.tokenPriceFeedMapping(
        dapp_token.address) == price_feed_address
    # Trying to set price feed from non-owner address should give an error:
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            dapp_token.address, price_feed_address, {"from": non_owner})


def test_stake_tokens(amount_staked):
    # amount_staked is a "fixture", see conftest.py how it is declared.
    # could use a global variable here as well, but for learnings sake we use conftest
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local unit test.")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(
        amount_staked, dapp_token.address, {"from": account})
    # Assert
    # "stakingBalance" is a mapping of a mapping, top access amount, we pass two parameters:
    assert token_farm.stakingBalance(
        dapp_token.address, account.address) == amount_staked
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local unit test.")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)
    # Act
    token_farm.issueTokens({"from": account})
    # Arrange
    # We are staking 1ETH worth of dapp_token
    # since our Mock price of 1ETH=2000USD, we expect 2000 dapp tokens as reward
    assert dapp_token.balanceOf(
        account.address) == starting_balance + INITIAL_PRICE_FEED_VALUE


# TODO: Write tests for the remaining functions (solution on github: https://github.com/PatrickAlphaC/defi-stake-yield-brownie-freecode/tree/main/tests)
