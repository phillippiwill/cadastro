# Generated by Django 5.1.2 on 2024-10-25 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_alter_email_email_alter_telefone_telefone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contato',
            name='celular',
        ),
        migrations.RemoveField(
            model_name='contato',
            name='email',
        ),
        migrations.RemoveField(
            model_name='contato',
            name='telefone_fixo',
        ),
    ]
