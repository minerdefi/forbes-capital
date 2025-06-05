from django.urls import path, include
from .views import *
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('login/',UserLogin,name='login'),
    path('register/',signup,name='register'),
    path('activate/<uidb64>/<token>/',activate_account, name='activate'),
    path('logout/',logout,name='logout'),
    path('dashboard/',Dashboard,name='dashboard'),
    path('deposit/',Deposit,name='deposit'),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('show-wallet-address/', views.show_wallet_address, name='show_wallet_address'),
	path('processing/', views.notify_admin_and_redirect, name='processing'),
    path('withdrawal/', views.withdrawal_view, name='withdrawal'),
    path('history/',History,name='history'),
    path('create_transaction_pin/', views.create_transaction_pin, name='create_transaction_pin'),
    path('account_settings/',AccountSettings.as_view(),name='account_settings'),
    path("password_change/", PasswordsChangeView.as_view(), name="password_change"),
    path('wire-transfer-notification/', views.wire_transfer_notification, name='wire_transfer_notification'),
]