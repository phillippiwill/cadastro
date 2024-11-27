# Generated by Django 5.1.2 on 2024-10-22 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_remove_contato_interesses_delete_interesse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contato',
            name='estado',
            field=models.CharField(default='Desconhecido', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contato',
            name='municipio',
            field=models.CharField(default='Desconhecido', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contato',
            name='telefone_fixo',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
