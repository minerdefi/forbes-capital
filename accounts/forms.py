from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import *



class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email', 'password1', 'password2']
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError("This field is required.")
        if User.objects.filter(email=self.cleaned_data['email']).count():
            raise ValidationError("Email is taken.")
        return self.cleaned_data['email']

    def save(self, request):
        user = super().save(commit=False)
        user.is_active = True
        user.save()
        context = {
             'from_email': settings.DEFAULT_FROM_EMAIL,
             'request': request,
             'protocol': request.scheme,
             'username': self.cleaned_data.get('username'),
             'domain': request.META['HTTP_HOST'],
             'uid': urlsafe_base64_encode(force_bytes(user.pk)),
             'token': default_token_generator.make_token(user),
            }
        subject ="Action Required to Complete the Account Creation"
        html_message= render_to_string('email/activation_email.html', context)
        email = strip_tags(html_message)
        send_mail(subject, email, 'forbescapital@forbespartners.org', [user.email],html_message=html_message)
        return user


class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ['amount', 'payment_type', 'deposit_type']
        help_texts = {
            'amount': 'Enter the amount you want to deposit.',
            'payment_type': 'Choose your preferred payment method.',
            'deposit_type': 'Select the type of deposit (e.g., tax, fund, fees, ADA).'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs.update({
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        })
        self.fields['payment_type'].widget.attrs.update({
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        })
        self.fields['deposit_type'].widget.attrs.update({
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        })



from django import forms
from django.contrib import messages

from django import forms
from django.core.exceptions import ValidationError

class WithdrawalForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        }),
    )
    
    PAYMENT_CHOICES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether (TRC-20)'),  # Fixed: was 'UST'
        ('WIRE', 'Wire Transfer'),
    )
    
    payment_type = forms.ChoiceField(
        choices=PAYMENT_CHOICES, 
        required=True, 
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        }),
    )
    
    wallet_address = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        }),
    )
    
    transaction_pin = forms.CharField(
        max_length=6, 
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        }),
    )
    
    bank_name = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        }),
    )
    
    account_number = forms.CharField(
        max_length=50,  # Increased from 20 to match model
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        }),
    )
    
    routing_number = forms.CharField(
        max_length=50,  # Increased from 9 to match model  
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'
        }),
    )
    
   





#Forms.py

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic']

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700'

class PasswordEditForm(PasswordChangeForm):
    old_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700',
                'type': 'password'
            }
        ),
    )
    new_password1 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700',
                'type': 'password'
            }
        ),
    )
    new_password2 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-orange-700',
                'type': 'password'
            }
        ),
    )



class TransactionPinForm(forms.Form):
	transaction_pin = forms.CharField(label='Transaction PIN',widget=forms.PasswordInput(attrs={'class': 'form-control'}),help_text="Enter a 4-digit PIN.")
	confirm_transaction_pin = forms.CharField(label='Confirm Transaction PIN',widget=forms.PasswordInput(attrs={'class': 'form-control'}),help_text="Confirm your 4-digit PIN.")
     


  
from django.contrib.auth.forms import AuthenticationForm


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email", widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full rounded-none bg-stone-300 dark:bg-stone-500 text-gray-700 border border-stone-600 py-2 px-3 leading-tight focus:outline-none focus:bg-white focus:border-base'
    }))