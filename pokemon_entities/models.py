from django.db import models  # noqa F401


class Pokemon(models.Model):
    title_en = models.CharField(max_length=200, blank=True, unique=True, verbose_name='Английское название')
    title_ru = models.CharField(max_length=200, blank=True, null=True, verbose_name='Русскаое название')
    title_jp = models.CharField(max_length=200, blank=True, null=True, verbose_name='Японское название')
    pokedex_num = models.IntegerField(null=True, unique=True, verbose_name='id покемона в покедексе')
    evolutions = models.ForeignKey(
        'self',
        verbose_name='Пердшествующая эволюция',
        null=True,
        blank=True,
        related_name='next_evolution',
        on_delete=models.CASCADE,
    )
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    poke_image_local = models.ImageField(blank=True, null=True, verbose_name='Локальная картинка')
    poke_image_link = models.URLField(
        blank=True, null=True, verbose_name='Ссылка на картинку(используется если нет локальной)'
    )

    def __str__(self):
        if self.pokedex_num and self.pokedex_num > 0:
            return f'№{self.pokedex_num} |  {self.title_en}'

        return f'№???? |  {self.title_en}'


class PokemonEntity(models.Model):
    pokedex_num = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    Lat = models.FloatField(default=55.751244, verbose_name='Широта')
    Lon = models.FloatField(default=37.618423, verbose_name='Долгота')
    appeared_at = models.DateTimeField(null=True, blank=True, verbose_name='Появление покемона')
    disappeared_at = models.DateTimeField(null=True, blank=True, verbose_name='Исчезновение покемона')
    level = models.IntegerField(blank=True, null=True, verbose_name='Уровень')
    health = models.IntegerField(blank=True, null=True, verbose_name='Здоровье')
    strength = models.IntegerField(blank=True, null=True, verbose_name='Сила')
    defense = models.IntegerField(blank=True, null=True, verbose_name='Защита')
    stamina = models.IntegerField(blank=True, null=True, verbose_name='Выносливость')

    def __str__(self):
        if self.catching_start == self.catching_end is not None:
            return f'''| Pokemon:{self.pokedex_num} |'''  # end string
        elif self.catching_start == self.catching_end:
            return f'''| Pokemon:{self.pokedex_num} |'''  # end string
        return f'''| Pokemon: {self.pokedex_num} |'''  # end string
