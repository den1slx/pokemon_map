import folium

from django.shortcuts import render, get_object_or_404
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
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)

    now = timezone.now()
    pokemon_entities = PokemonEntity.objects.filter(pokemon=pokemon, appeared_at__lte=now, disappeared_at__gte=now)

    image = get_image(request, pokemon)
    previous_evolution = pokemon.previous_evolution
    next_evolution = None
    if pokemon.next_evolutions.count() > 0:
        next_evolution = get_evolutions(request, pokemon.next_evolutions.first())
    pokemon_id = pokemon.id

    previous_evolution = get_evolutions(request, previous_evolution)

    pokemon_info = {
        'pokemon_id': pokemon_id,
        'title_ru': pokemon.title_ru,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
        'img_url': image,
    }

    if next_evolution:
        pokemon_info.update({'next_evolution': next_evolution})
    if previous_evolution:
        pokemon_info.update({'previous_evolution': previous_evolution})

    for pokemon_entity in pokemon_entities:
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
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemons = Pokemon.objects.all()

    now = timezone.now()
    pokemon_entities = PokemonEntity.objects.filter(appeared_at__lte=now, disappeared_at__gte=now).prefetch_related(
        'pokemon')
    for pokemon_entity in pokemon_entities:
        image = get_image(request, pokemon_entity.pokemon)
        add_pokemon(
            folium_map,
            pokemon_entity.latitude,
            pokemon_entity.longitude,
            image,
        )

    pokemons_on_page = []
    for pokemon in pokemons:
        poke_id = pokemon.id
        if not poke_id:
            poke_id = 0
        image = pokemon.image
        if not image:
            image = DEFAULT_IMAGE_URL
        else:
            image = image.url
        title = pokemon.title_ru
        pokemons_on_page.append({
            'pokemon_id': poke_id,
            'img_url': image,
            'title_ru': title,
        })
    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def get_image(request, pokemon_object):
    image = pokemon_object.image
    if not image:
        return DEFAULT_IMAGE_URL
    image = request.build_absolute_uri(pokemon_object.image.url)
    return image


def get_evolutions(request, evolution):
    evolutions_info = None
    if evolution:
        title = evolution.title_ru
        pokemon_id = evolution.id
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
