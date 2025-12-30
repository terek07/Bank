import runpy
import builtins
import pytest


def _run_cli_with_inputs(inputs, monkeypatch, capsys):
    """
    Helper: runs `cli_bank` as a script with a sequence of inputs.
    Returns captured stdout as string.
    """
    it = iter(inputs)

    def _fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            # If input exhausted, return "0" to trigger exit
            return "0"

    monkeypatch.setattr(builtins, "input", _fake_input)
    runpy.run_module("cli_bank", run_name="__main__")
    out = capsys.readouterr().out
    return out


def test_create_checking_and_show_accounts(monkeypatch, capsys):
    inputs = [
        "1",      # Create Account
        "1",      # checking
        "Alice",  # owner
        "1000",   # withdrawal limit
        "-100",   # overdraft limit
        "5",      # Show Accounts
        "0",      # Exit
    ]
    out = _run_cli_with_inputs(inputs, monkeypatch, capsys)
    assert "Created" in out or "Created:" in out
    assert "Checking Account" in out
    assert "Owner: Alice" in out


def test_deposit_and_transfer_flow(monkeypatch, capsys):
    inputs = [
        "1",      # Create Account (0)
        "1",      # checking
        "A",      # owner A
        "10000",  # wl
        "-100",   # od
        "1",      # Create Account (1)
        "1",      # checking
        "B",      # owner B
        "10000",  # wl
        "-100",   # od
        "2",      # Deposit
        "0",      # Account ID
        "500",    # Amount
        "4",      # Transfer
        "0",      # From
        "1",      # To
        "200",    # Amount
        "5",      # Show Accounts
        "0",      # Exit
    ]
    out = _run_cli_with_inputs(inputs, monkeypatch, capsys)
    assert "Deposit successful" in out
    assert "Transfer successful" in out
    assert "Balance: 300.00" in out or "300.0" in out
    assert "Balance: 200.00" in out or "200.0" in out


def test_interest_and_invalid_account_for_interest(monkeypatch, capsys):
    # success path: create savings, deposit, calculate interest
    inputs_success = [
        "1",      # Create Account (0)
        "2",      # savings
        "Tester", # owner
        "12",     # capitalization periods per year
        "6",      # annual interest rate (percent)
        "1000",   # withdrawal limit
        "2",      # Deposit
        "0",      # Account ID
        "1000",   # Amount
        "7",      # Calculate Interest (Savings)
        "0",      # Savings Account ID
        "365",    # Days
        "0",      # Exit
    ]
    out_success = _run_cli_with_inputs(inputs_success, monkeypatch, capsys)
    assert "Final amount after 365 days" in out_success or "Final amount" in out_success
    assert "Interest earned" in out_success

    # failure: calculate interest for non-existent account -> should show "Error:"
    inputs_fail = [
        "7",     # Calculate Interest (Savings)
        "999",   # non-existent account id
        "30",    # Days
        "0",     # Exit
    ]
    out_fail = _run_cli_with_inputs(inputs_fail, monkeypatch, capsys)
    assert "Error:" in out_fail
