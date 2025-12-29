from abc import ABC, abstractmethod
from datetime import datetime


class Account(ABC):
    def __init__(self, id, owner):
        self.id = id
        self.owner = owner
        self._balance = 0

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def __str__(self):
        pass

class SavingsAccount(Account):
    def __init__(self, id, owner, capitalization_period, annual_interest_rate, withdrawal_limit):
        super().__init__(id, owner)
        self.capitalization_period = capitalization_period
        self.annual_interest_rate = annual_interest_rate
        self.withdrawal_limit = withdrawal_limit

    def withdraw(self, amount):
        if amount <= self.balance and amount <= self.withdrawal_limit:
            self._balance -= amount
            return 1
        return 0

    def __str__(self):
        return f"Saving account owned by {self.owner}. Account balance is {self.balance}"

class CheckingAccount(Account):
    def __init__(self, id, owner, withdrawal_limit, overdraft_limit):
        super().__init__(id, owner)
        self.withdrawal_limit = withdrawal_limit
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if self.balance - amount >= self.overdraft_limit and amount <= self.withdrawal_limit:
            self._balance -= amount
            return 1
        return 0

    def __str__(self):
        return f"Checking account owned by {self.owner}. Account balance is {self.balance}"

class Transaction:
    def __init__(self, transaction_type, amount, source_account, target_account=None):
        self.transaction_type = transaction_type
        self.amount = amount
        self.source_account = source_account
        self.target_account = target_account
        self.timestamp = datetime.now()

    def __str__(self):
        target = f" to {self.target_account.owner}" if self.target_account else ""
        return f"Transaction made by {self.source_account.owner}{target}. Transaction type is {self.transaction_type}. Amount is {self.amount}"


class Bank:
    counter = 0
    def __init__(self):
        self.accounts = {}
        self.transactions = []

    def create_account(self,account_type, owner_name, **kwargs):
        account = None
        if account_type == "checking":
            account = CheckingAccount(self.counter, owner_name, kwargs["withdrawal_limit"], kwargs["overdraft_limit"])
        elif account_type == "savings":
            account = SavingsAccount(self.counter, owner_name, kwargs["capitalization_period"], kwargs["annual_interest_rate"], kwargs["withdrawal_limit"])

        if account:
            self.accounts[self.counter] = account
            self.counter += 1
        return account

    def transfer(self, from_id, to_id, amount):
        if self.accounts[from_id].withdraw(amount):
            self.accounts[to_id].deposit(amount)
            self.transactions.append(Transaction("transfer", amount, self.accounts[from_id], self.accounts[to_id]))

    def deposit(self, account_id, amount):
        self.accounts[account_id].deposit(amount)
        self.transactions.append(Transaction("deposit", amount, self.accounts[account_id]))

    def withdraw(self, account_id, amount):
        if self.accounts[account_id].withdraw(amount):
            self.transactions.append(Transaction("withdraw", amount, self.accounts[account_id]))


if __name__ == "__main__":
    bank = Bank()
    print("Welcome in my bank")
    while True:
        print("\nMenu:")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. Show Accounts")
        print("6. Show Transactions")
        print("0. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            acc_type = input("Enter account type (checking/savings): ").strip().lower()
            owner = input("Enter owner name: ")
            if acc_type == "checking":
                wl = int(input("Withdrawal limit: "))
                od = int(input("Overdraft limit: "))
                acc = bank.create_account("checking", owner, withdrawal_limit=wl, overdraft_limit=od)
            elif acc_type == "savings":
                cp = int(input("Capitalization period: "))
                rate = float(input("Annual interest rate: "))
                wl = int(input("Withdrawal limit: "))
                acc = bank.create_account("savings", owner, capitalization_period=cp, annual_interest_rate=rate, withdrawal_limit=wl)
            else:
                print("Invalid account type")
                continue
            if acc:
                print("Created:", acc.__str__())

        elif choice == "2":
            acc_id = int(input("Account ID: "))
            amt = float(input("Amount: "))
            bank.deposit(acc_id, amt)

        elif choice == "3":
            acc_id = int(input("Account ID: "))
            amt = float(input("Amount: "))
            bank.withdraw(acc_id, amt)

        elif choice == "4":
            src = int(input("From Account ID: "))
            dst = int(input("To Account ID: "))
            amt = float(input("Amount: "))
            bank.transfer(src, dst, amt)

        elif choice == "5":
            for acc in bank.accounts.values():
                print(acc)

        elif choice == "6":
            for tx in bank.transactions:
                print(tx)

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice")

