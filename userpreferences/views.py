from django.shortcuts import render, redirect
import os
import json
from django.conf import settings
from . models import UserPreference
from django.contrib import messages
from expenses.models import ExpenseBudget,Category
from userincome.models import IncomeBudget, Source
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# Create your views here.


@login_required(login_url='/authentication/login')
def index(request):
    currency_data = []
    expense_category = Category.objects.all()
    income_source = Source.objects.all()
    months_of_the_year = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ]


    years = range(2000, 2100)
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

        for key,value in data.items():
            currency_data.append({'name':key, 'value':value})
        
    exists = UserPreference.objects.filter(user=request.user).exists()

    user_preferences = None

    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)
    if request.method == 'GET':
        context ={'currencies': currency_data, 'user_preferences':user_preferences,
         'months': months_of_the_year,
         'values': request.POST,
         'income_sources': income_source,
         'expense_category': expense_category,
         'years': years
         
        }

        return render(request, 'preferences/index.html', context)
    else:
        currency = request.POST['currency']
        
        if exists:
            currency = request.POST['currency']

            user_preferences.currency = currency
            user_preferences.save()
            # messages.success(request, 'Changes saved')
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Changes saved')
        return render(request, 'preferences/index.html', {'currencies': currency_data, 'user_preferences':user_preferences})


@login_required(login_url='/authentication/login')
def addIncomeBudget(request):
    if request.method == 'POST':
        income_amount = request.POST['income_amount']
        income_month = request.POST['income_month']
        income_year = request.POST['income_year']
        income_source = request.POST['income_source']
        
        
        if IncomeBudget.objects.filter(Q(owner=request.user) & Q(month=income_month) & Q(source=income_source)).exists():
            IncomeBudget.objects.filter(Q(owner=request.user) & Q(month=income_month) & Q(source=income_source)).update(
            source = income_source,
            amount = income_amount,
            month = income_month,
            year = income_year
            )
            messages.success(request, "income budget Updated")
            return redirect('preferences')
        else:
            IncomeBudget.objects.create(
                owner = request.user,
                source = income_source,
                amount = income_amount,
                month = income_month,
                year = income_year
            )
            messages.success(request, "income budget Saved")
            return redirect('preferences')

@login_required(login_url='/authentication/login')
def addExpenseBudget(request):
    if request.method == 'POST':
        expense_amount = request.POST['expense_amount']
        expense_month = request.POST['expense_month']
        expense_year = request.POST['expense_year']
        expense_category = request.POST['expense_category']

        if ExpenseBudget.objects.filter(Q(owner=request.user) & Q(month=expense_month) & Q(category=expense_category)).exists():
            ExpenseBudget.objects.filter(Q(owner=request.user) & Q(month=expense_month) & Q(category=expense_category)).update(
            category = expense_category,
            amount = expense_amount,
            month = expense_month,
            year = expense_month
            )
            messages.success(request, "expense budget Updated")
            return redirect('preferences')
        else:
            ExpenseBudget.objects.create(
                owner = request.user,
                category = expense_category,
                amount = expense_amount,
                month = expense_month,
                year = expense_year
            )
            messages.success(request, "expense budget Saved")
            return redirect('preferences')