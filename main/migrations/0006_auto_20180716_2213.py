# Generated by Django 2.0.4 on 2018-07-16 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20180716_2050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='practice',
            name='faculty',
        ),
        migrations.AddField(
            model_name='practice',
            name='speciality',
            field=models.CharField(blank=True, max_length=200, verbose_name='Специальность/Направление подготовки'),
        ),
        migrations.AlterField(
            model_name='documenttemplate',
            name='document_name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Уникальный ключ документа'),
        ),
    ]