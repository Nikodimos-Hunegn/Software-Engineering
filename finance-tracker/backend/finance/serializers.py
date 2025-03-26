from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Transaction, Category, Budget, SavingsGoal
from datetime import date


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }
    
    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower().strip()

    def validate_username(self, value):
        """Ensure username is alphanumeric and has no spaces."""
        if ' ' in value:
            raise serializers.ValidationError("Username cannot contain spaces.")
        if not value.isalnum():
            raise serializers.ValidationError("Username must be alphanumeric.")
        return value.strip()

    def validate_password(self, value):
        """Ensure password meets minimum security requirements."""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        return value

    def validate_first_name(self, value):
        """Ensure first name is not empty and has no leading/trailing spaces."""
        return value.strip()

    def validate_last_name(self, value):
        """Ensure last name is not empty and has no leading/trailing spaces."""
        return value.strip()

    def create(self, validated_data):
        """Create a new user with a hashed password."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type']
        read_only_fields = ['id']

    def validate_name(self, value):
        """Ensure category name is unique per user and stripped of spaces."""
        user = self.context['request'].user if self.context.get('request') else None
        value = value.strip()
        if Category.objects.filter(name__iexact=value, user=user).exists():
            raise serializers.ValidationError("You already have a category with this name.")
        return value

    def validate_category_type(self, value):
        """Ensure category_type is either 'income' or 'expense'."""
        allowed_types = ['income', 'expense']
        if value.lower() not in allowed_types:
            raise serializers.ValidationError("Category type must be either 'income' or 'expense'.")
        return value.lower()


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'category', 'amount', 'date', 'description']
        read_only_fields = ['id']
    
    def validate_amount(self, value):
        """Ensure amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Transaction amount must be greater than zero.")
        return round(value, 2)  # Ensure only two decimal places
    
    def validate_date(self, value):
        """Ensure date is not in the future."""
        if value > date.today():
            raise serializers.ValidationError("Transaction date cannot be in the future.")
        return value

    def validate_category(self, value):
        """Ensure category belongs to the authenticated user."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and value.user != user:
            raise serializers.ValidationError("You do not own this category.")
        return value

    def validate_description(self, value):
        """Trim spaces and check for empty descriptions."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Description cannot be empty.")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user 
        return Transaction.objects.create(user = user, **validated_data)
    

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'category', 'allocated_amount', 'start_date', 'end_date']
        read_only_fields = ['id']
    
    def validate_allocated_amount(self, value):
        """Ensure allocated amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Allocated amount must be greater than zero.")
        return round(value, 2)  # Ensure only two decimal places

    def validate_start_date(self, value):
        """Ensure start date is not in the past."""
        if not self.instance and value < date.today():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return value

    def validate(self, data):
        """Ensure end date is after start date."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({"end_date": "End date must be after the start date."})

        return data

    def validate_category(self, value):
        """Ensure category belongs to the authenticated user."""
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("You do not own this category.")
        return value
    
    def create(self, validated_data):
        """Assign the user before saving the budget."""
        user = self.context['request'].user
        return Budget.objects.create(user=user, **validated_data)


class SavingsGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = ['id', 'goal_name', 'target_amount', 'current_amount', 'deadline']
        read_only_fields = ['id']
    
    def validate_target_amount(self, value):
        """Ensure target amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Target amount must be greater than zero.")
        return round(value, 2)

    def validate_current_amount(self, value):
        """Ensure current amount is positive."""
        if value < 0:
            raise serializers.ValidationError("Current amount cannot be negative.")
        return round(value, 2)

    def validate_deadline(self, value):
        """Ensure deadline is in the future."""
        if value <= date.today():
            raise serializers.ValidationError("Deadline must be a future date.")
        return value

    def validate(self, data):
        """Ensure current amount does not exceed target amount."""
        target_amount = data.get('target_amount', getattr(self.instance, 'target_amount', None))
        current_amount = data.get('current_amount', getattr(self.instance, 'current_amount', None))


        if target_amount is not None and current_amount is not None and current_amount > target_amount:
            raise serializers.ValidationError({"current_amount": "Current amount cannot exceed the target amount."})

        return data

    def create(self, validated_data):
        """Assign the user before saving the savings goal."""
        user = self.context['request'].user
        return SavingsGoal.objects.create(user=user, **validated_data)