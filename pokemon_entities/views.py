import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from .models import Pokemon, PokemonEntity
from django.utils import timezone
from random import choice


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
    pokemons = Pokemon.objects.all()
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemon = pokemons.filter(pokedex_num=pokemon_id)
    if not pokemon or int(pokemon_id) < 1:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    pokemon = pokemon[0]
    pokemon_entities = PokemonEntity.objects.filter(pokedex_num=pokemon)
    image = get_image(request, pokemon)
    previous_evolution = pokemon.evolutions
    next_evolution = None
    if pokemon.next_evolution.all():
        next_evolutions = pokemon.next_evolution.all()
        next_evolution = []
        for evolution in next_evolutions:
            evolution = get_evolutions(request, evolution)
            next_evolution.append(evolution)
    pokemon_id = pokemon.pokedex_num

    previous_evolution = get_evolutions(request, previous_evolution)

    pokemon_info = {
        'pokemon_id': pokemon_id,
        'title_ru': pokemon.title_ru,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
        'img_url': image,
        'entities': [{'lvl': '', 'lat': '', 'lon': ''}],
    }
    if next_evolution:
        if len(next_evolution) > 1:
            pokemon_info.update({f'next_evolution': choice(next_evolution)})
        else:
            pokemon_info.update({'next_evolution': next_evolution[0]})
    if previous_evolution:
        pokemon_info.update({'previous_evolution': previous_evolution})

    for pokemon_entity in pokemon_entities:
        if is_catching_time(pokemon_entity):
            add_pokemon(
                folium_map,
                pokemon_entity.latitude,
                pokemon_entity.longitude,
                image,
            )
    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_info,
    })


def show_all_pokemons(request):
    try:
        get_json_entity('pokemon_entities/pokemons.json')
    except FileNotFoundError:
        pass
    except KeyError:
        pass
    except json.JSONDecodeError:
        pass

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemons = Pokemon.objects.all()
    for pokemon in pokemons:
        pokemon_entities = PokemonEntity.objects.filter(pokedex_num=pokemon)
        for pokemon_entity in pokemon_entities:
            image = get_image(request, pokemon)
            if is_catching_time(pokemon_entity):
                add_pokemon(
                    folium_map,
                    pokemon_entity.latitude,
                    pokemon_entity.longitude,
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
        title = get_pokemon_name(pokemon)
        pokemons_on_page.append({
            'pokemon_id': poke_id,
            'img_url': image,
            'title_ru': title,
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
        check_pokemon = Pokemon.objects.filter(pokedex_num=pokemon_id)
        if not check_pokemon:
            Pokemon.objects.create(
                title_en=pokemon['title_en'],
                title_ru=pokemon['title_ru'],
                title_jp=pokemon['title_jp'],
                description=pokemon['description'],
                pokedex_num=pokemon_id,
                poke_image_link=pokemon['img_url']
            )
        else:
            check_pokemon.update(
                poke_image_link=pokemon['img_url'],
                description=pokemon['description'],
            )
        pokemon_obj = Pokemon.objects.filter(pokedex_num=pokemon_id)
        pokemon_obj = pokemon_obj[0]

        for pokemon_entity in pokemon['entities']:
            pokemon_entities = PokemonEntity.objects.filter(pokedex_num=pokemon_obj)
            check = pokemon_entities.filter(
                pokedex_num=pokemon_obj,
                latitude=pokemon_entity['lat'],
                longitude=pokemon_entity['lon'],
            )
            if not check:
                pokemon_entities.create(
                    pokedex_num=pokemon_obj,
                    latitude=pokemon_entity['lat'],
                    longitude=pokemon_entity['lon'],
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


def get_image(request, pokemon_object):
    image = pokemon_object.poke_image_local
    if not image:
        return pokemon_object.poke_image_link
    else:
        image = request.build_absolute_uri(pokemon_object.poke_image_local.url)
    if not image:
        return DEFAULT_IMAGE_URL
    return image


def get_evolutions(request, evolution):
    evolutions_info = None
    if evolution:
        title = get_pokemon_name(evolution)
        pokemon_id = evolution.pokedex_num
        img_url = get_image(request, evolution)
        if pokemon_id:
            evolutions_info = {
                'title_ru': title,
                'pokemon_id': int(pokemon_id),
                'img_url': img_url,
            },
    if evolutions_info:
        return evolutions_info[0]
    else:
        return None


def get_pokemon_name(pokemon):
    title = pokemon.title_ru
    if not title:
        title = pokemon.title_en
    if not title:
        title = pokemon.title_jp
    return title
