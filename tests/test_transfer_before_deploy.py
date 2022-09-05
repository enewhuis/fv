from brownie import web3, reverts


def test_transfer_before_deploy(accounts, factory, token, FreedomWallet):
    sender = accounts[0]
    owner = accounts.add()
    receiver = accounts[1]
    operator = accounts[2]

    # Sender has some tokens
    token.mint(sender, 100e18)

    # Determine the FreedomWallet address from the owner address and the owner's instance id (salt)
    walletAddress = factory.getAddress(owner, 0)

    # Transfer tokens to the FreedomWallet address 
    token.transfer(walletAddress, 100e18, {'from': sender})

    # Deploy the FreedomWallet for the owner; the address should match.
    tx_deploy = factory.deploy(owner, 0)
    wallet = FreedomWallet.at(tx_deploy.return_value)
    assert wallet.address == walletAddress

    # Owner sign a transaction that transfers 50 tokens to receiver
    tx = dict(destination = token.address,
              value = 0,
              data = token.transfer.encode_input(receiver, 50e18),
              nonce = wallet.nonce(),
              executor = operator.address,
              gasLimit = 1000000)

    # FreedomWallet owner signs the transaction for the operator to execute.
    signed = sign(wallet, owner, tx)

    # Operator broadcast signed transaction paying for gas on behalf of owner
    wallet.execute(
        signed.v, signed.r, signed.s,
        tx['destination'],
        tx['value'],
        tx['data'],
        tx['executor'],
        tx['gasLimit'],
        {'from': operator, 'gasLimit': tx['gasLimit']})

    # Did the tokens arrive?
    assert token.balanceOf(receiver) == 50e18

    # Owner should still have 50 remaining in the FreedomWallet.
    assert token.balanceOf(wallet.address) == 50e18


def test_wallets_have_different_addresses(accounts, factory, token, FreedomWallet):
    owner = accounts.add()
    thief = accounts.add()

    assert thief.address != owner.address

    # Determine the FreedomWallet address from the owner address and the owner's instance id (salt)
    walletAddress = factory.getAddress(owner, 0)

    # Deploy the FreedomWallet for the owner; the address should match.
    tx_deploy = factory.deploy(owner.address, 0)
    wallet = FreedomWallet.at(tx_deploy.return_value)
    assert wallet.address == walletAddress

    # Deploy the FreedomWallet for the owner; the address should match.
    tx_deploy_2 = factory.deploy(thief.address, 0)
    wallet_2 = FreedomWallet.at(tx_deploy_2.return_value)
    assert wallet_2.address != wallet.address


def test_signer_matters(accounts, factory, token, FreedomWallet):
    sender = accounts[0]
    owner = accounts.add()
    thief = accounts.add()
    receiver = accounts[1]
    operator = accounts[2]

    # Sender has some tokens
    token.mint(sender, 100e18)

    # Determine the FreedomWallet address from the owner address and the owner's instance id (salt)
    walletAddress = factory.getAddress(owner, 0)

    # Transfer tokens to the FreedomWallet address 
    token.transfer(walletAddress, 100e18, {'from': sender})

    # Deploy the FreedomWallet for the owner; the address should match.
    tx_deploy = factory.deploy(owner, 0)
    wallet = FreedomWallet.at(tx_deploy.return_value)
    assert wallet.address == walletAddress

    # Owner sign a transaction that transfers 50 tokens to receiver
    tx = dict(destination = token.address,
              value = 0,
              data = token.transfer.encode_input(receiver, 50e18),
              nonce = wallet.nonce(),
              executor = operator.address,
              gasLimit = 1000000)

    # FreedomWallet thief signs the transaction for the operator to execute.
    signed = sign(wallet, thief, tx)

    # Operator broadcasting transaction signed by wrong account should fail.
    with reverts():
        wallet.execute(
            signed.v, signed.r, signed.s,
            tx['destination'],
            tx['value'],
            tx['data'],
            tx['executor'],
            tx['gasLimit'],
            {'from': operator, 'gasLimit': tx['gasLimit']})

  
def sign(wallet, signer, tx):
    txInput = web3.eth.codec.encode_abi(
        ['bytes32', 'address', 'uint256', 'bytes32', 'uint256', 'address', 'uint256'],
        [
            wallet.TXTYPE_HASH(),
            tx['destination'],
            tx['value'],
            web3.keccak(hexstr=tx['data']),
            tx['nonce'],
            tx['executor'],
            tx['gasLimit']
        ]).hex()
    txInputHash = web3.keccak(hexstr=txInput).hex()
    txInputHashEIP712 = '0x19' + '01' + wallet.EIP712_DOMAIN_SEPARATOR().hex() + txInputHash[2:]
    txHashEIP712 = web3.keccak(hexstr=txInputHashEIP712).hex()
    return web3.eth.account.signHash(txHashEIP712, signer.private_key)
