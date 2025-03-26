from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Transaction, Budget, SavingsGoal
from datetime import date, timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

class FinanceAPITestCase(TestCase):
    def setUp(self):
        """Set up test users, categories, and API client."""
        self.client = APIClient()

        # Create user
        self.user = User.objects.create_user(username='testuser', password='testpassword1234')
        self.client.force_authenticate(user=self.user)

        # Create categories
        self.income_category = Category.objects.create(name='Salary', category_type='income', user=self.user)
        self.expense_category = Category.objects.create(name='Groceries', category_type='expense', user=self.user)

        # Create transactions
        self.transaction1 = Transaction.objects.create(
            user=self.user, amount=100.00, category=self.income_category, date=date.today(), description='Paycheck'
        )
        self.transaction2 = Transaction.objects.create(
            user=self.user, amount=50.00, category=self.expense_category, date=date.today(), description='Food'
        )

        # Create budgets
        self.budget = Budget.objects.create(
            user=self.user, category=self.expense_category, allocated_amount=200.00,
            start_date=date.today() - timedelta(days=5), end_date=date.today() + timedelta(days=25)
        )

        # Create savings goal
        self.savings_goal = SavingsGoal.objects.create(
            user=self.user, goal_name="Emergency Fund", target_amount=1000.00, current_amount=200.00,
            deadline=date.today() + timedelta(days=300)
        )

    def test_user_creation(self):
        """Test user registration."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser', 'password': 'newpassword123', 'email': 'newuser@example.com',
            'first_name': 'Test', 'last_name': 'User'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_transaction(self):
        """Test creating a valid transaction."""
        response = self.client.post(reverse('transaction-list'), {
            'category': self.income_category.id, 'amount': 75.00, 'date': date.today(), 'description': 'Bonus',
            'category_type':'income'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_transaction_negative_amount(self):
        """Test transaction cannot have a negative amount."""
        response = self.client.post(reverse('transaction-list'), {
            'category': self.expense_category.id, 'amount': -100.00, 'date': date.today(), 'description': 'Error',
            'category_type':'expense'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_budget_limit_exceeded(self):
        """Test transaction exceeding budget should be handled properly."""
        response = self.client.post(reverse('transaction-list'), {
            'category': self.expense_category.id, 'amount': 250.00, 'date': date.today(), 'description': 'Overspend',
            'category_type':'expense', 'budget': self.budget.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_budget_within_limit(self):
        """Test transaction within budget should pass."""
        response = self.client.post(reverse('transaction-list'), {
            'category': self.expense_category.id, 'amount': 150.00, 'date': date.today(), 'description': 'Groceries',
            'category_type':'expense', 'budget': self.budget.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_budget_filtering(self):
        """Test filtering budgets based on category type."""
        response = self.client.get(reverse('budget-list'), {'category_type': 'expense'})
        self.assertEqual(len(response.data), 1)

    def test_create_savings_goal(self):
        """Test creating a valid savings goal."""
        response = self.client.post(reverse('savingsgoal-list'), {
            'goal_name': 'Vacation Fund', 'target_amount': 2000.00, 'current_amount': 0,
            'deadline': date.today() + timedelta(days=365)
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_savings_goal_negative_amount(self):
        """Test that savings goal cannot have a negative current amount."""
        response = self.client.post(reverse('savingsgoal-list'), {
            'goal_name': 'Invalid Goal', 'target_amount': 2000.00, 'current_amount': -100.00,
            'deadline': date.today() + timedelta(days=365)
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_savings_goal_past_deadline(self):
        """Test that savings goal cannot have a past deadline."""
        response = self.client.post(reverse('savingsgoal-list'), {
            'goal_name': 'Late Goal', 'target_amount': 500.00, 'current_amount': 100.00,
            'deadline': date.today() - timedelta(days=10)
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_savings_goal_progress(self):
        """Test updating the current amount in savings goal."""
        response = self.client.patch(reverse('savingsgoal-detail', kwargs={'pk': self.savings_goal.id}), {
            'current_amount': 500.00
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.savings_goal.refresh_from_db()
        self.assertEqual(self.savings_goal.current_amount, 500.00)

    def test_savings_goal_exceed_target(self):
        """Test that savings goal current amount cannot exceed target."""
        response = self.client.patch(reverse('savingsgoal-detail', kwargs={'pk': self.savings_goal.id}), {
            'current_amount': 1100.00
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access resources."""
        self.client.logout()
        response = self.client.get(reverse('budget-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_transaction_data(self):
        """Test transaction creation with missing required fields."""
        response = self.client.post(reverse('transaction-list'), {
            'category': self.expense_category.id, 'date': date.today()
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_category(self):
        """Test that duplicate category names for the same user are not allowed."""
        response = self.client.post(reverse('category-list'), {
            'name': 'Salary', 'category_type': 'income'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_category_creation_valid(self):
        """Test creating a new valid category."""
        response = self.client.post(reverse('category-list'), {
            'name': 'Investment', 'category_type': 'income'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)