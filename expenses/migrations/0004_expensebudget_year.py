# Generated by Django 4.2.2 on 2023-07-19 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0003_expensebudget'),
    ]

    operations = [
        migrations.AddField(
            model_name='expensebudget',
            name='year',
            field=models.CharField(default='0000', max_length=256),
        ),
    ]