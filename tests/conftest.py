from brownie import web3
import pytest

# EIP712 Precomputed hashes:
# keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)")
EIP712_DOMAINTYPE_HASH = '0xd87cd6ef79d4e2b95e15ce8abf732db51ec771f1ca2edccf22a46c729ac56472'

# keccak256("FreedomWallet")
NAME_HASH = '0xc928069db9738122d42f41bf3d58cdeee8e5fdb61e64ec8b1d15ba776cb0d080'

# keccak256("1")
VERSION_HASH = '0xc89efdaa54c0f20c7adf612882df0950f5a951637e0307cdcb4c672f298b8bc6'

# keccak256("SignedTransaction(address destination,uint256 value,bytes data,uint256 nonce,address executor,uint256 gasLimit)")
TXTYPE_HASH = '0xb2743a4bb0cb3cc82bc7804a803be38fdb3587e5fd092ef3d1ee3ea65bd5875f'

SALT = '0x9de06115391ae9892df837de56cee2a6e966cf778042d209176c84a9d6e0188f'

@pytest.fixture(scope="module")
def factory(accounts, FreedomFactory):
    return FreedomFactory.deploy({"from": accounts[0]})

@pytest.fixture(scope="module")
def agent(accounts, factory, FreedomAgent):
    return FreedomAgent.deploy(factory, {"from": accounts[0]})

@pytest.fixture(scope="module")
def token(accounts, MockERC20):
    return MockERC20.deploy("Mock Token", "MOCK", {"from": accounts[0]})

def sign(wallet, signer, tx):
    txInput = web3.eth.codec.encode_abi(
        ['bytes32', 'address', 'uint256', 'bytes32', 'uint256', 'address', 'uint256'],
        [
            TXTYPE_HASH,
            tx['destination'],
            tx['value'],
            web3.keccak(hexstr=tx['data']),
            tx['nonce'],
            tx['executor'],
            tx['gasLimit']
        ]).hex()
    txInputHash = web3.keccak(hexstr=txInput).hex()
    txDomainSeparator = wallet.EIP712_DOMAIN_SEPARATOR().hex()
    txInputHashEIP712 = '0x19' + '01' + txDomainSeparator + txInputHash[2:]
    txHashEIP712 = web3.keccak(hexstr=txInputHashEIP712).hex()
    return web3.eth.account.signHash(txHashEIP712, signer.private_key)

def sign2(factory, owner, instance, chainId, tx):
    txInput = web3.eth.codec.encode_abi(
        ['bytes32', 'address', 'uint256', 'bytes32', 'uint256', 'address', 'uint256'],
        [
            TXTYPE_HASH,
            tx['destination'],
            tx['value'],
            web3.keccak(hexstr=tx['data']),
            tx['nonce'],
            tx['executor'],
            tx['gasLimit']
        ]).hex()
    txInputHash = web3.keccak(hexstr=txInput).hex()
    txDomainSeparator = computeEIP712DomainSeparator(factory, owner, instance, chainId).hex()[2:]
    txInputHashEIP712 = '0x19' + '01' + txDomainSeparator + txInputHash[2:]
    txHashEIP712 = web3.keccak(hexstr=txInputHashEIP712).hex()
    return web3.eth.account.signHash(txHashEIP712, owner.private_key)

def computeEIP712DomainSeparator(factory, owner, instance, chainId):
    return web3.keccak(hexstr=web3.eth.codec.encode_abi([
        'bytes32',
        'bytes32',
        'bytes32',
        'uint256',
        'address',
        'bytes32'
    ], [
        EIP712_DOMAINTYPE_HASH,
        NAME_HASH,
        VERSION_HASH,
        chainId,
        factory.getAddress(owner, instance),
        SALT
    ]).hex())
