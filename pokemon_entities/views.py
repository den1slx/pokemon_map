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


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL,
                level=None, health=None, strength=None, defense=None, stamina=None):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    text = collect_string(level, health, strength, defense, stamina)

    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
        popup=text,
    ).add_to(folium_map)


def show_pokemon(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)
    types = pokemon.element_type.all()
    types = get_types(types, request)
    now = timezone.now()
    pokemon_entities = PokemonEntity.objects.filter(pokemon=pokemon, appeared_at__lte=now, disappeared_at__gte=now)

    image = get_image(request, pokemon)
    previous_evolution = pokemon.previous_evolution
    next_evolution = get_evolutions(request, pokemon.next_evolutions.first())
    previous_evolution = get_evolutions(request, previous_evolution)

    pokemon_info = {
        'pokemon_id': pokemon.id,
        'title_ru': pokemon.title_ru,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
        'img_url': image,
        'element_type': types,
    }

    if next_evolution:
        pokemon_info.update({'next_evolution': next_evolution})
    if previous_evolution:
        pokemon_info.update({'previous_evolution': previous_evolution})

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map,
            pokemon_entity.latitude,
            pokemon_entity.longitude,
            image,
            level=pokemon_entity.level,
            health=pokemon_entity.health,
            strength=pokemon_entity.strength,
            defense=pokemon_entity.defense,
            stamina=pokemon_entity.stamina,
        )
    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_info,
    })


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemons = Pokemon.objects.all()

    now = timezone.now()
    pokemon_entities = PokemonEntity.objects.filter(appeared_at__lte=now, disappeared_at__gte=now).select_related(
        'pokemon')
    for pokemon_entity in pokemon_entities:
        image = get_image(request, pokemon_entity.pokemon)
        add_pokemon(
            folium_map,
            pokemon_entity.latitude,
            pokemon_entity.longitude,
            image,
            level=pokemon_entity.level,
            health=pokemon_entity.health,
            strength=pokemon_entity.strength,
            defense=pokemon_entity.defense,
            stamina=pokemon_entity.stamina,
        )

    pokemons_on_page = []
    for pokemon in pokemons:
        image = get_image(request, pokemon)
        title = pokemon.title_ru
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
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
    if evolution and evolution.id:
        title = evolution.title_ru
        img_url = get_image(request, evolution)
        evolutions_info = {
            'title_ru': title,
            'pokemon_id': evolution.id,
            'img_url': img_url,
        }
    return evolutions_info


def collect_string(level, health, strength, defense, stamina):
    text = ''
    if level:
        text += f'Уровень: {level}\n'
    else:
        text += f'Уровень ???\n'
    if health:
        text += f'Здоровье: {health}\n'
    else:
        text += f'Здоровье ???\n'
    if strength:
        text += f'Сила: {strength}\n'
    else:
        text += f'Сила ???\n'
    if defense:
        text += f'Защита: {defense}\n'
    else:
        text += f'Защита ???\n'
    if stamina:
        text += f'Выносливость: {stamina} \n'
    else:
        text += f'Выносливость ???\n'
    return text


def get_types(types_objects, request):
    element_type = []
    for type_obj in types_objects:
        type_info = {
            'img': get_image(request, type_obj),
            'title': type_obj.title,
            'strong_against': type_obj.strong_against.all()
        }
        element_type.append(type_info)
    return element_type
