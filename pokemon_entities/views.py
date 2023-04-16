import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_pokemon(request, pokemon_id):
    with open('pokemon_entities/pokemons.json', encoding='utf-8') as database:
        pokemons = json.load(database)['pokemons']

    for pokemon in pokemons:
        if pokemon['pokemon_id'] == int(pokemon_id):
            requested_pokemon = pokemon
            break
    else:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    for pokemon_entity in requested_pokemon['entities']:
        add_pokemon(
            folium_map, pokemon_entity['lat'],
            pokemon_entity['lon'],
            pokemon['img_url']
        )

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon
    })


def show_all_pokemons(request):
    unpack_json('pokemon_entities/pokemons.json')
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemons = Pokemon.objects.all()
    for pokemon in pokemons:
        pokemon_entities = PokemonEntity.objects.filter(title=pokemon)
        for pokemon_entity in pokemon_entities:
            image = pokemon.poke_image_local
            if not image:
                image = pokemon.poke_image_link
            else:
                image = image.path

            add_pokemon(
                folium_map,
                pokemon_entity.Lat,
                pokemon_entity.Lon,
                image,
            )

    pokemons_on_page = []
    for pokemon in pokemons:
        poke_id = pokemon.pokedex_num
        if not poke_id:
            poke_id = 0
        image = pokemon.poke_image_local
        if not image:
            image = pokemon.poke_image_link
        else:
            image = image.url
        pokemons_on_page.append({
            'pokemon_id': poke_id,
            'img_url': image,
            'title_ru': pokemon.title,
        })
    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def unpack_json(path):
    with open(path, encoding='utf-8') as database:
        pokemons = json.load(database)['pokemons']
    for pokemon in pokemons:
        pokemon_id = pokemon['pokemon_id']
        check_pokemon = Pokemon.objects.filter(title=pokemon['title_en'], pokedex_num=pokemon_id)
        if not check_pokemon:
            Pokemon.objects.create(title=pokemon['title_en'], pokedex_num=pokemon_id, poke_image_link=pokemon['img_url'])
        else:
            check_pokemon.update(poke_image_link=pokemon['img_url'])
        pokemon_obj = Pokemon.objects.filter(pokedex_num=pokemon_id)
        pokemon_obj = pokemon_obj[0]

        for pokemon_entity in pokemon['entities']:
            pokemon_entities = PokemonEntity.objects.filter(title=pokemon_obj)
            check = pokemon_entities.filter(
                title=pokemon_obj,
                Lat=pokemon_entity['lat'],
                Lon=pokemon_entity['lon'],
            )
            if not check:
                pokemon_entities.create(
                    title=pokemon_obj,
                    Lat=pokemon_entity['lat'],
                    Lon=pokemon_entity['lon'],
                )

