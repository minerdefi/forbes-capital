from django import forms


class ContactForm(forms.Form):
	first_name = forms.CharField(max_length =100)
	last_name = forms.CharField(max_length = 100)
	email_address = forms.EmailField(max_length = 250)
	phone=forms.CharField(max_length=250)
	message = forms.CharField(widget = forms.Textarea, max_length = 2000)