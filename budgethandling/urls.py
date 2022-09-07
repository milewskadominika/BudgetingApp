from django.urls import path
from . import views
from .views import CalendarView

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('expense/', views.expenses, name='expenses'),
    path('income/', views.incomes, name='incomes'),
    path('settings/', views.settings, name='settings'),
    path('register/', views.register, name="register"),
    path('history/', views.CalendarView.as_view(), name='history'),
    path('delete_transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('history/<int:category_nr>/<str:category_name>/', views.categories, name="categories"),
    path('stats/', views.stats, name="stats"),
]
