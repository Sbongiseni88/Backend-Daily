from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from sqlalchemy.exc import SQLAlchemyError


# Create a Flask app
app = Flask(__name__)

# Configure SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking.db'  # SQLite file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy database
db = SQLAlchemy(app)

# Define the Account model
class Account(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)

# Define the Transaction model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(Enum('withdraw', 'deposit', name='transaction'), nullable=False)
    account = db.relationship('Account', backref='transactions')

# Define a route for the homepage
@app.route('/')
def home():
    return 'Welcome to the Banking API System.'

# Route to create the database
@app.route('/create-db')
def create_db():
    try:
        with app.app_context():
            db.create_all()
            return 'Database created successfully'
    except Exception as e:
            return f'Failed to create database: {e}'

# Route to add sample data for testing
@app.route('/add-sample-data')
def add_sample_data():
    try:
        existing_account = Account.query.filter_by(email='sibongiseni@gmail.com').first()
        if existing_account:
            db.session.delete(existing_account)
            db.session.commit()

        account = Account(name='Sibongiseni', email='sibongiseni@gmail.com', balance=1000.00)
        db.session.add(account)
        db.session.commit()
        return 'Sample account added successfully'
    
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"


# Route to view all accounts
@app.route('/accounts', methods=['GET'])
def view_accounts():
    try:
        accounts = Account.query.all()
        account_list = []
        for account in accounts:
            account_list.append({
                'id': account.id,
                'name': account.name,
                'email': account.email,
                'balance': account.balance
            })
        return {'accounts': account_list}
    
    except Exception as e:
        return {'error': f'An error occurred while fetching accounts: {str(e)}'}, 500

# Route to create a new account
@app.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    if not data:
        return {'error': 'No data provided in the request body'}, 400
    
    name = data.get('name')
    email = data.get('email')
    balance = data.get('balance', 0.0)

    if not name or not email:
        return {'error': 'name and email must be provided'}, 400

    if Account.query.filter_by(email=email).first():
        return {'message': 'Account already exists'}, 400

    try :
        new_account = Account(name=name, email=email, balance=balance)
        db.session.add(new_account)
        db.session.commit()
        return {'message': 'Account created successfully', 'account_id': new_account.id}, 201
    
    except Exception as e:
        db.session.rollback()
        return {'error': 'An error occurred while creating the account', 'details': str(e)}, 500


# Route to get account by ID
@app.route('/accounts/<int:id>', methods=['GET'])
def get_account(id):
    account = Account.query.get(id)
    if not account:
        return {'error': 'Account not found'}, 404

    return {
        'id': account.id,
        'name': account.name,
        'email': account.email,
        'balance': account.balance
    }

# Route to update an existing account by ID
@app.route('/accounts/<int:id>', methods=['PUT'])
def update_account(id):
    data = request.get_json()
    account = Account.query.get(id)

    if not account:
        return {'error': 'Account not found'}, 404

    name = data.get('name')
    email = data.get('email')
    balance = data.get('balance')

    if name:
        account.name = name
    if email:
        account.email = email
    if balance is not None:
        account.balance = balance

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return {'error': 'Database error: ' + str(e)}, 500

    return {'message': 'Account updated successfully'}, 200

# Route to delete an account by ID
@app.route('/accounts/<int:id>', methods=['DELETE'])
def delete_account(id):
    try:
        account = Account.query.get(id)
        if not account:
            return {'error': 'Account not found'}, 404

        db.session.delete(account)
        db.session.commit()
        return {'message': 'Account deleted successfully'}
    
    except Exception as e:
        db.session.rollback()
        return {'error': f'An error occurred: {str(e)}'}, 500

# Route for deposit transaction
@app.route('/transactions/deposit', methods=['POST'])
def deposit():
    data = request.get_json()
    account_id = data.get('account_id')
    amount = data.get('amount')

    if not account_id or not amount:
        return {'error': 'Account ID and amount are required'}, 400

    account = Account.query.get(account_id)
    if not account:
        return {'error': 'Account not found'}, 404

    if amount <= 0:
        return {'error': 'Amount must be greater than 0'}, 400

    account.balance += amount
    transaction = Transaction(account_id=account.id, amount=amount, type='deposit')

    try:
        db.session.add(transaction)
        db.session.commit()

    except Exception as e:
        return {'error': f'An error occurred while processing the deposit: {str(e)}'}, 500

    return {'message': 'Deposit successful', 'new balance': account.balance}

# Route for withdraw transaction
@app.route('/transactions/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json()
    account_id = data.get('account_id')
    amount = data.get('amount')

#check if account_id or amount is not empty
    if not account_id or not amount:
        return {'error': 'Account ID and amount are required'}, 400

    account = Account.query.get(account_id)
    if not account:
        return {'error': 'Account not found'}, 404

    if amount <= 0:
        return {'error': 'Amount must be greater than zero'}, 400

    if amount > account.balance:
        return {'error': 'Insufficient balance'}, 400

    account.balance -= amount
    transaction = Transaction(account_id=account.id, amount=amount, type='withdraw')

    try:
        db.session.add(transaction)
        db.session.commit()
    except Exception as e:
        db.session.rollback() 
        return {'error': f'An error occurred while processing the deposit: {str(e)}'}, 500


    return {'message': 'Withdrawal successful', 'new balance': account.balance}

if __name__ == '__main__':
    app.run(debug=True)

