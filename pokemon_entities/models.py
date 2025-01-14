from django.db import models  # noqa F401


class PokemonElementType(models.Model):
    title = models.CharField(max_length=30, null=True)
    image = models.ImageField(blank=True, verbose_name='Путь к картинке на вашем устройстве', null=True)
    strong_against = models.ManyToManyField('self', symmetrical=False, blank=True)

    def __str__(self):
        return self.title


class Pokemon(models.Model):
    title_en = models.CharField(max_length=200, blank=True, null=True, verbose_name='Английское название')
    title_ru = models.CharField(max_length=200, null=True, verbose_name='Русское название')
    title_jp = models.CharField(max_length=200, blank=True, null=True, verbose_name='Японское название')
    element_type = models.ManyToManyField(PokemonElementType, blank=True)
    previous_evolution = models.ForeignKey(
        'self',
        verbose_name='Предшествующая эволюция',
        null=True,
        blank=True,
        related_name='next_evolutions',
        on_delete=models.CASCADE,
    )
    description = models.TextField('Описание', blank=True, null=True)
    image = models.ImageField(blank=True, null=True, verbose_name='Путь к картинке на вашем устройстве')

    def __str__(self):
        return f'id: {self.id} | Pokemon: {self.title_ru}'


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        verbose_name='id покемона в покедексе',
        related_name='pokemon_id',
    )
    latitude = models.FloatField(null=True, verbose_name='Широта')
    longitude = models.FloatField(null=True, verbose_name='Долгота')
    appeared_at = models.DateTimeField(null=True, verbose_name='Появление покемона')
    disappeared_at = models.DateTimeField(null=True, verbose_name='Исчезновение покемона')
    level = models.IntegerField(blank=True, null=True, verbose_name='Уровень')
    health = models.IntegerField(blank=True, null=True, verbose_name='Здоровье')
    strength = models.IntegerField(blank=True, null=True, verbose_name='Сила')
    defense = models.IntegerField(blank=True, null=True, verbose_name='Защита')
    stamina = models.IntegerField(blank=True, null=True, verbose_name='Выносливость')

    def __str__(self):
        return f'| {self.pokemon} |'


