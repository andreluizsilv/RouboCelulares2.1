# Generated by Django 5.1.1 on 2024-09-25 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roubos_celulares', '0005_remove_bairro_cidade_remove_bairro_latitude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bairro',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='bairro',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
