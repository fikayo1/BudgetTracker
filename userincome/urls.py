from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('', views.index, name="income"),
    path('add-income', views.add_income, name="add-income"),
    path('edit-income/<int:id>', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>', views.delete_income, name="income-delete"),
    path('search-income', csrf_exempt(views.search_income), name="search-income"),
    path('stats', views.stats_view, name="in-stats"),
    path('export-csv', views.export_csv, name="export-csv"),
    path('export-excel', views.export_excel, name="export-excel"),
    path('income_source_summary/<int:year>/<int:month>/', views.income_source_summary, name="income_source_summary"),
]