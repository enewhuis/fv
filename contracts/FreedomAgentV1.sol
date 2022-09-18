// SPDX-License-Identifier: MIT
pragma solidity ^0.8.16;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./FreedomFactory.sol";
import "./FreedomWallet.sol";

contract FreedomAgentV1 is AccessControl {
  using SafeERC20 for IERC20; // freaking important

  bytes32 public constant AGENT_ROLE = keccak256("AGENT_ROLE");

  FreedomFactory public immutable factory;
  address public immutable admin;

  constructor(address factory_, address admin_)
  {
    factory = FreedomFactory(factory_);
    admin = admin_;
    
    _setupRole(DEFAULT_ADMIN_ROLE, admin_);
  }

  function transfer(address owner, uint256 salt, address payable to, uint256 netAmount, uint8 sigV, bytes32 sigR, bytes32 sigS, address token, uint256 value, uint256 exists, bytes memory data, uint gasLimit)
    public
    payable
    onlyRole(AGENT_ROLE)
  {
    FreedomWallet wallet;
    if (exists == 0) {
      wallet = FreedomWallet(factory.deploy(owner, salt));
    }
    else {
      wallet = FreedomWallet(factory.getAddress(owner, salt));
    }

    // The token.balanceOf(this) should be 0 before executing the signed function on behalf of the owner
    // but, regardless, the caller is going to collect whatever remains after transferring

    // Check the signature and execute the transfer to this.
    wallet.execute(sigV, sigR, sigS, token, value, data, address(this), gasLimit);

    // netAmount should be less than the value param or transfer(to, amount) calldata encoded in the data param.
    if (token == address(this)) {
      to.transfer(netAmount);
      payable(admin).transfer(address(this).balance);
    }
    else {
      // ERC20?
      //
      // Do not expect perfect conformance to the ERC20 standard.
      // Do not inspect return values.
      // There could be a tax especially if address(this) is not whitelisted.
      //
      IERC20 t = IERC20(token);
      t.safeTransfer(to, netAmount);
      uint256 capturedFee = t.balanceOf(address(this));
      if (capturedFee > 0) {
        t.safeTransfer(admin, capturedFee);
      }
    }
  }

  function receive_it() external payable {}
}
