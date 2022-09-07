from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User



# Register your models here.
from .models import MyUser, Category, Recurring_Expense, Transaction, Plots

admin.site.register(Plots)
admin.site.register(MyUser)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)
    raw_id_fields = ('user',)
    search_fields = ('name',)
admin.site.register(Recurring_Expense)
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'suma', 'date', 'typek', 'category')
    list_filter = ('typek', 'user', 'date' , 'category')
    raw_id_fields = ('user',)
    search_fields = ('name',)
    date_hierarchy = 'date'
    ordering = ('user','date')