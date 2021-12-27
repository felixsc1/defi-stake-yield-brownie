// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract DappToken is ERC20, Ownable {
    constructor() ERC20("Dapp Token", "DAPP") {}

    function mint() public onlyOwner {
        _mint(msg.sender, 1000000000000000000000000);
    }
}
