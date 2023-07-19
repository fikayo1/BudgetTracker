from django.shortcuts import render, redirect   
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from expenses.models import ExpenseBudget
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import datetime
import csv
import xlwt
from django.views.generic import TemplateView

# import weasyprint
from django.template.loader import render_to_string
# from weasyprint import HTML
import tempfile
from django.db.models import Sum
# Create your views here.


class homeView(TemplateView):
    template_name = 'home.html'
@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = "AED: United Arab Emirates Dirham"

    context = {
        "expenses": expenses,
        "page_obj": page_obj,
        "currency": currency
    }
    return render(request, 'expenses/index.html', context)

@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    try:
        if request.method == "GET":
            
            return render(request, 'expenses/add_expense.html', context)


        if request.method == "POST":
            amount = request.POST['amount']

            if not amount:
                messages.error(request, 'Amount is required')
                return render(request, 'expenses/add_expense.html', context)
            description = request.POST['description']
            date = request.POST['expense_date']
            category = request.POST['category']


            if not description:
                messages.error(request, 'Description is required')
                return render(request, 'expenses/add_expense.html', context)
            
            Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
            messages.success(request, "Expense saved successfully")

            return redirect('expenses')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('expenses')
@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    
    context = {
        'expense': expense,
        'values':expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']


        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/edit-expense.html', context)

        
        
        
        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, "Expense Updated successfully")
        
        

        return redirect('expenses')
@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense removed")
    return redirect('expenses')


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        expenses = Expense.objects.filter(amount__istartswith = search_str, owner = request.user) | Expense.objects.filter(date__istartswith = search_str, owner = request.user) | Expense.objects.filter(description__icontains = search_str, owner = request.user) | Expense.objects.filter(category__icontains = search_str, owner = request.user)

        data = expenses.values()
        return JsonResponse(list(data), safe=False)

def expense_category_summary(request, month, year):
    year = int(year)
    month = int(month)
    # Calculate the start and end dates of the selected month
    start_date = datetime.date(year, month, 1)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1)
    else:
        end_date = datetime.date(year, month + 1, 1)

    
    
    expenses = Expense.objects.filter(owner=request.user, date__gte=start_date, date__lt=end_date)

    
    finalrep = {}
    category_list = list(set(expenses.values_list("category", flat=True)))  # Get distinct categories
    

    for category in category_list:
        amount_spent = expenses.filter(category=category).aggregate(Sum("amount"))["amount__sum"] or 0
        budget = ExpenseBudget.objects.filter(owner=request.user, category=category, month=month, year=year).first()
        budget_amount = budget.amount if budget else 0

        finalrep[category] = {
            "amount_spent": amount_spent,
            "budget": budget_amount,
        }
    # def get_cartegory(expense):
    #     return expense.category

    # category_list = list(set(map(get_cartegory, expenses)))

    # def get_category_amount(category):
    #     amount = 0
    #     filtered_by_category = expenses.filter(category=category)

    #     for item in filtered_by_category:
    #         amount += item.amount
    #     return amount

    # for i in expenses:
    #     for j in category_list:
    #         finalrep[j] = get_category_amount(j)
        
    # print(finalrep)

    return JsonResponse({"expense_category_data":finalrep}, safe=False)


def stats_view(request):
    expenses = Expense.objects.filter(owner = request.user)
    total_income = expenses.aggregate(Sum('amount'))

    year_range = range(2000, 2100)
    context = {
        "total_expense": total_income,
        "year_range": year_range
    }
    return render(request, 'expenses/stats.html', context)


def export_csv(request):
    response = HttpResponse(content_type = 'text\csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses'+ str(datetime.datetime.now()) + '.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner = request.user)
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response

def export_excel(request):
    response = HttpResponse(content_type = 'application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses'+ str(datetime.datetime.now()) + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response

# def export_pdf(request):
#     response = HttpResponse(content_type = 'application/pdf')
#     response['Content-Disposition'] = 'inline; attachment; filename=Expenses'+ str(datetime.datetime.now()) + '.pdf'

#     response['Content-Transfer-Encoding'] = 'binary'

#     expenses = Expense.objects.filter(owner = request.user)
#     sum = expenses.aggregate(Sum('amount'))

#     html_string = render_to_string('expenses/pdf-output.html', {'expenses': expenses, 'total': sum['amount__sum']})
#     html = HTML(string=html_string)

#     result = html.write_pdf()

#     with tempfile.NamedTemporaryFile(delete=True) as output:
#         output.write(result)
#         output.flush()


#         output = open(output.name, 'rb')
#         response.write(output.read())

#     return response