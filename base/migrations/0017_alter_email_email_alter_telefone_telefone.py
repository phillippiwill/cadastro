# Generated by Django 5.1.2 on 2024-10-25 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_rename_endereco_email_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='telefone',
            name='telefone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
