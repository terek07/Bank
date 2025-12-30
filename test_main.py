import pytest

from main import (
    Bank,
    CheckingAccount,
    SavingsAccount,
    ACCOUNT_CHECKING,
    ACCOUNT_SAVINGS,
    TX_DEPOSIT,
    TX_WITHDRAW,
    TX_TRANSFER,
    InvalidAmountError,
    InsufficientFundsError,
    WithdrawalLimitError,
    AccountNotFoundError,
    CompoundInterestCalculator,
)

# =========================================================
# Fixtures: Bank
# =========================================================

@pytest.fixture
def bank():
    return Bank()


# =========================================================
# Fixtures: CheckingAccount variants
# =========================================================

@pytest.fixture
def checking_for_overdraft(bank):
    """
    High withdrawal limit so overdraft is the ONLY constraint.
    """
    acc = bank.create_account(
        ACCOUNT_CHECKING,
        "Alice",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )
    acc.deposit(300)
    return acc


@pytest.fixture
def checking_for_withdraw_limit(bank):
    """
    Low withdrawal limit so withdrawal limit is the ONLY constraint.
    """
    acc = bank.create_account(
        ACCOUNT_CHECKING,
        "Bob",
        withdrawal_limit=100,
        overdraft_limit=-10_000,
    )
    acc.deposit(1_000)
    return acc


@pytest.fixture
def checking_empty(bank):
    """
    No funds, no overdraft.
    """
    return bank.create_account(
        ACCOUNT_CHECKING,
        "Carol",
        withdrawal_limit=10_000,
        overdraft_limit=0,
    )


# =========================================================
# Fixtures: SavingsAccount variants
# =========================================================

@pytest.fixture
def savings_for_balance(bank):
    """
    High withdrawal limit so balance is the ONLY constraint.
    """
    acc = bank.create_account(
        ACCOUNT_SAVINGS,
        "Dave",
        capitalization_periods_per_year=30,
        annual_interest_rate=0.05,
        withdrawal_limit=10_000,
    )
    acc.deposit(500)
    return acc


@pytest.fixture
def savings_for_withdraw_limit(bank):
    """
    Low withdrawal limit so withdrawal limit is the ONLY constraint.
    """
    acc = bank.create_account(
        ACCOUNT_SAVINGS,
        "Eve",
        capitalization_periods_per_year=30,
        annual_interest_rate=0.05,
        withdrawal_limit=300,
    )
    acc.deposit(1_000)
    return acc


# =========================================================
# Deposit tests
# =========================================================

@pytest.mark.parametrize("amount", [0, -1, -100])
def test_deposit_invalid_amount(amount, checking_for_overdraft):
    with pytest.raises(InvalidAmountError):
        checking_for_overdraft.deposit(amount)


def test_deposit_large_amount(checking_for_overdraft):
    checking_for_overdraft.deposit(1_000_000)
    assert checking_for_overdraft.balance == 1_000_300


# =========================================================
# SavingsAccount: balance-only tests (NO limit conflicts)
# =========================================================

def test_savings_withdraw_exact_balance(savings_for_balance):
    savings_for_balance.withdraw(500)
    assert savings_for_balance.balance == 0


def test_savings_withdraw_exceeds_balance(savings_for_balance):
    with pytest.raises(InsufficientFundsError):
        savings_for_balance.withdraw(501)


# =========================================================
# SavingsAccount: withdrawal-limit-only tests
# =========================================================

def test_savings_withdraw_exact_limit(savings_for_withdraw_limit):
    savings_for_withdraw_limit.withdraw(300)
    assert savings_for_withdraw_limit.balance == 700


def test_savings_withdraw_exceeds_limit(savings_for_withdraw_limit):
    with pytest.raises(WithdrawalLimitError):
        savings_for_withdraw_limit.withdraw(301)


@pytest.mark.parametrize("amount", [0, -10])
def test_savings_withdraw_invalid_amount(amount, savings_for_withdraw_limit):
    with pytest.raises(InvalidAmountError):
        savings_for_withdraw_limit.withdraw(amount)


# =========================================================
# CheckingAccount: overdraft-only tests
# =========================================================

def test_checking_withdraw_to_exact_overdraft_limit(checking_for_overdraft):
    checking_for_overdraft.withdraw(400)
    assert checking_for_overdraft.balance == -100


def test_checking_withdraw_beyond_overdraft_limit(checking_for_overdraft):
    with pytest.raises(InsufficientFundsError):
        checking_for_overdraft.withdraw(401)


# =========================================================
# CheckingAccount: withdrawal-limit-only tests
# =========================================================

def test_checking_withdraw_exact_withdrawal_limit(checking_for_withdraw_limit):
    checking_for_withdraw_limit.withdraw(100)
    assert checking_for_withdraw_limit.balance == 900


def test_checking_withdraw_exceeds_withdrawal_limit(checking_for_withdraw_limit):
    with pytest.raises(WithdrawalLimitError):
        checking_for_withdraw_limit.withdraw(101)


@pytest.mark.parametrize("amount", [0, -5])
def test_checking_withdraw_invalid_amount(amount, checking_for_overdraft):
    with pytest.raises(InvalidAmountError):
        checking_for_overdraft.withdraw(amount)


# =========================================================
# Bank: deposit
# =========================================================

def test_bank_deposit_creates_transaction(bank, checking_empty):
    bank.deposit(checking_empty.account_id, 200)

    assert checking_empty.balance == 200
    assert bank.transactions[-1].tx_type == TX_DEPOSIT


