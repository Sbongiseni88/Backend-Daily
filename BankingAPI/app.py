from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create a Flask app
app = Flask(__name__)

# Configure SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking.db'  # SQLite file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy database
db = SQLAlchemy(app)

# Define the Account model
class Account(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)  # Unique ID for each account
    name = db.Column(db.String(100), nullable=False)  # Name of the account holder
    email = db.Column(db.String(100), unique=True, nullable=False)  # Account holder's email
    balance = db.Column(db.Float, default=0.0)  # Initial account balance

# Define the Transaction model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique transaction identifier
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)  # Links to Account
    amount = db.Column(db.Float, nullable=False)  # Transaction amount
    type = db.Column(db.String(10), nullable=False)  # 'deposit' or 'withdraw'
    account = db.relationship('Account', backref='transactions')  # Access to account details

# Define a route for the homepage
@app.route('/')
def home():
    return 'Welcome to the Banking API System.'

# Route to create the database
@app.route('/create-db')
def create_db():
    with app.app_context():
        try:
            db.create_all()  
            return 'Database created successfully'
        except Exception as e:
            return f'Failed to create database: {e}'

@app.route('/add-sample-data')
def add_sample_data():
    # Check and delete existing account if found
    existing_account = Account.query.filter_by(email='sibongiseni@gmail.com').first()
    if existing_account:
        db.session.delete(existing_account)
        db.session.commit()  

    # Add the new account
    account = Account(name='Sibongiseni', email='sibongiseni@gmail.com', balance=1000.00)
    db.session.add(account)
    db.session.commit()  
    return 'Sample account added successfully'

@app.route('/view-accounts')
def view_accounts():
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



# Start server
if __name__ == '__main__':
    app.run(debug=True)
