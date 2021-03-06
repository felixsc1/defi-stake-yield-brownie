# Defi Contract  - Tutorial

**TokenFarm.sol** is a Defi contract that allows users to:
- Stake tokens
- Unstake tokens

While the owner can:
- Add allowed tokens (only tokens on the list can then be staked)
- Issue Tokens as rewards for staking

The contract calculates the USD value of all tokens staked by each user (via chainlink),
to compute the amount of reward tokens to be issued (**DappToken.sol**).
The contract keeps track of all balances, so that the owner only has to call *issueTokens()* once, to reward all users.


## Frontend

This is also a first introduction into REACT as front end.
Front end implements components from [useDapp](https://usedapp.readthedocs.io/en/latest/getting-started.html#installation) and uses [MUI](https://mui.com/getting-started/usage/) for styling.