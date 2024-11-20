import unittest
from flask_testing import TestCase  
from app import *

class BankingAPITestCase(TestCase):
    def create_app(self):
        # Set up the Flask app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
        return app

    def setUp(self):
        # Set up the database before each test
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Drop all tables after each test
        with app.app_context():
            db.drop_all()

    def test_create_account(self):
        # Test POST /accounts route (create account)
        response = self.client.post('/accounts', json={
            'name': 'Sibongiseni',
            'email': 'sibongiseni@gmail.com',
            'balance': 1000.00
        })
        self.assertEqual(response.status_code, 201)  
        self.assertIn('Account created successfully', response.get_json()['message'])

    def test_view_all_accounts(self):
        # Test GET /accounts route (view all accounts)
        self.client.post('/accounts', json={
            'name': 'Sibongiseni',
            'email': 'sibongiseni@gmail.com',
            'balance': 1000.00
        })  # Create an account first

        response = self.client.get('/accounts')
        self.assertEqual(response.status_code, 200)  
        self.assertTrue(len(response.get_json()['accounts']) > 0)  

    def test_get_account_by_id(self):
        # Test GET /accounts/<id> route (view account by id)
        response = self.client.post('/accounts', json={
            'name': 'Sibongiseni',
            'email': 'sibongiseni@gmail.com',
            'balance': 1000.00
        })
        account_id = response.get_json()['account_id']

        response = self.client.get(f'/accounts/{account_id}')
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(response.get_json()['id'], account_id)

    def test_update_account(self):
        # Test PUT /accounts/<id> route (update account)
        response = self.client.post('/accounts', json={
            'name': 'Sibongiseni',
            'email': 'sibongiseni@gmail.com',
            'balance': 1000.00
        })
        account_id = response.get_json()['account_id']

        response = self.client.put(f'/accounts/{account_id}', json={
            'name': 'Updated Name',
            'email': 'updatedemail@gmail.com',
            'balance': 2000.00
        })
        self.assertEqual(response.status_code, 200)  
        self.assertIn('Account updated successfully', response.get_json()['message'])

    def test_delete_account(self):
        # Test DELETE /accounts/<id> route (delete account)
        response = self.client.post('/accounts', json={
            'name': 'Sibongiseni',
            'email': 'sibongiseni@gmail.com',
            'balance': 1000.00
        })
        account_id = response.get_json()['account_id']

        response = self.client.delete(f'/accounts/{account_id}')
        self.assertEqual(response.status_code, 200)  #
        self.assertIn('Account deleted successfully', response.get_json()['message'])

if __name__ == '__main__':
    unittest.main()
