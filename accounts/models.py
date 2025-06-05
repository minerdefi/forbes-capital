from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ValidationError

class TransactionHistory(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('earnings', 'Earnings'),
        ('tax','Tax'),
        ('ada','ADA'),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)  # Fixed: was datetime.now
    details = models.CharField(max_length=255, blank=True, null=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type.capitalize()} of {self.amount} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class Deposit(models.Model):
    CRYPTO_CHOICES = (
        ('USDT', 'USDT (TRC-20)'),
        ('BTC', 'BTC'),
        ('BCH', 'BCH'),
        ('ETH', 'ETH'),
        ('WIRE', 'Wire Transfer'),  # Added Wire Transfer as a deposit option
    )
    
    DEPOSIT_TYPE_CHOICES = (
        ('tax', 'Tax'),
        ('fund', 'Fund'),
        ('fees', 'Fees'),
        ('ada', 'ADA'),
    )
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=CRYPTO_CHOICES, default='BTC')
    deposit_type = models.CharField(max_length=50, choices=DEPOSIT_TYPE_CHOICES, default='fund')  # New field for deposit type
    confirmed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)  # Fixed: was datetime.now

    def save(self, *args, **kwargs):
        super(Deposit, self).save(*args, **kwargs)
        if self.confirmed:
            profile = self.user.profile
            if self.deposit_type == 'tax':
                profile.Tax_balance += self.amount
            else:
                profile.balance += self.amount
                profile.deposit += self.amount
            profile.save()
            # Log the confirmed transaction
            TransactionHistory.objects.create(
                user=self.user,
                transaction_type='deposit',
                amount=self.amount,
                confirmed=True,
                details=f"Deposit to {self.deposit_type} via {self.payment_type} - Confirmed"
            )

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({'Confirmed' if self.confirmed else 'Pending'})"




class Withdrawal(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    PAYMENT_CHOICES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether (TRC-20)'),
        ('WIRE', 'Wire Transfer'),  # Added Wire Transfer as a withdrawal option
    )
    
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    
    wallet_address = models.CharField(max_length=100, blank=True, null=True)  # Optional for Wire Transfer
    
    # Additional fields for Wire Transfer
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    routing_number = models.CharField(max_length=50, blank=True, null=True)
    
    request_date = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False)
    
    # Add transaction_pin field for withdrawal verification
    transaction_pin = models.CharField(max_length=6, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        from django.db import transaction
        
        profile = self.user.profile
        
        if self.processed and not self.pk:  # Only process once when first marked as processed
            # Validate the transaction PIN
            if not self.transaction_pin or profile.transaction_pin != self.transaction_pin:
                raise ValidationError("Invalid transaction PIN.")
            
            # Check if user has sufficient balance
            if profile.avail_balance < self.amount:
                raise ValidationError("Insufficient balance.")
            
            # Use database transaction to ensure atomicity
            with transaction.atomic():
                # Deduct the amount from the user's balance
                profile.balance -= self.amount
                profile.avail_balance -= self.amount
                profile.save()
                
                # Log the transaction
                TransactionHistory.objects.create(
                    user=self.user,
                    transaction_type='withdrawal',
                    amount=self.amount,
                    confirmed=True,
                    details=f"Withdrawal to {self.wallet_address or 'Bank Account'} via {self.payment_type}"
                )
        
        super(Withdrawal, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} ({'Processed' if self.processed else 'Pending'})"




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(null=True, blank=True, upload_to="static/profile/")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    earnings = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    ADA = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    avail_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    Tax_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    deposit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    transaction_pin = models.CharField(max_length=6, blank=True, null=True)

    def add_profit(self, amount):
        self.earnings += amount
        self.balance += amount
        self.save()
        # Log the transaction
        TransactionHistory.objects.create(
            user=self.user,
            transaction_type='earnings',
            amount=amount,
            confirmed = True,
            details="Earnings added"
        )

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}, earnings: {self.earnings}, PIN: {'Set' if self.transaction_pin else 'Not Set'}"


# Automatically create or update the Profile when a User is created or saved
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class WalletAddress(models.Model):
    CRYPTO_CHOICES = (
        ('USDT', 'USDT (TRC-20)'),
        ('BTC', 'BTC'),
        ('BCH', 'BCH'),
        ('ETH', 'ETH'),  # Add more cryptocurrency choices as needed
    )

    cryptocurrency = models.CharField(max_length=10, choices=CRYPTO_CHOICES, unique=True)
    address = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.get_cryptocurrency_display()} Address: {self.address}"
    


class Earnings(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)  # Fixed: was datetime.now
    confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        profile = self.user.profile
        if self.confirmed:
            # Add the profit to the user's balance
            profile.balance += self.amount
            profile.earnings += self.amount
            profile.save()
            # Log the profit addition
            TransactionHistory.objects.create(
                user=self.user,
                transaction_type='earnings',
                amount=self.amount,
                confirmed=True,
                details="Earnings"
            )
        super(Earnings, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - Earnings of {self.amount} ({'Confirmed' if self.confirmed else 'Pending'})"
    

class Tax(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)  # Fixed: was datetime.now
    confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        profile = self.user.profile
        if self.confirmed:
            # Add the profit to the user's balance
            
            profile.Tax_balance += self.amount
            profile.save()
            # Log the profit addition
            TransactionHistory.objects.create(
                user=self.user,
                transaction_type='tax',
                amount=self.amount,
                confirmed=True,
                details="Tax"
            )
        super(Tax, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - Tax of {self.amount} ({'Confirmed' if self.confirmed else 'Pending'})"
    


class ADA(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)  # Fixed: was datetime.now
    confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        profile = self.user.profile
        if self.confirmed:
            # Add the profit to the user's balance
            profile.balance += self.amount
            profile.ADA += self.amount
            profile.save()
            # Log the profit addition
            TransactionHistory.objects.create(
                user=self.user,
                transaction_type='ada',
                amount=self.amount,
                confirmed=True,
                details="ADA"
            )
        super(ADA, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - ADA of {self.amount} ({'Confirmed' if self.confirmed else 'Pending'})"