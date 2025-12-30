from bank import ACCOUNT_CHECKING, Bank, ACCOUNT_SAVINGS, BankError
from finance_tools import CompoundInterestCalculator

if __name__ == "__main__":
    bank = Bank()
    print("Welcome to my bank")

    while True:
        print("\nMenu:")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. Show Accounts")
        print("6. Show Transactions")
        print("7. Calculate Interest (Savings)")
        print("0. Exit")

        choice = input("Choose option: ").strip()

        try:
            if choice == "1":
                acc_type = input("Account type (1=checking, 2=savings): ").strip()
                owner = input("Owner name: ")

                if acc_type == "1":
                    wl = int(input("Withdrawal limit: "))
                    od = int(input("Overdraft limit: "))
                    acc = bank.create_account(
                        ACCOUNT_CHECKING,
                        owner,
                        withdrawal_limit=wl,
                        overdraft_limit=od,
                    )
                elif acc_type == "2":
                    cp = int(input("Capitalization periods per year: "))
                    rate = float(input("Annual interest rate (percent): "))
                    wl = int(input("Withdrawal limit: "))
                    acc = bank.create_account(
                        ACCOUNT_SAVINGS,
                        owner,
                        capitalization_periods_per_year=cp,
                        annual_interest_rate=rate,
                        withdrawal_limit=wl,
                    )
                else:
                    print("Invalid account type")
                    continue

                print("Created:\n", acc)

            elif choice == "2":
                bank.deposit(int(input("Account ID: ")), float(input("Amount: ")))
                print("Deposit successful")

            elif choice == "3":
                bank.withdraw(int(input("Account ID: ")), float(input("Amount: ")))
                print("Withdrawal successful")

            elif choice == "4":
                bank.transfer(
                    int(input("From Account ID: ")),
                    int(input("To Account ID: ")),
                    float(input("Amount: ")),
                )
                print("Transfer successful")

            elif choice == "5":
                for acc in bank.accounts.values():
                    print(acc)

            elif choice == "6":
                for tx in bank.transactions:
                    print(tx)

            elif choice == "7":
                acc_id = int(input("Savings Account ID: "))
                days = int(input("Days to calculate: "))
                account = bank._get_account(acc_id)
                amount = CompoundInterestCalculator.calculate_savings_account_compound_interest(account, days)
                interest = amount - account.balance
                print(f"Final amount after {days} days: {amount:.2f}")
                print(f"Interest earned: {interest:.2f}")

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid choice")

        except BankError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Invalid input: {e}")
        except TypeError as e:
            print(f"Type error: {e}")