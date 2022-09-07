from datetime import datetime, timedelta
from calendar import HTMLCalendar
from django.shortcuts import render
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.defchararray import upper
from .models import *
from io import BytesIO
import pandas
import base64



class Calendar(HTMLCalendar):

    def __init__(self, year=None, month=None, user=None):
    	self.year = year
    	self.month = month
    	self.user = user
    	super(Calendar, self).__init__()


    def wypisz_tranzakcje(self, month, transactions):
        transactions_per_month = transactions.filter(user = self.user, date__month=self.month)
        d = '<table class="table table-hover"> <thead> <tr> <th>#</th> <th>data</th> <th>nazwa</th> <th>kategoria</th> <th>należność</th><th>edycja</th></tr> </thead><tbody>'
        index = 1
        for transaction in transactions_per_month:
            if transaction.typek == -1:
                d+= f'<tr> <td>{index}</td> <td>{transaction.date.strftime("%d.%m.%Y")}</td> <td>{transaction.name}</td> <td><a href="/history/{ transaction.category.id }/{ transaction.category }/">{ transaction.category }</a></td> <td> -{transaction.suma } zł</td> <td><a href="/delete_transaction/{ transaction.id }/">USUŃ</a></td></tr>'
            elif transaction.typek == 1:
                d+= f'<tr> <td>{index}</td> <td>{transaction.date.strftime("%d.%m.%Y")}</td> <td>{transaction.name}</td> <td>{transaction.category} </td> <td> +{transaction.suma } zł</td> <td><a href="/delete_transaction/{ transaction.id }/">USUŃ</a></td></tr>'
            index+=1
        d+=f'</tbody></table>'
        return f'{d}'

    def wypisz_tranzakcje_roczne(self, month, transactions):
        transactions_per_year = transactions.filter(user = self.user, date__year=self.year)
        d = '<tr> <th>#</th> <th>data</th> <th>nazwa</th> <th>kategoria</th> <th>należność</th></tr>'
        index = 1
        for transaction in transactions_per_year:
            d+= f'<tr> <td>{index}</td> <td>{transaction.date.strftime("%d.%m.%Y")}</td> <td>{transaction.name}</td> <td>{transaction.category}</td> <td>  {transaction.suma}</td></tr>'
            index+=1
        d+=f'</tbody></table>'
        return f'{d}'

    	# formatowanie tego żeby tabela ładnie wyglądała - jak w banku
    	# filtrowanie tranzakcji ze wzgledu na rok i miesiąc
    def formatmonth(self, withyear=True):
    	transactions = Transaction.objects.filter(date__year=self.year, date__month=self.month)
    	cal = f''
    	cal += f'<h4> {self.formatmonthname(self.year, self.month, withyear=withyear)} </h4>\n'
    	cal+= f'{self.wypisz_tranzakcje(self.month, transactions)}\n'
    	return cal




def data_magic(transaction_list):

    lista = []
    i = 0

    for transaction in transaction_list:
        lista.append([])
        lista[i].append(transaction.category.name)
        lista[i].append(transaction.suma)
        i+=1

    return pandas.DataFrame(lista, columns=['Category', 'Suma'])



def get_chart(plottype, transactions):
    plt.switch_backend('AGG')
    colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(transactions)))

    d = data_magic(transactions)
    a = d.groupby('Category', as_index=False)['Suma'].sum()
    b = pandas.DataFrame(a, columns=['Category', 'Suma'])

    fig, ax = plt.subplots(figsize=(10,4))

    if plottype == '1':
        ax.bar(b['Category'], b['Suma'], color=colors)
        plt.xlabel('Kategoria')
        plt.ylabel('Kwota transakcji')

    else:
        ax.pie(b['Suma'], labels=b['Category'], autopct='%1.1f%%', colors = colors, shadow = True, )
        ax.axis('equal')

    plt.style.use('classic')
    plt.title("Zestawienie transakcji")
    plt.tight_layout()
    flike = BytesIO()
    fig.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    return b64

