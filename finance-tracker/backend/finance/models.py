from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=7, choices=CATEGORY_TYPES)

    def __str__(self):
        return f"{self.name} ({self.category_type})"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Budget for {self.category.name}: {self.allocated_amount}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    budget = models.ForeignKey(Budget, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.category.name} - {self.amount}"


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()

    def __str__(self):
        return f"{self.goal_name} - {self.current_amount}/{self.target_amount}"