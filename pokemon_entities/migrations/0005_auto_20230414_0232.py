# Generated by Django 3.1.14 on 2023-04-13 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon_entities', '0004_auto_20230414_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokemon',
            name='pokedex_num',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pokemon',
            name='title',
            field=models.CharField(blank=True, max_length=200, unique=True),
        ),
    ]