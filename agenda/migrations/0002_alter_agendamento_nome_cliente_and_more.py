# Generated by Django 4.0.3 on 2022-03-27 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agendamento',
            name='nome_cliente',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='agendamento',
            name='telefone_cliente',
            field=models.CharField(max_length=20),
        ),
    ]
