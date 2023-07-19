from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='preferences'),
    path('incomebudget', views.addIncomeBudget, name='incomebudget'),
    path('expensebudget', views.addExpenseBudget, name='expensebudget'),
]