def test_bank_deposit_invalid_account(bank):
    with pytest.raises(AccountNotFoundError):
        bank.deposit(999, 100)


# =========================================================
# Bank: withdraw
# =========================================================

def test_bank_withdraw_creates_transaction(bank, checking_for_overdraft):
    bank.withdraw(checking_for_overdraft.account_id, 100)

    assert checking_for_overdraft.balance == 200
    assert bank.transactions[-1].tx_type == TX_WITHDRAW


def test_bank_withdraw_no_transaction_on_failure(bank, checking_empty):
    tx_count = len(bank.transactions)

    with pytest.raises(InsufficientFundsError):
        bank.withdraw(checking_empty.account_id, 50)

    assert len(bank.transactions) == tx_count


# =========================================================
# Bank: transfer
# =========================================================

def test_transfer_success(bank, checking_for_overdraft):
    target = bank.create_account(
        ACCOUNT_CHECKING,
        "Target",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )

    bank.transfer(checking_for_overdraft.account_id, target.account_id, 200)

    assert checking_for_overdraft.balance == 100
    assert target.balance == 200
    assert bank.transactions[-1].tx_type == TX_TRANSFER


def test_transfer_exact_overdraft_limit(bank, checking_for_overdraft):
    target = bank.create_account(
        ACCOUNT_CHECKING,
        "Target",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )

    bank.transfer(checking_for_overdraft.account_id, target.account_id, 400)

    assert checking_for_overdraft.balance == -100
    assert target.balance == 400


def test_transfer_insufficient_funds(bank, checking_for_overdraft):
    target = bank.create_account(
        ACCOUNT_CHECKING,
        "Target",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )

    with pytest.raises(InsufficientFundsError):
        bank.transfer(checking_for_overdraft.account_id, target.account_id, 401)


def test_transfer_same_account(bank, checking_for_overdraft):
    with pytest.raises(ValueError):
        bank.transfer(
            checking_for_overdraft.account_id,
            checking_for_overdraft.account_id,
            50,
        )


@pytest.mark.parametrize("amount", [0, -10])
def test_transfer_invalid_amount(bank, checking_for_overdraft, amount):
    target = bank.create_account(
        ACCOUNT_CHECKING,
        "Target",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )

    with pytest.raises(InvalidAmountError):
        bank.transfer(checking_for_overdraft.account_id, target.account_id, amount)


def test_transfer_invalid_source(bank):
    target = bank.create_account(
        ACCOUNT_CHECKING,
        "Target",
        withdrawal_limit=10_000,
        overdraft_limit=-100,
    )

    with pytest.raises(AccountNotFoundError):
        bank.transfer(999, target.account_id, 50)


def test_transfer_invalid_target(bank, checking_for_overdraft):
    with pytest.raises(AccountNotFoundError):
        bank.transfer(checking_for_overdraft.account_id, 999, 50)


# =========================================================
# General invariants
# =========================================================

def test_account_ids_are_unique(bank):
    acc1 = bank.create_account(
        ACCOUNT_CHECKING, "A", withdrawal_limit=100, overdraft_limit=-50
    )
    acc2 = bank.create_account(
        ACCOUNT_CHECKING, "B", withdrawal_limit=100, overdraft_limit=-50
    )

    assert acc1.account_id != acc2.account_id

# =========================================================
# CompoundInterestCalculator tests
# =========================================================

def test_compound_interest_one_year():
    final = CompoundInterestCalculator.calculate_compound_interest(1000, 365, 1, 5)
    assert final == pytest.approx(1050.0, rel=1e-9)

def test_compound_interest_fractional_periods():
    starting = 2000
    days = 182  # ~0.5 year
    periods_per_year = 12
    rate = 6  # percent
    final = CompoundInterestCalculator.calculate_compound_interest(starting, days, periods_per_year, rate)
    expected_periods = (days / 365) * periods_per_year
    rate_per_period = rate / periods_per_year / 100
    expected = starting * (1 + rate_per_period) ** expected_periods
    assert final == pytest.approx(expected, rel=1e-9)

def test_compound_interest_invalid_types_and_values():
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest("1000", 365, 1, 5)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(1000, "365", 1, 5)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(1000, 365, 0, 5)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(1000, 365, 12, -1)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(-100, 365, 12, 5)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(1000, -10, 12, 5)

def test_calculate_savings_account_compound_interest_with_account():
    bank = Bank()
    acc = bank.create_account(
        ACCOUNT_SAVINGS,
        "Tester",
        capitalization_periods_per_year=12,
        annual_interest_rate=6,
        withdrawal_limit=1000,
    )
    acc.deposit(1000)
    final = CompoundInterestCalculator.calculate_savings_account_compound_interest(acc, 365)
    expected = 1000 * (1 + 0.06 / 12) ** 12
    assert final == pytest.approx(expected, rel=1e-9)

def test_calculate_savings_account_compound_interest_wrong_account_type():
    bank = Bank()
    acc = bank.create_account(
        ACCOUNT_CHECKING,
        "NotSavings",
        withdrawal_limit=1000,
        overdraft_limit=-100,
    )
    with pytest.raises(TypeError):
        CompoundInterestCalculator.calculate_savings_account_compound_interest(acc, 30)

def test_calculate_savings_account_compound_interest_invalid_days_type():
    bank = Bank()
    acc = bank.create_account(
        ACCOUNT_SAVINGS,
        "Tester2",
        capitalization_periods_per_year=12,
        annual_interest_rate=5,
        withdrawal_limit=1000,
    )
    acc.deposit(500)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_savings_account_compound_interest(acc, "30")

