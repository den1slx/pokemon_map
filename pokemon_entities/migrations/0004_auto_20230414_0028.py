# Generated by Django 3.1.14 on 2023-04-13 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon_entities', '0003_pokemon_pokedex_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokemon',
            name='pokedex_num',
            field=models.IntegerField(blank=True),
        ),
    ]
