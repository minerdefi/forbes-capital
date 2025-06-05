from django.contrib.auth.models import User
from rest_framework import serializers
from .models import TransactionHistory, Deposit, Withdrawal, Profile, WalletAddress, Earnings, Tax, ADA

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = '__all__'

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = '__all__'

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class WalletAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletAddress
        fields = '__all__'

class EarningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earnings
        fields = '__all__'

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = '__all__'

class ADASerializer(serializers.ModelSerializer):
    class Meta:
        model = ADA
        fields = '__all__'
