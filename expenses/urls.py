from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('', views.homeView.as_view(), name="home"),
    path('expenses', views.index, name="expenses"),
    path('add-expense', views.add_expense, name="add-expense"),
    path('edit-expense/<int:id>', views.expense_edit, name="expense-edit"),
    path('expense-delete/<int:id>', views.delete_expense, name="expense-delete"),
    path('search-expenses', csrf_exempt(views.search_expenses), name="search-expenses"),
    path('expense_category_summary', views.expense_category_summary, name="expense_category_summary"),
    path('stats', views.stats_view, name="stats"),
    path('export-csv', views.export_csv, name="Export-csv"),
    path('export-excel', views.export_excel, name="Export-excel"),
    path('expense_category_summary/<int:year>/<int:month>/', views.expense_category_summary, name='expense_category_summary'),

    # path('export-pdf', views.export_pdf, name="export-pdf"),
]