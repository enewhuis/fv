// SPDX-License-Identifier: MIT
pragma solidity ^0.8.16;

contract FreedomWallet {

  // EIP712 Precomputed hashes:
  // keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)")
  bytes32 public constant EIP712_DOMAINTYPE_HASH = 0xd87cd6ef79d4e2b95e15ce8abf732db51ec771f1ca2edccf22a46c729ac56472;

  // keccak256("FreedomWallet")
  bytes32 public constant NAME_HASH = 0xc928069db9738122d42f41bf3d58cdeee8e5fdb61e64ec8b1d15ba776cb0d080;

  // keccak256("1")
  bytes32 public constant VERSION_HASH = 0xc89efdaa54c0f20c7adf612882df0950f5a951637e0307cdcb4c672f298b8bc6;

  // keccak256("SignedTransaction(address destination,uint256 value,bytes data,uint256 nonce,address executor,uint256 gasLimit)")
  bytes32 public constant TXTYPE_HASH = 0xb2743a4bb0cb3cc82bc7804a803be38fdb3587e5fd092ef3d1ee3ea65bd5875f;

  bytes32 public constant SALT = 0x9de06115391ae9892df837de56cee2a6e966cf778042d209176c84a9d6e0188f;

  bytes32 public immutable EIP712_DOMAIN_SEPARATOR;
  
  address public immutable owner;
  uint256 public nonce;

  // For a given owner address and salt, the deployed contract must have the same address
  // regardless of which chain it is deployed on.  This is desireable to enable recovery
  // of tokens accidentally transferred on the wrong chain.  Therefore the only argument
  // allowed in the constructor is the owner address.  The deployment/instance salt,
  // not to be confused with the EIP712 salt used here, is used by the EVM from Solidity's
  // implementation of CREATE2 via the new FreedomWallet{salt:theSalt}(owner) syntax.
  constructor(address owner_)
  {
    require(owner_ != address(0));
    owner = owner_;
    EIP712_DOMAIN_SEPARATOR = keccak256(abi.encode(EIP712_DOMAINTYPE_HASH,
                                                   NAME_HASH,
                                                   VERSION_HASH,
                                                   block.chainid,
                                                   this,
                                                   SALT));
  }

  function execute(uint8 sigV, bytes32 sigR, bytes32 sigS, address destination, uint256 value, bytes memory data, address executor, uint gasLimit)
    public
  {
    require(executor == msg.sender || executor == address(0));

    // EIP712 scheme: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-712.md
    bytes32 txInputHash = keccak256(abi.encode(TXTYPE_HASH, destination, value, keccak256(data), nonce, executor, gasLimit));
    bytes32 totalHash = keccak256(abi.encodePacked("\x19\x01", EIP712_DOMAIN_SEPARATOR, txInputHash));

    address recovered = ecrecover(totalHash, sigV, sigR, sigS);
    require(recovered == owner);

    ++nonce;
    bool success = false;
    assembly { success := call(gasLimit, destination, value, add(data, 0x20), mload(data), 0, 0) }
    require(success);
  }

  function transfer(address token, address destination, uint256 amount)
    public
  {
    
  }
}
