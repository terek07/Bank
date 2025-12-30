from bank import SavingsAccount


class CompoundInterestCalculator:
    @staticmethod
    def calculate_compound_interest(starting_capital, days, capitalization_periods_per_year, annual_interest_rate):
        # Walidacja wejścia
        if not isinstance(starting_capital, (int, float)):
            raise ValueError("starting_capital must be a number")
        if starting_capital < 0:
            raise ValueError("starting_capital must be non-negative")
        if not isinstance(days, int):
            raise ValueError("days must be an integer")
        if days < 0:
            raise ValueError("days must be non-negative")
        if not isinstance(capitalization_periods_per_year, int):
            raise ValueError("capitalization_periods_per_year must be an integer")
        if capitalization_periods_per_year <= 0:
            raise ValueError("capitalization_periods_per_year must be positive")
        if not isinstance(annual_interest_rate, (int, float)):
            raise ValueError("annual_interest_rate must be a number")
        if annual_interest_rate < 0:
            raise ValueError("annual_interest_rate must be non-negative")

        periods = (days / 365) * capitalization_periods_per_year
        rate_per_period = annual_interest_rate / capitalization_periods_per_year / 100
        final_amount = starting_capital * (1 + rate_per_period) ** periods
        return final_amount

    @staticmethod
    def calculate_savings_account_compound_interest(account: SavingsAccount, days: int) -> float:
        if not isinstance(account, SavingsAccount):
            raise TypeError("Account must be a SavingsAccount")
        return CompoundInterestCalculator.calculate_compound_interest(
            starting_capital=account.balance,
            days=days,
            capitalization_periods_per_year=account.capitalization_periods_per_year,
            annual_interest_rate=account.annual_interest_rate
        )
