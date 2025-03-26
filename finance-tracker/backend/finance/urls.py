from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterUserView, TransactionViewSet, CategoryViewSet,
    BudgetViewSet, SavingsGoalViewSet, TotalIncomeExpenseReport,
    IncomeExpenseTrendsReport, NetWorthReport, BudgetNotificationView
)


router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename = 'transaction')
router.register(r'categories', CategoryViewSet, basename = 'category')
router.register(r'budgets', BudgetViewSet, basename = 'budget')
router.register(r'savingsgoals', SavingsGoalViewSet, basename = 'savingsgoal')


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name = 'register'),
    path('login/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('reports/income-expenses/', TotalIncomeExpenseReport.as_view(), name='total-income-expenses-report'),
    path('reports/income-expense-trends/', IncomeExpenseTrendsReport.as_view(), name='income-expense-trends-report'),
    path('reports/net-worth/', NetWorthReport.as_view(), name='net-worth-report'),
    path('api/budget-notifications/', BudgetNotificationView.as_view(), name='budget-notifications'),
    path('', include(router.urls))
]