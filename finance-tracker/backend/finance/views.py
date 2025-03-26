from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncWeek
from rest_framework.views import APIView
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, TransactionSerializer, CategorySerializer, BudgetSerializer, SavingsGoalSerializer
from .models import Transaction, Category, Budget, SavingsGoal
from datetime import datetime
from rest_framework.pagination import PageNumberPagination

# Create your views here.

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status = status.HTTP_201_CREATED)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Category.objects.all()

        category_type = self.request.query_params.get('category_type', None)

        if category_type:
            queryset = queryset.filter(type = category_type)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        # Filtering by category (optional)
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)

        # Filtering by transaction type (optional)
        category_type = self.request.query_params.get('category_type', None)
        if category_type:
            queryset = queryset.filter(category__category_type=category_type)

        # Filtering by date range (optional)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            start_date = parse_date(start_date)
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            end_date = parse_date(end_date)
            queryset = queryset.filter(date__lte=end_date)

        return queryset
    
    def perform_create(self, serializer):
        category = self.request.data.get('category')
        category_obj = Category.objects.get(id=category)
        transaction_type = category_obj.category_type

        budget_id = self.request.data.get('budget')  # Assuming the budget ID is provided in the request

        if transaction_type == 'expense' and budget_id:
            try:
                budget = Budget.objects.get(id=budget_id, user=self.request.user)
                serializer.save(user=self.request.user, budget=budget)
            except Budget.DoesNotExist:
                raise serializer.ValidationError("Invalid budget selected")
        else:
            serializer.save()


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Budget.objects.filter(user=self.request.user)

        # Filter by timeframe (start date to end date)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(start_date__gte=start_date, end_date__lte=end_date)

        # Filter by category type (assuming you have a 'type' field in the Category model)
        category_type = self.request.query_params.get('category_type', None)
        if category_type:
            queryset = queryset.filter(category__category_type=category_type)

        return queryset
    

class SavingsGoalViewSet(viewsets.ModelViewSet):
    queryset = SavingsGoal.objects.all()
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class TotalIncomeExpenseReport(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        category_type = request.query_params.get('category_type', None)

        transactions = Transaction.objects.filter(user=user)

        if start_date and end_date:
            transactions = transactions.filter(date__gte=start_date, date__lte=end_date)

        
        if category_type:
            transactions = transactions.filter(category__category_type=category_type)

        income = transactions.filter(category__category_type = "Income").aggregate(total_income = Sum('amount'))['total_income'] or 0
        expense = transactions.filter(category__category_type = "Expense").aggregate(total_expense = Sum('amount'))['total_expense'] or 0

        return Response({
            'total_income': income,
            'total_expense': expense
        })
    

class IncomeExpenseTrendsReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        category_type = request.query_params.get('category_type', None)
        timeframe = request.query_params.get('timeframe', 'month')

        transactions = Transaction.objects.filter(user=user)

        if start_date and end_date:
            transactions = transactions.filter(date__gte=start_date, date__lte=end_date)

        if category_type:
            transactions = transactions.filter(category__category_type=category_type)

        if timeframe == 'month':
            transactions = transactions.annotate(period=TruncMonth('date'))
        elif timeframe == 'week':
            transactions = transactions.annotate(period=TruncWeek('date'))

        
        income_trends = transactions.filter(transaction_type="income").values('period').annotate(total_income=Sum('amount')).order_by('period')
        expense_trends = transactions.filter(transaction_type="expense").values('period').annotate(total_expenses=Sum('amount')).order_by('period')

        income_data = {str(item['period']): item['total_income'] for item in income_trends}
        expense_data = {str(item['period']): item['total_expenses'] for item in expense_trends}

        report_data = []
        all_periods = sorted(set(income_data.keys()).union(expense_data.keys()))

        for period in all_periods:
            report_data.append({
                'period': period,
                'total_income': income_data.get(period, 0),
                'total_expenses': expense_data.get(period, 0)
            })

        return Response({'trends': report_data})
    

class NetWorthReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        category_type = request.query_params.get('category_type', None)

        transactions = Transaction.objects.filter(user=user)

        if start_date and end_date:
            transactions = transactions.filter(date__gte=start_date, date__lte=end_date)

        if category_type:
            transactions = transactions.filter(category__category_type=category_type)

        income = transactions.filter(category__category_type='Income').aggregate(total_income=Sum('amount'))['total_income'] or 0
        expense = transactions.filter(category__category_type='Expense').aggregate(total_expense=Sum('amount'))['total_expense'] or 0

        savings = SavingsGoal.objects.filter(user = user).aggregate(total_savings=Sum('current_amount'))['total_savings'] or 0

        net_worth = income - expense + savings

        return Response({
            'net_worth': net_worth,
            'total_income': income,
            'total_expense': expense,
            'total_savings': savings
        })
    

class BudgetNotificationView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        budgets = Budget.objects.filter(user=request.user)
        alerts = []

        for budget in budgets:
            total_expenses = Transaction.objects.filter(budget=budget, transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
            if total_expenses > budget.allocated_amount:
                alerts.append({
                    'message': f"Your total expenses for the {budget.category.name} category have exceeded your allocated budget of {budget.allocated_amount}.",
                    'is_high_priority': True
                })

        return Response({
            'alerts': alerts
        })