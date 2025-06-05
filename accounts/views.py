from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.db.models.query_utils import Q

from django.utils.encoding import force_bytes, force_str

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import JsonResponse

from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout as auth_logout
from django.http import HttpResponse
from .forms import *
from .models import *

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Registration successful. An activation email has been sent to your mail,please click on the link to activate your account.')
            user = form.save(request)
            login(request, user)
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                   for error in errors:
                       messages.error(request, f"{error}")         
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if (user is not None and default_token_generator.check_token(user, token)):
        user.is_active = True
        user.save()
        messages.add_message(request, messages.INFO, 'Account activated. Please login.')
    else:
        messages.add_message(request, messages.INFO, 'Link Expired. Contact admin to activate your account.')

    return redirect('login')

def UserLogin(request):
	if request.method == 'POST':
		form = EmailOrUsernameAuthenticationForm(request, request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			return redirect('dashboard')  # Replace 'home' with the URL name for your homepage
		else:
			messages.error(request,('Incorrect Username or Password. Please try again'))
	else:

		form = EmailOrUsernameAuthenticationForm()

	context ={'form':form}
	return render(request,'accounts/login.html',context)

def logout(request):
    auth_logout(request)
    messages.success(request, "Logout Success!")
    return redirect('home')

@login_required
def Dashboard(request):
    user = request.user
    profile = user.profile

    # Get the five most recent deposit and withdrawal transactions
    recent_transactions = TransactionHistory.objects.filter(
        user=user, 
        transaction_type__in=['deposit', 'withdrawal','earnings','ada','tax']
    ).order_by('-timestamp')[:5]

    # Get all profit logs
    earnings_logs = TransactionHistory.objects.filter(
        user=user, 
        transaction_type='earnings'
    ).order_by('-timestamp')
    total_balance = profile.balance
    total_earnings = profile.earnings
    
    total_deposits = TransactionHistory.objects.filter(user=request.user, transaction_type='deposit', confirmed=True).aggregate(total=models.Sum('amount'))['total'] or 0
    total_withdrawals = TransactionHistory.objects.filter(user=request.user, transaction_type='withdrawal', confirmed=True).aggregate(total=models.Sum('amount'))['total'] or 0
    availble_balance =profile.avail_balance
    ada=profile.ADA
    Tax_balance=profile.Tax_balance
    total_deposits_earnings = total_deposits + total_earnings


    context = {
        'profile': profile,
        'recent_transactions': recent_transactions,
        'earnings_logs': earnings_logs,
        'total_balance': total_balance,
        'total_earnings': total_earnings,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_deposits_earnings':total_deposits_earnings,
        'availble_balance':availble_balance,
        'ada':ada,
        'Tax_balance':Tax_balance
    }

    return render(request, 'accounts/dashboard.html', context)
@login_required
def History(request):
	user= request.user
	profile=user.profile
	transactions = TransactionHistory.objects.filter(
        user=user, 
        transaction_type__in=['deposit', 'withdrawal','profit','earnings','ada','tax']
    ).order_by('-timestamp')
	context ={
		'profile':profile,
		'transactions':transactions
    }
	return render(request, 'accounts/history.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
@login_required
def Deposit(request):
    user = request.user
    profile = user.profile
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.save()
            
            payment_type = form.cleaned_data['payment_type']
            deposit_type = form.cleaned_data['deposit_type']  # Get the deposit_type

            if payment_type == 'WIRE':
                # Store selected payment type and deposit type in session
                request.session['selected_payment_type'] = payment_type
                request.session['selected_deposit_type'] = deposit_type  # Store deposit_type
                # Redirect to a notification page for wire transfer
                return redirect('wire_transfer_notification')
            else:
                request.session['selected_payment_type'] = payment_type
                request.session['selected_deposit_type'] = deposit_type
                # For other payment types, redirect to the wallet address page
                return redirect('show_wallet_address')
    else:
        form = DepositForm()
        
    context = {'form': form, 'profile': profile}
    return render(request, 'accounts/deposit.html', context)



def wire_transfer_notification(request):
    return render(request, 'accounts/wire_transfer_notification.html')

@login_required
def show_wallet_address(request):
    user = request.user
    profile = user.profile
    selected_payment_type = request.session.get('selected_payment_type')

    if selected_payment_type:
        try:
            # Ensure that the WalletAddress is filtered by both user and selected cryptocurrency
            wallet_address = WalletAddress.objects.get(cryptocurrency=selected_payment_type)
            return render(request, 'accounts/wallet_address.html', {'wallet_address': wallet_address, 'profile': profile})
        except WalletAddress.DoesNotExist:
            # Handle case when wallet address for the selected payment type is not found
            return render(request, 'error.html', {'message': 'Wallet address not found.'})
    else:
        # Handle case when selected_payment_type is not found in session
        return render(request, 'error.html', {'message': 'Payment type not found.'})
@login_required      
def notify_admin_and_redirect(request):
	# Notify the admin (replace with your notification logic)
	admin_email = User.objects.get(is_superuser=True).email
	user = request.user
	subject = 'Payment Notification'
	message = f'{user.username} has made a deposit. Please verify the transaction.'
	send_mail(subject, message, 'forbescapital@forbespartners.org', [admin_email], fail_silently=False)
	# Add a success message
	messages.success(request, 'Payment notification sent to Forbes Capital.')
	# Redirect to the dashboard or a relevant page
	return redirect('dashboard')

@login_required
def withdrawal_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            transaction_pin = form.cleaned_data['transaction_pin']
            payment_type = form.cleaned_data['payment_type']

            # For cryptocurrency transfers
            wallet_address = form.cleaned_data.get('wallet_address', '')

            # For wire transfers
            bank_name = form.cleaned_data.get('bank_name', '')
            account_number = form.cleaned_data.get('account_number', '')
            routing_number = form.cleaned_data.get('routing_number', '')

            if amount > 0 and amount <= profile.avail_balance:
                if transaction_pin == profile.transaction_pin:
                    # Handle the creation of a Withdrawal object based on payment type
                    if payment_type == 'WIRE':
                        # Ensure all wire transfer fields are present
                        if not bank_name or not account_number or not routing_number:
                            messages.error(request, 'All bank details are required for wire transfers.')
                            return render(request, 'accounts/withdraw.html', {'form': form, 'profile': profile})
                        
                        withdrawal = Withdrawal(
                            user=request.user, 
                            amount=amount, 
                            payment_type=payment_type,
                            bank_name = bank_name,
                            account_number = account_number,
                            routing_number = routing_number
                        )
                        withdrawal.save()

                        context = {
                            'user': request.user,
                            'amount': amount,
                            'bank_name': bank_name,
                            'account_number': account_number,
                            'routing_number': routing_number,
                            'payment_type': payment_type,
                        }
                        subject = "Withdrawal Notification (Wire Transfer)"
                        html_message = render_to_string('email/withdrawal_email_wire.html', context)
                    else:
                        # Handle cryptocurrency withdrawals
                        if not wallet_address:
                            messages.error(request, 'Wallet address is required for cryptocurrency withdrawals.')
                            return render(request, 'accounts/withdraw.html', {'form': form, 'profile': profile})

                        withdrawal = Withdrawal(
                            user=request.user, 
                            amount=amount, 
                            wallet_address=wallet_address, 
                            payment_type=payment_type
                        )
                        withdrawal.save()

                        context = {
                            'user': request.user,
                            'amount': amount,
                            'wallet_address': wallet_address,
                            'payment_type': payment_type,
                        }
                        subject = "Withdrawal Notification (Cryptocurrency)"
                        html_message = render_to_string('email/withdrawal_email.html', context)

                    # Send email notifications to user and admin
                    email = strip_tags(html_message)
                    send_mail(subject, email, 'forbescapital@forbespartners.org', [user.email], html_message=html_message)
                    send_mail(subject, email, 'forbescapital@forbespartners.org', ['forbescapital@forbespartners.org'], html_message=html_message)
                    
                    messages.success(request, 'Withdrawal request submitted.')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid transaction PIN. Please try again.')
            else:
                messages.error(request, 'Withdrawal amount is lower than or exceeds the available balance.')
    else:
        form = WithdrawalForm()

    return render(request, 'accounts/withdraw.html', {'form': form, 'profile': profile})


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.txt"
                    c = {
                    "email":user.email,
                    'domain':'forbescapital@forbespartners.org',
                    'site_name': 'forbescapital@forbespartners.org',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'forbescapital@forbespartners.org' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})

from django.contrib.auth.views import PasswordChangeView
class AccountSettings(generic.UpdateView):
    form_class = EditProfileForm
    template_name = 'accounts/account_settings.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        # Return the Profile instance instead of User
        return self.request.user.profile

class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordEditForm  # Corrected to form_class
    template_name = 'accounts/change-password.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        # Return the Profile instance instead of User
        return self.request.user.profile



def create_transaction_pin(request):
	if request.method == 'POST':
		form = TransactionPinForm(request.POST)
		if form.is_valid():
			transaction_pin = form.cleaned_data['transaction_pin']
			confirm_transaction_pin = form.cleaned_data['confirm_transaction_pin']
			if transaction_pin == confirm_transaction_pin:
				user = request.user
				user.profile.transaction_pin = transaction_pin
				user.profile.save()  # Fixed: was user.save()
				messages.success(request, 'Transaction PIN created successfully.')
				return redirect('dashboard')  # Redirect to the user's profile page or wherever you want
			else:
				messages.error(request, 'Transaction PINs do not match.')
	else:
		form = TransactionPinForm()
	return render(request, 'accounts/create_transaction_pin.html', {'form': form})

from rest_framework import viewsets
from .models import TransactionHistory, Deposit, Withdrawal, Profile, WalletAddress, Earnings, Tax, ADA
from .serializers import TransactionHistorySerializer, DepositSerializer, WithdrawalSerializer, ProfileSerializer, WalletAddressSerializer, EarningsSerializer, TaxSerializer, ADASerializer, UserSerializer
from django.contrib.auth.models import User

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TransactionHistoryViewSet(viewsets.ModelViewSet):
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer

class DepositViewSet(viewsets.ModelViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer

class WithdrawalViewSet(viewsets.ModelViewSet):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class WalletAddressViewSet(viewsets.ModelViewSet):
    queryset = WalletAddress.objects.all()
    serializer_class = WalletAddressSerializer

class EarningsViewSet(viewsets.ModelViewSet):
    queryset = Earnings.objects.all()
    serializer_class = EarningsSerializer

class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer

class ADAViewSet(viewsets.ModelViewSet):
    queryset = ADA.objects.all()
    serializer_class = ADASerializer