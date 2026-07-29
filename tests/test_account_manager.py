from app.models.account import Account
from app.services.account_manager import AccountManager


def test_create_account_manager():
    manager = AccountManager()

    assert manager.accounts == []


def test_add_account():
    manager = AccountManager()

    account = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    manager.add_account(account)

    assert manager.accounts == [account]


def test_find_account_by_id():
    manager = AccountManager()

    account = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    manager.add_account(account)

    found_account = manager.find_account("ACC001")

    assert found_account == account


def test_find_account_returns_none_when_not_found():
    manager = AccountManager()

    result = manager.find_account("ACC999")

    assert result is None


def test_remove_account():
    manager = AccountManager()

    account = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    manager.add_account(account)

    result = manager.remove_account("ACC001")

    assert result is True
    assert manager.accounts == []


def test_remove_account_returns_false_when_not_found():
    manager = AccountManager()

    result = manager.remove_account("ACC999")

    assert result is False


import pytest


def test_cannot_add_duplicate_account_id():
    manager = AccountManager()

    account1 = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    account2 = Account(
        account_id="ACC001",
        balance=5000,
        currency="USD",
        leverage=50,
    )

    manager.add_account(account1)

    with pytest.raises(
        ValueError,
        match="Account ID already exists.",
    ):
        manager.add_account(account2)


def test_account_count_after_duplicate_attempt():
    manager = AccountManager()

    account1 = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    account2 = Account(
        account_id="ACC001",
        balance=5000,
        currency="USD",
        leverage=50,
    )

    manager.add_account(account1)

    with pytest.raises(ValueError):
        manager.add_account(account2)

    assert len(manager.accounts) == 1


def test_get_all_accounts():
    manager = AccountManager()

    account1 = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    account2 = Account(
        account_id="ACC002",
        balance=5000,
        currency="USD",
        leverage=50,
    )

    manager.add_account(account1)
    manager.add_account(account2)

    accounts = manager.get_all_accounts()

    assert accounts == [account1, account2]
