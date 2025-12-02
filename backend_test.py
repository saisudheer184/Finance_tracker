#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class FinanceTrackerAPITester:
    def __init__(self, base_url="https://expense-wise-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Request failed: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        user_data = {
            "email": test_email,
            "name": "Test User",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            self.test_email = test_email
            return True
        return False

    def test_user_login(self):
        """Test user login"""
        if not hasattr(self, 'test_email'):
            self.log_test("User Login", False, "No test user created")
            return False
            
        login_data = {
            "email": self.test_email,
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            return True
        return False

    def test_get_user_profile(self):
        """Test getting user profile"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_income_transaction(self):
        """Test creating income transaction"""
        transaction_data = {
            "type": "income",
            "amount": 5000.00,
            "category": "Salary",
            "description": "Monthly salary",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        success, response = self.run_test(
            "Create Income Transaction",
            "POST",
            "transactions",
            200,
            data=transaction_data
        )
        
        if success and 'id' in response:
            self.income_transaction_id = response['id']
            return True
        return False

    def test_create_expense_transaction(self):
        """Test creating expense transaction"""
        transaction_data = {
            "type": "expense",
            "amount": 150.50,
            "category": "Food",
            "description": "Grocery shopping",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        success, response = self.run_test(
            "Create Expense Transaction",
            "POST",
            "transactions",
            200,
            data=transaction_data
        )
        
        if success and 'id' in response:
            self.expense_transaction_id = response['id']
            return True
        return False

    def test_get_transactions(self):
        """Test getting all transactions"""
        success, response = self.run_test(
            "Get All Transactions",
            "GET",
            "transactions",
            200
        )
        
        if success and isinstance(response, list):
            self.log_test("Transaction List Format", True)
            return True
        else:
            self.log_test("Transaction List Format", False, "Response is not a list")
            return False

    def test_get_transactions_by_type(self):
        """Test filtering transactions by type"""
        # Test income filter
        success_income, _ = self.run_test(
            "Get Income Transactions",
            "GET",
            "transactions?type=income",
            200
        )
        
        # Test expense filter
        success_expense, _ = self.run_test(
            "Get Expense Transactions",
            "GET",
            "transactions?type=expense",
            200
        )
        
        return success_income and success_expense

    def test_update_transaction(self):
        """Test updating a transaction"""
        if not hasattr(self, 'expense_transaction_id'):
            self.log_test("Update Transaction", False, "No expense transaction to update")
            return False
            
        update_data = {
            "type": "expense",
            "amount": 175.75,
            "category": "Food",
            "description": "Updated grocery shopping",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        success, response = self.run_test(
            "Update Transaction",
            "PUT",
            f"transactions/{self.expense_transaction_id}",
            200,
            data=update_data
        )
        return success

    def test_get_single_transaction(self):
        """Test getting a single transaction"""
        if not hasattr(self, 'income_transaction_id'):
            self.log_test("Get Single Transaction", False, "No transaction ID available")
            return False
            
        success, response = self.run_test(
            "Get Single Transaction",
            "GET",
            f"transactions/{self.income_transaction_id}",
            200
        )
        return success

    def test_create_budget(self):
        """Test creating a budget"""
        current_date = datetime.now()
        budget_data = {
            "month": current_date.month,
            "year": current_date.year,
            "category": "Food",
            "amount": 500.00
        }
        
        success, response = self.run_test(
            "Create Budget",
            "POST",
            "budgets",
            200,
            data=budget_data
        )
        
        if success and 'id' in response:
            self.budget_id = response['id']
            return True
        return False

    def test_get_budgets(self):
        """Test getting budgets"""
        current_date = datetime.now()
        success, response = self.run_test(
            "Get Budgets",
            "GET",
            f"budgets?month={current_date.month}&year={current_date.year}",
            200
        )
        return success

    def test_delete_budget(self):
        """Test deleting a budget"""
        if not hasattr(self, 'budget_id'):
            self.log_test("Delete Budget", False, "No budget ID available")
            return False
            
        success, response = self.run_test(
            "Delete Budget",
            "DELETE",
            f"budgets/{self.budget_id}",
            200
        )
        return success

    def test_get_summary_report(self):
        """Test getting summary report"""
        success, response = self.run_test(
            "Get Summary Report",
            "GET",
            "reports/summary",
            200
        )
        
        if success:
            # Check if response has expected fields
            expected_fields = ['total_income', 'total_expense', 'total_savings', 'category_breakdown']
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                self.log_test("Summary Report Structure", False, f"Missing fields: {missing_fields}")
                return False
            else:
                self.log_test("Summary Report Structure", True)
                return True
        return False

    def test_get_monthly_report(self):
        """Test getting monthly report"""
        success, response = self.run_test(
            "Get Monthly Report",
            "GET",
            "reports/monthly",
            200
        )
        
        if success and isinstance(response, list):
            self.log_test("Monthly Report Format", True)
            return True
        else:
            self.log_test("Monthly Report Format", False, "Response is not a list")
            return False

    def test_delete_transaction(self):
        """Test deleting a transaction"""
        if not hasattr(self, 'expense_transaction_id'):
            self.log_test("Delete Transaction", False, "No transaction ID available")
            return False
            
        success, response = self.run_test(
            "Delete Transaction",
            "DELETE",
            f"transactions/{self.expense_transaction_id}",
            200
        )
        return success

    def test_invalid_auth(self):
        """Test API with invalid authentication"""
        # Save current token
        original_token = self.token
        self.token = "invalid_token"
        
        success, response = self.run_test(
            "Invalid Auth Test",
            "GET",
            "auth/me",
            401
        )
        
        # Restore original token
        self.token = original_token
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Finance Tracker API Tests...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Authentication Tests
        print("\n🔐 Authentication Tests")
        if not self.test_user_registration():
            print("❌ Registration failed, stopping tests")
            return False
            
        self.test_user_login()
        self.test_get_user_profile()
        self.test_invalid_auth()
        
        # Transaction Tests
        print("\n💰 Transaction Tests")
        self.test_create_income_transaction()
        self.test_create_expense_transaction()
        self.test_get_transactions()
        self.test_get_transactions_by_type()
        self.test_get_single_transaction()
        self.test_update_transaction()
        
        # Budget Tests
        print("\n📊 Budget Tests")
        self.test_create_budget()
        self.test_get_budgets()
        
        # Report Tests
        print("\n📈 Report Tests")
        self.test_get_summary_report()
        self.test_get_monthly_report()
        
        # Cleanup Tests
        print("\n🗑️ Cleanup Tests")
        self.test_delete_budget()
        self.test_delete_transaction()
        
        # Print Results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = FinanceTrackerAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": tester.tests_run,
        "passed_tests": tester.tests_passed,
        "success_rate": (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
        "test_details": tester.test_results
    }
    
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())