from account import TradingAccount
from account_manager import AccountManager


# Create trading account objects
main_account = TradingAccount("Main Account", 5000, 2)
demo_account = TradingAccount("Demo Account", 10000, 1)
funded_account = TradingAccount("Funded Account", 25000, 0.5)


# Create the account manager
manager = AccountManager()


# Add accounts to the manager
manager.add_account(main_account)
manager.add_account(demo_account)
manager.add_account(funded_account)


# Test duplicate account prevention
manager.add_account(demo_account)


# Remove the demo account
manager.remove_account("Demo Account")


# Update the main account balance
manager.update_balance("Main Account", 6500)


# Deposit money and save the transaction
manager.deposit_to_account("Main Account", 1000)


# Withdraw money and save the transaction
manager.withdraw_from_account("Main Account", 500)


# Successful transfer
manager.transfer(
    "Main Account",
    "Funded Account",
    1000
)


# Failed transfer because the balance is not enough
manager.transfer(
    "Main Account",
    "Funded Account",
    100000
)


# Display all transaction records
manager.show_transaction_history()


# Generate the account statement
manager.generate_statement("Main Account")


# Display all remaining accounts
# manager.show_all_accounts()


# Search for an account using user input
search_name = input("Enter account name: ")

found_account = manager.find_account(search_name)

if found_account:
    print("Account found:")
    found_account.show_details()
else:
    print("Account not found.")