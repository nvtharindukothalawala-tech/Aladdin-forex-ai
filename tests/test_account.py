import pytest

from app.account import Account


def test_create_account():
    account = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    assert account.account_id == "ACC001"
    assert account.balance == 10000
    assert account.currency == "USD"
    assert account.leverage == 100


def test_empty_account_id_is_rejected():
    with pytest.raises(
        ValueError,
        match="Account ID cannot be empty.",
    ):
        Account(
            account_id="",
            balance=10000,
            currency="USD",
            leverage=100,
        )


def test_deposit_money():
    account = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    account.deposit(500)

    assert account.balance == 10500


def test_deposit_rejects_zero_or_negative_amount():
    account = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    with pytest.raises(
        ValueError,
        match="Deposit amount must be greater than zero.",
    ):
        account.deposit(0)


def test_withdraw_money():
    account = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    account.withdraw(1500)

    assert account.balance == 8500


def test_withdraw_rejects_zero_or_negative_amount():
    account = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    with pytest.raises(
        ValueError,
        match="Withdrawal amount must be greater than zero.",
    ):
        account.withdraw(0)


def test_cannot_withdraw_more_than_balance():
    account = Account(
        account_id="ACC001",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    with pytest.raises(
        ValueError,
        match="Insufficient balance.",
    ):
        account.withdraw(15000)
