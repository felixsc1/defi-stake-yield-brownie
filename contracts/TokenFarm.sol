// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {
    // Things that contract can do:
    // stakeTokens
    // unstakeTokens
    // issueTokens (=rewards for staking)
    // addAllowedTokens  (specify which tokens can be staked)
    // getValue  (of the staked tokens, to calculate reward)

    // e.g. if someone stakes 50 ETH and 50 DAI, need to convert to common unit to give reward of 1DAPPtoken / 1 DAI.

    // create a list of tokens that can be staked, with function to add tokens to the list
    // and function that loops through this list to check.
    address[] public allowedTokens;

    // we need to map three levels:
    // token address -> staker/user address -> amount
    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => uint256) public uniqueTokensStaked;
    address[] public stakers;
    mapping(address => address) public tokenPriceFeedMapping;

    IERC20 public dappToken;

    constructor(address _dappTokenAddress) public {
        dappToken = IERC20(_dappTokenAddress);
    }

    function setPriceFeedContract(address _token, address _priceFeed)
        public
        onlyOwner
    {
        tokenPriceFeedMapping[_token] = _priceFeed;
    }

    function issueTokens() public onlyOwner {
        // issue token rewards to all stakers
        for (
            uint256 stakersIndex = 0;
            stakersIndex < stakers.length;
            stakersIndex++
        ) {
            address recipient = stakers[stakersIndex];
            // now send each their token reward, but first we need to get their total value locked
            uint256 userTotalValue = getUserTotalValue(recipient);
            // here we simply issue 1 dappToken per 1 USD in staked value.
            dappToken.transfer(recipient, userTotalValue);
        }
    }

    function getUserTotalValue(address _user) public view returns (uint256) {
        // Involves lots of looping, expensive calculations, to provide total reward automatically.
        // thats why usually users have to claim rewards for each of their tokens themselves (more gas efficient).
        // note how each sub-step in getting the total value is carried out in smaller functions below.
        uint256 totalValue = 0;
        require(uniqueTokensStaked[_user] > 0, "No tokens staked!");
        for (
            uint256 allowedTokensIndex = 0;
            allowedTokensIndex < allowedTokens.length;
            allowedTokensIndex++
        ) {
            totalValue += getUserSingleTokenValue(
                _user,
                allowedTokens[allowedTokensIndex]
            );
        }
        return totalValue;
    }

    function getUserSingleTokenValue(address _user, address _token)
        public
        view
        returns (uint256)
    {
        if (uniqueTokensStaked[_user] == 0) {
            return 0; // not using require() here, because we want it to return something
        }
        // we want to return the stakingBalance * tokenValue in USD, thus first get the price:
        (uint256 price, uint256 decimals) = getTokenValue(_token);
        return ((stakingBalance[_token][_user] * price) / (10**decimals));
        // Explanation:
        // if we have 10 ETH, price of feed is ETH/USD, e.g = 100
        // numerator: 10 * 100 = 1000
        // ETH has 18 decimals, but price feed has e.g. 8 decimals, after multiplying -> 24 decimals
        // thus in denominator: divide by extra decimals to get units in wei again.
    }

    function getTokenValue(address _token)
        public
        view
        returns (uint256, uint256)
    {
        // using chainlink price feeds, the addresses of which were set above
        address priceFeedAddress = tokenPriceFeedMapping[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAddress
        );
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        return (uint256(price), decimals);
    }

    function stakeTokens(uint256 _amount, address _token) public {
        // how much can they stake?
        // we don't need max amount since in solidity ^0.8 theres no wrap around
        require(_amount > 0, "Amount must be more than 0");
        require(tokenIsAllowed(_token), "This token cannot be staked");
        // TokenFarm contract itself does not own the tokens (yet), thus we need to use transferFrom
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        updateUniqueTokensStaked(msg.sender, _token);
        stakingBalance[_token][msg.sender] += _amount;
        // we only  want to add each staker once to staker array, i.e. if the newly staked token is their first one.
        if (uniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    function unstakeToken(address _token) public {
        // transfers entire balance of given token back to whoever called the function.
        // todo: Is this vulnerable to "reentrancy" attacks?
        uint256 balance = stakingBalance[_token][msg.sender];
        require(balance > 0, "No tokens staked.");
        IERC20(_token).transfer(msg.sender, balance);
        stakingBalance[_token][msg.sender] = 0;
        uniqueTokensStaked[msg.sender] -= 1;
        // todo: msg.sender now has no tokens staked anymore, remove from stakers list.
        // not critical, because issueTokens function will check if there are tokens staked.
    }

    function updateUniqueTokensStaked(address _user, address _token) internal {
        // We only want each user to be added to the stakers array once.
        // When a user calls stakeTokens(), this function is called.
        // increments uniqueTokensStaked mapping only if user adds a new token.
        if (stakingBalance[_token][_user] <= 0) {
            uniqueTokensStaked[_user]++;
        }
    }

    function addAllowedTokens(address _token) public onlyOwner {
        allowedTokens.push(_token);
    }

    function tokenIsAllowed(address _token) public returns (bool) {
        for (
            uint256 allowedTokensIndex = 0;
            allowedTokensIndex < allowedTokens.length;
            allowedTokensIndex++
        ) {
            if (allowedTokens[allowedTokensIndex] == _token) {
                return true;
            }
        }
        return false;
    }
}
