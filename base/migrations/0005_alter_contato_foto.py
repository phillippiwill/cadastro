# Generated by Django 5.1.2 on 2024-10-22 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_contato_foto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contato',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='static/images/fotos_perfil/'),
        ),
    ]
