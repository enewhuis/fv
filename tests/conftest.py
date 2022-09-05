
import pytest

@pytest.fixture(scope="module")
def factory(accounts, FreedomFactory):
    return FreedomFactory.deploy({"from": accounts[0]})

@pytest.fixture(scope="module")
def token(accounts, MockERC20):
    return MockERC20.deploy("Mock Token", "MOCK", {"from": accounts[0]})
