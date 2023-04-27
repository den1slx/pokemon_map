from django.contrib import admin

from .models import Pokemon, PokemonEntity, PokemonElementType, ElementType

admin.site.register(Pokemon)
admin.site.register(PokemonEntity)
admin.site.register(PokemonElementType)
admin.site.register(ElementType)
