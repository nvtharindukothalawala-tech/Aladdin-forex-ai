from account import TradingAccount
from account_manager import AccountManager

main_account = TradingAccount("Main Account", 5000, 2)
demo_account = TradingAccount("Demo Account", 10000, 1)
funded_account = TradingAccount("Funded Account", 25000, 0.5)

manager = AccountManager()

manager.add_account(main_account)
manager.add_account(demo_account)
manager.add_account(funded_account)

manager.add_account(demo_account)

manager.remove_account("Demo Account")

manager.update_balance("Main Account", 6500)

manager.show_all_accounts()

search_name = input("Enter account name: ")

found_account = manager.find_account(search_name)

if found_account:
    print("Account found:")
    found_account.show_details()
else:
    print("Account not found.")