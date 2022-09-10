from brownie import web3, reverts
from conftest import sign, sign2

def test_transfer_before_deploy(accounts, factory, token, FreedomWallet, chain):
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
    instance = 0
    tx_deploy = factory.deploy(owner, instance)
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
    signed2 = sign2(factory, owner, instance, chain.id, tx)
    assert signed == signed2

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
