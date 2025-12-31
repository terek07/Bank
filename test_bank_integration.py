import pytest

from bank import (
    CheckingAccount,
    SavingsAccount,
    ACCOUNT_CHECKING,
    ACCOUNT_SAVINGS,
    TX_DEPOSIT,
    TX_WITHDRAW,
    TX_TRANSFER,
    InsufficientFundsError,
    WithdrawalLimitError,
)

from finance_tools import CompoundInterestCalculator

from config_test import bank

# =========================================================
# Integration: Bank + Accounts + Transactions
# =========================================================

def test_checking_to_savings_full_flow(bank):
    checking = bank.create_account(
        ACCOUNT_CHECKING,
        "Alice",
        withdrawal_limit=1000,
        overdraft_limit=-200,
    )

    savings = bank.create_account(
        ACCOUNT_SAVINGS,
        "Bob",
        capitalization_periods_per_year=12,
        annual_interest_rate=5,
        withdrawal_limit=500,
    )

    bank.deposit(checking.account_id, 500)
    bank.transfer(checking.account_id, savings.account_id, 200)

    assert checking.balance == 300
    assert savings.balance == 200

    assert [tx.tx_type for tx in bank.transactions] == [
        TX_DEPOSIT,
        TX_TRANSFER,
    ]


# =========================================================
# Overdraft integration
# =========================================================

def test_overdraft_is_applied_during_transfer(bank):

    src = bank.create_account(
        ACCOUNT_CHECKING,
        "Alice",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )

    dst = bank.create_account(
        ACCOUNT_CHECKING,
        "Bob",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )

    bank.deposit(src.account_id, 300)
    bank.transfer(src.account_id, dst.account_id, 400)

    assert src.balance == -100
    assert dst.balance == 400


def test_overdraft_limit_blocks_transfer(bank):

    src = bank.create_account(
        ACCOUNT_CHECKING,
        "Alice",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )

    dst = bank.create_account(
        ACCOUNT_CHECKING,
        "Bob",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )

    bank.deposit(src.account_id, 300)

    with pytest.raises(InsufficientFundsError):
        bank.transfer(src.account_id, dst.account_id, 401)

    assert src.balance == 300
    assert dst.balance == 0
    assert len(bank.transactions) == 1  # deposit only


# =========================================================
# Withdrawal limit integration
# =========================================================

def test_withdrawal_limit_blocks_withdraw_even_with_funds(bank):

    acc = bank.create_account(
        ACCOUNT_CHECKING,
        "Alice",
        withdrawal_limit=100,
        overdraft_limit=-10_000,
    )

    bank.deposit(acc.account_id, 1000)

    with pytest.raises(WithdrawalLimitError):
        bank.withdraw(acc.account_id, 200)

    assert acc.balance == 1000
    assert len(bank.transactions) == 1  # deposit only


# =========================================================
# State invariants
# =========================================================

def test_failed_operations_do_not_create_transactions(bank):

    acc = bank.create_account(
        ACCOUNT_CHECKING,
        "Alice",
        withdrawal_limit=100,
        overdraft_limit=0,
    )

    initial_tx_count = len(bank.transactions)

    with pytest.raises(InsufficientFundsError):
        bank.withdraw(acc.account_id, 50)

    assert acc.balance == 0
    assert len(bank.transactions) == initial_tx_count


def test_account_ids_are_unique(bank):

    acc1 = bank.create_account(
        ACCOUNT_CHECKING,
        "A",
        withdrawal_limit=100,
        overdraft_limit=-50,
    )
    acc2 = bank.create_account(
        ACCOUNT_CHECKING,
        "B",
        withdrawal_limit=100,
        overdraft_limit=-50,
    )

    assert acc1.account_id != acc2.account_id


# =========================================================
# Multiple accounts & transaction ordering
# =========================================================

def test_transaction_order_across_multiple_accounts(bank):

    a = bank.create_account(
        ACCOUNT_CHECKING,
        "A",
        withdrawal_limit=500,
        overdraft_limit=-200,
    )
    b = bank.create_account(
        ACCOUNT_CHECKING,
        "B",
        withdrawal_limit=500,
        overdraft_limit=-200,
    )

    bank.deposit(a.account_id, 300)
    bank.deposit(b.account_id, 200)
    bank.transfer(a.account_id, b.account_id, 100)
    bank.withdraw(b.account_id, 50)

    assert [tx.tx_type for tx in bank.transactions] == [
        TX_DEPOSIT,
        TX_DEPOSIT,
        TX_TRANSFER,
        TX_WITHDRAW,
    ]


# =========================================================
# Integration: Finance tools + SavingsAccount
# =========================================================

def test_savings_account_interest_calculation_integration(bank):

    savings = bank.create_account(
        ACCOUNT_SAVINGS,
        "Bob",
        capitalization_periods_per_year=12,
        annual_interest_rate=6,
        withdrawal_limit=10_000,
    )

    bank.deposit(savings.account_id, 1000)

    interest = CompoundInterestCalculator.calculate_savings_account_compound_interest(
        savings,
        days=365,
    )

    assert interest > 0
    assert interest == pytest.approx(1061.68, rel=1e-2)


def test_zero_interest_rate_results_in_zero_interest(bank):

    savings = bank.create_account(
        ACCOUNT_SAVINGS,
        "Bob",
        capitalization_periods_per_year=12,
        annual_interest_rate=0,
        withdrawal_limit=10_000,
    )

    bank.deposit(savings.account_id, 1000)

    interest = CompoundInterestCalculator.calculate_savings_account_compound_interest(
        savings,
        days=365,
    )

    assert interest == 1000.0
