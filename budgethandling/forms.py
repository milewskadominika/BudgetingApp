from django import forms
from .models import Category, __str__
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class CategoryForm(forms.Form):
    name = forms.CharField( max_length=100, widget = forms.TextInput(attrs={'class':'form-control'}))

class TransactionForm(forms.Form):
    #def __init__(self, *args, **kwargs):
    #    self._user_id = kwargs.pop('user_id')
    #    super().__init__(*args, **kwargs)

    def __init__(self, myuser, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categories']=forms.ModelChoiceField(queryset=Category.objects.filter(user = myuser),widget = forms.Select(attrs={'class':'form-control'}))

    name = forms.CharField( max_length=100, widget = forms.TextInput(attrs={'class':'form-control'}))
    amount = forms.FloatField( min_value=0, widget = forms.NumberInput(attrs={'class':'form-control'}))
    categories = forms.ChoiceField()
    date = forms.DateField( widget=forms.widgets.DateInput(attrs={'type': 'date', 'class':'form-control'}))


class HistoryForm(forms.Form):

    startdate = forms.DateField( widget=forms.widgets.DateInput(attrs={'type': 'date', 'class':'form-control'}), required = False)
    enddate = forms.DateField( widget=forms.widgets.DateInput(attrs={'type': 'date', 'class':'form-control'}), required = False)


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='username', min_length=5, max_length=150)
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    def username_clean(self):
        username = self.cleaned_data['username'].lower()
        new = User.objects.filter(username = username)
        if new.count():
            raise ValidationError("User Already Exist")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")
        return password2

    def save(self, commit = True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user



class PlotForm(forms.Form):

    def __init__(self, myuser, *args, **kwargs):
        super().__init__(*args, **kwargs)






        self.fields['plottype']=forms.ChoiceField(choices=(('1', 'Słupkowy'), ('2', 'Kołowy')), widget = forms.Select(attrs={'class':'form-control'}))

    plottype = forms.ChoiceField()
    startdate = forms.DateField( widget=forms.widgets.DateInput(attrs={'type': 'date', 'class':'form-control'}), required = False)
    enddate = forms.DateField( widget=forms.widgets.DateInput(attrs={'type': 'date', 'class':'form-control'}), required = False)