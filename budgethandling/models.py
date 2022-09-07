from django.db import models
from django.contrib.auth.models import User
from django_matplotlib import MatplotlibFigureField
from django.urls import reverse

class MyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    balance = models.FloatField(default = 0)

    def __str__(self):
        return self.user.username

#kategorie wydatkow
class Category(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse("category_name", kwargs={"slug": self.name})


class Transaction(models.Model):
    name = models.CharField(max_length=30)
    suma = models.FloatField()
    date = models.DateTimeField()
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    typek = models.FloatField(choices = [(-1,'Wydatek'),(1, 'Przychód')])
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.name

    def sample_view(request):
        current_user = request.user
        return current_user.id

    def modify_balance(self):
        self.user.balance += self.typek * self.suma



#wydatki cykliczne
class Recurring_Expense(Transaction):
    interval_days = models.IntegerField()
    interval_weeks = models.IntegerField()
    interval_months = models.IntegerField()
    interval_years = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

class Plots(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    wydatki_kategorie = MatplotlibFigureField(figure='wydatki_kategorie')

