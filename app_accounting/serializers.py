from rest_framework import serializers
from app_accounting.models import Account, JournalEntry, JournalItem, Expense, ExpenseClaim, EmployeeLoan, EmployeeLoanRepayment

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = '__all__'


class JournalItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalItem
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'


class ExpenseClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseClaim
        fields = '__all__'


class EmployeeLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLoan
        fields = '__all__'


class EmployeeLoanRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLoanRepayment
        fields = '__all__'


