from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(WalletAddress)
admin.site.register(Deposit)
admin.site.register(Withdrawal)
admin.site.register(TransactionHistory)
admin.site.register(Profile)
admin.site.register(Earnings)
admin.site.register(Tax)
admin.site.register(ADA)