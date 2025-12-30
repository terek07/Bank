from abc import ABC, abstractmethod
from datetime import datetime

# =====================
# Constants
# =====================

# Account types
ACCOUNT_CHECKING = "checking"
ACCOUNT_SAVINGS = "savings"

# Transaction types
TX_DEPOSIT = "deposit"
TX_WITHDRAW = "withdraw"
TX_TRANSFER = "transfer"

# =====================
# Exceptions
# =====================

class BankError(Exception):
    """Base class for bank-related errors."""
    pass


class InvalidAmountError(BankError):
    pass


class InsufficientFundsError(BankError):
    pass


class WithdrawalLimitError(BankError):
    pass


class AccountNotFoundError(BankError):
    pass


# =====================
# Accounts
# =====================

class Account(ABC):
    def __init__(self, account_id, owner):
        self.account_id = account_id
        self.owner = owner
        self._balance = 0.0

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
        self._balance += amount

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def __str__(self):
        pass


class SavingsAccount(Account):
    def __init__(self, account_id, owner, capitalization_period, annual_interest_rate, withdrawal_limit):
        super().__init__(account_id, owner)
        self.capitalization_periods_per_year = capitalization_period
        self.annual_interest_rate = annual_interest_rate
        self.withdrawal_limit = withdrawal_limit

    def withdraw(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        if amount > self.withdrawal_limit:
            raise WithdrawalLimitError("Withdrawal limit exceeded")
        if amount > self.balance:
            raise InsufficientFundsError("Insufficient funds")

        self._balance -= amount

    def __str__(self):
        return (
            "=== Savings Account ===\n"
            f"ID: {self.account_id}\n"
            f"Owner: {self.owner}\n"
            f"Balance: {self.balance:.2f}\n"
            f"Capitalization periods per year: {self.capitalization_periods_per_year}\n"
            f"Annual interest rate: {self.annual_interest_rate}\n"
            f"Withdrawal limit: {self.withdrawal_limit}"
        )


class CheckingAccount(Account):
    def __init__(self, account_id, owner, withdrawal_limit, overdraft_limit):
        super().__init__(account_id, owner)
        self.withdrawal_limit = withdrawal_limit
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        if amount > self.withdrawal_limit:
            raise WithdrawalLimitError("Withdrawal limit exceeded")
        if self.balance - amount < self.overdraft_limit:
            raise InsufficientFundsError("Overdraft limit exceeded")

        self._balance -= amount

    def __str__(self):
        return (
            "=== Checking Account ===\n"
            f"ID: {self.account_id}\n"
            f"Owner: {self.owner}\n"
            f"Balance: {self.balance:.2f}\n"
            f"Withdrawal limit: {self.withdrawal_limit}\n"
            f"Overdraft limit: {self.overdraft_limit}"
        )


# =====================
# Transaction
# =====================

class Transaction:
    def __init__(self, tx_type, amount, source_account_id, target_account_id=None):
        self.tx_type = tx_type
        self.amount = amount
        self.source_account_id = source_account_id
        self.target_account_id = target_account_id
        self.timestamp = datetime.now()

    def __str__(self):
        target = f" -> {self.target_account_id}" if self.target_account_id is not None else ""
        return (
            f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] "
            f"{self.tx_type.upper()} | {self.amount:.2f} | "
            f"{self.source_account_id}{target}"
        )


# =====================
# Bank Service
# =====================

class Bank:
    def __init__(self):
        self._counter = 0
        self.accounts = {}
        self.transactions = []

    def _get_account(self, account_id):
        if account_id not in self.accounts:
            raise AccountNotFoundError("Account not found")
        return self.accounts[account_id]

    def create_account(self, account_type, owner, **kwargs):
        if account_type == ACCOUNT_CHECKING:
            account = CheckingAccount(
                self._counter,
                owner,
                kwargs["withdrawal_limit"],
                kwargs["overdraft_limit"],
            )
        elif account_type == ACCOUNT_SAVINGS:
            # expect key 'capitalization_period' to match SavingsAccount init
            account = SavingsAccount(
                self._counter,
                owner,
                kwargs["capitalization_periods_per_year"],
                kwargs["annual_interest_rate"],
                kwargs["withdrawal_limit"],
            )
        else:
            raise ValueError("Invalid account type")

        self.accounts[self._counter] = account
        self._counter += 1
        return account

    def deposit(self, account_id, amount):
        account = self._get_account(account_id)
        account.deposit(amount)
        self.transactions.append(
            Transaction(TX_DEPOSIT, amount, account_id)
        )

    def withdraw(self, account_id, amount):
        account = self._get_account(account_id)
        account.withdraw(amount)
        self.transactions.append(
            Transaction(TX_WITHDRAW, amount, account_id)
        )

    def transfer(self, from_id, to_id, amount):
        if from_id == to_id:
            raise ValueError("Cannot transfer to the same account")
        source = self._get_account(from_id)
        target = self._get_account(to_id)

        source.withdraw(amount)
        target.deposit(amount)

        self.transactions.append(
            Transaction(TX_TRANSFER, amount, from_id, to_id)
        )