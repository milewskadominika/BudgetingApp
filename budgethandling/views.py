from django.shortcuts import render, redirect
from .forms import TransactionForm, CategoryForm, PlotForm, HistoryForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum


# HISTORIA
from datetime import datetime, timedelta, date
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe
import calendar

from .models import Transaction, MyUser, Category, Plots
from .utils import Calendar, get_chart

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


class CalendarView(generic.ListView):
    model = Transaction
    template_name = 'budgethandling/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get("month", None))
        u = self.request.user
        mu = MyUser.objects.get(user = u)
        cal = Calendar(d.year, d.month, user = mu)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
        suma_przychod = Transaction.objects.filter(user = mu,typek = 1, date__month=d.month).aggregate(Sum('suma'))['suma__sum']
        suma_wydatek = Transaction.objects.filter(user = mu,typek = -1, date__month=d.month).aggregate(Sum('suma'))['suma__sum']
        if suma_przychod is None:
            suma_przychod = 0
        if suma_wydatek is None:
            suma_wydatek = 0
        context["suma_przychod"] = suma_przychod
        context["suma_wydatek"] = suma_wydatek
        return context

# KONIEC HISTORII



def delete_transaction(request, transaction_id):
    u = request.user
    mu = MyUser.objects.get(user = u)

    transaction = Transaction.objects.get(pk=transaction_id)
    if transaction.typek == 1:
        mu.balance -= transaction.suma
    else:
        mu.balance += transaction.suma
    transaction.delete()
    mu.save()


    return redirect('history')

# Create your views here.

#rejestracja


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'budgethandling/register.html', {'form': form})



#strona glowna
def home(request):

    u = request.user

    if u.is_authenticated:
        mu = MyUser.objects.get(user = u)
        transaction_list = Transaction.objects.filter(user=mu).order_by('-date')[:5]
        d = get_date(request.GET.get("month", None))
        suma_przychod = Transaction.objects.filter(user = mu, typek = 1, date__month=d.month).aggregate(Sum('suma'))['suma__sum']
        suma_wydatek = Transaction.objects.filter(user = mu, typek = -1, date__month=d.month).aggregate(Sum('suma'))['suma__sum']
        if suma_przychod is None:
            suma_przychod = 0
        if suma_wydatek is None:
            suma_wydatek = 0

        try:
            saldo = suma_przychod - suma_wydatek
        except TypeError:
            saldo = 0

    else:
        form = UserCreationForm()
        return render(request, 'budgethandling/register.html', {'form': form})
    return render(request, 'budgethandling/home.html', {'transaction_list': transaction_list, 'saldo': saldo})







#strona z podzialami wydatkow
def categories(request, category_nr, category_name):
    context = {}
    context['form'] = HistoryForm()
    u = request.user
    mu = MyUser.objects.get(user = u)

    category_Transactions = Transaction.objects.filter(user=mu, category=category_nr)
    suma = Transaction.objects.filter(user=mu, category=category_nr).aggregate(Sum('suma'))['suma__sum']

    if request.method == 'POST':
        form = HistoryForm(request.POST)

        if form.is_valid():
            startdate = form['startdate'].value()
            enddate = form['enddate'].value()

            category_Transactions = Transaction.objects.filter(user=mu, date__range=(startdate, enddate), category=category_nr)
            suma = Transaction.objects.filter(user=mu, date__range=(startdate, enddate), category=category_nr).aggregate(Sum('suma'))['suma__sum']


    context["category_Transactions"] = category_Transactions
    context["suma"] = suma
    context["category_nr"] = category_nr
    context["category_name"] = category_name
    return render(request, 'budgethandling/categories.html', context)


#dodanie przychodu
def incomes(request):
    u = request.user
    mu = MyUser.objects.get(user = u)

    context = {}
    context['form'] = TransactionForm(mu)

    if request.method == 'POST':
        form = TransactionForm(mu, request.POST, request.FILES)

        if form.is_valid():
            name = form.cleaned_data['name']
            suma = form.cleaned_data['amount']
            date = form.cleaned_data['date']
            category= form.cleaned_data['categories']

            t = Transaction.objects.create(name = name, suma = suma, date=date, typek = 1, category= category, user = mu)
            t.save()
            mu.balance += mu.balance+suma
            mu.save()
    return render(request, 'budgethandling/incomes.html', context)


#dodanie wydaku
def expenses(request):
    context = {}
    u = request.user
    mu = MyUser.objects.get(user = u)
    context['form'] = TransactionForm(mu)


    if request.method == 'POST':
        form = TransactionForm(mu, request.POST, request.FILES)

        if form.is_valid():
            name = form.cleaned_data['name']
            suma = form.cleaned_data['amount']
            date = form.cleaned_data['date']
            category= form.cleaned_data['categories']

            t = Transaction.objects.create(name = name, suma = suma, date=date, typek = -1, category= category, user = mu)
            t.save()
            mu.balance -= suma
            mu.save()
    return render(request, 'budgethandling/expenses.html', context)


#ustawienia
def settings(request):
    context = {}
    context['form'] = CategoryForm()
    u = request.user
    mu = MyUser.objects.get(user = u)

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']

            c = Category.objects.create(name = name, user = mu)
            c.save()

    return render(request, 'budgethandling/settings.html', context)

def stats(request):
    u = request.user
    mu = MyUser.objects.get(user = u)

    context = {}
    context['form'] = PlotForm(mu)



    if request.POST:
        form = PlotForm(mu, request.POST)

        if form.is_valid():
            plottype = form['plottype'].value()
            startdate = form['startdate'].value()
            enddate = form['enddate'].value()


            transactions = Transaction.objects.filter(user=mu, date__range=(startdate, enddate))
            chart = get_chart(plottype, transactions)
            context['chart'] = chart



    return render(request, 'budgethandling/stats.html', context)











