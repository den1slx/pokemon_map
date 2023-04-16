import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from .models import Pokemon, PokemonEntity
from django.utils import timezone


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
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemon = Pokemon.objects.filter(pokedex_num=pokemon_id)
    if not pokemon or int(pokemon_id) < 1:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    pokemon = pokemon[0]
    pokemon_entities = PokemonEntity.objects.filter(title=pokemon)
    image = pokemon.poke_image_local
    if not image:
        image = pokemon.poke_image_link
    else:
        image = request.build_absolute_uri(pokemon.poke_image_local.url)
    pokemon_info = {
        'pokemon_id': pokemon_id,
        'title_ru': '',
        'title_en': pokemon.title,
        'title_jp': '',
        'description': '''''',
        'img_url': image,
        'entities': [],
        # 'next_evolution': {'title_ru': '', 'pokemon_id': '', 'img_url': ''},
        # 'previous_evolution': {'title_ru': '', 'pokemon_id': '', 'img_url': ''},
    }

    for pokemon_entity in pokemon_entities:
        if is_catching_time(pokemon_entity):
            add_pokemon(
                folium_map,
                pokemon_entity.Lat,
                pokemon_entity.Lon,
                image,
            )
    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_info,
    })


def show_all_pokemons(request):
    get_json_entity('pokemon_entities/pokemons.json')
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
            if is_catching_time(pokemon_entity):
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


def get_json_entity(path):
    with open(path, encoding='utf-8') as database:
        pokemons = json.load(database)['pokemons']
    for pokemon in pokemons:
        pokemon_id = pokemon['pokemon_id']
        check_pokemon = Pokemon.objects.filter(title=pokemon['title_en'], pokedex_num=pokemon_id)
        if not check_pokemon:
            Pokemon.objects.create(
                title=pokemon['title_en'],
                pokedex_num=pokemon_id,
                poke_image_link=pokemon['img_url']
            )
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


def is_catching_time(pokemon_entity_object):
    start = pokemon_entity_object.appeared_at
    end = pokemon_entity_object.disappeared_at
    now = timezone.now()
    if not now:
        return False
    if start and end:
        return start <= now <= end
    if start and not end:
        return start <= now
    if not start and end:
        return now < end
    if not start and not end:
        return False
