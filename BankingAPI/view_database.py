import sqlite3

#connect to the sqlite database file
conn=sqlite3.connect('banking.db')

#cursor to execute sqlcommands
cursor=conn.cursor()

#display allaccounts
print('Accounts Table:')
cursor.execute('SELECT * FROM account')
accounts=cursor.fetchall()
print(accounts)
if accounts:
    for account in accounts:
        print(f'ID: {account[0]}, Name: {account[1]}, Email: {account[2]}, Balance: {account[3]}')
else:
    print('No accounts found')
print('\nTransactions Table: ')

#display all transactiond
cursor.execute('SELECT * FROM transaction')
transactions= cursor.fetchall()
if transactions:
    for transaction in transactions:
        print(f'ID: {transaction[0]}, Account ID: {transaction[1]}, Amount: {transaction[2]}, Type: {transaction[3]}')
else:
    print('No transactions found')

#close the connection
conn.close()            