from django.urls import path, include
from .views import *
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('',Thesis,name='home'),
    path('home/',Thesis,name='home'),
    path('portfolio/',Portfolio,name='portfolio'),
    path('team/',Team,name='team'),
    path('contact',Contact,name='contact'),
    # path('thesis',Thesis,name='thesis'),
    path('financerenaissance',FinanceRenaissance,name='financerenaissance'),
    path('faq/',FAQ, name='faq'),
    path('tnc/',TNC, name='tnc'),
	path('privacy/',Privacy, name='privacy'),
    path('funds/',Funds,name='funds'),
    path('methodology/',Methodology, name= 'methodology'),
]
