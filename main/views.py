from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail, BadHeaderError

# Create your views here.


def Home(request):
    context={}
    return render(request,'home.html',context)

def Portfolio(request):
    context={}
    return render(request,'portfolio.html',context)

def Team(request):
    context={}
    return render(request,'team.html',context)

def Methodology(request):
    context={}
    return render(request,'methodology.html',context)

def Contact(request):
	if request.method == 'POST':
		form=ContactForm(request.POST)
		if form.is_valid():
			subject = "Website Inquiry"
			body = {
				'first_name': form.cleaned_data['first_name'],
				'last_name': form.cleaned_data['last_name'],
				'email': form.cleaned_data['email_address'],
				'phone': form.cleaned_data['phone'],
				'message':form.cleaned_data['message'],
			}
			message = "\n".join(body.values())
			messages.success(request, 'Message Submited. You will receive a response via mail')

			send_mail(subject, message, 'forbescapital@forbespartners.org', ['support@forbespartners.org'])


		return redirect ("home")
	
	form = ContactForm()
	
	context={'form':form}
	return render(request,'contact.html',context)




def Thesis(request):
    context={}
    return render(request,'thesis.html',context)

def FinanceRenaissance(request):
    context={}
    return render(request,'financerenaissance.html',context)


def FAQ(request):
	return render(request,'faq.html')

def TNC (request):
	return render(request,'tnc.html')
def Privacy (request):
	return render(request,'privacy.html')


def Funds (request):
	return render(request,'funds.html')
