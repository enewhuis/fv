// SPDX-License-Identifier: MIT
pragma solidity ^0.8.16;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./FreedomFactory.sol";
import "./FreedomWallet.sol";

contract FreedomAgent {
  FreedomFactory public immutable factory;

  constructor(address factory_)
  {
    factory = FreedomFactory(factory_);
  }

  function transfer(address owner, uint256 salt, address to, uint256 netAmount, uint8 sigV, bytes32 sigR, bytes32 sigS, address token, uint256 value, uint256 nonce, bytes memory data, uint gasLimit)
    public
  {
    FreedomWallet wallet;
    if (nonce == 0) {
      wallet = FreedomWallet(factory.deploy(owner, salt));
    }
    else {
      wallet = FreedomWallet(factory.getAddress(owner, salt));
    }

    // The token.balanceOf(this) should be 0 before executing the signed function on behalf of the owner
    // but, regardless, the caller is going to collect whatever remains after transferring
  
    // Check the signature and execute the transfer to this.
    wallet.execute(sigV, sigR, sigS, token, value, data, address(this), gasLimit);

    // Transfer netAmount that should be less than transfer(to, amount) encoded in the data parameter.
    require(IERC20(token).transfer(to, netAmount));

    // Sender takes the rest as the fee.
    require(IERC20(token).transfer(msg.sender, IERC20(token).balanceOf(address(this))));
  }

}
