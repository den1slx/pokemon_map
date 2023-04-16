from django.db import models  # noqa F401


class Pokemon(models.Model):
    title_en = models.CharField(max_length=200, blank=True, unique=True)
    title_ru = models.CharField(max_length=200, blank=True, null=True)
    title_jp = models.CharField(max_length=200, blank=True, null=True)
    pokedex_num = models.IntegerField(null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    poke_image_local = models.ImageField(blank=True, null=True)
    poke_image_link = models.URLField(blank=True, null=True)

    def __str__(self):
        if self.pokedex_num and self.pokedex_num > 0:
            return f'№{self.pokedex_num} |  {self.title_en}'

        return f'№???? |  {self.title_en}'


class PokemonEntity(models.Model):
    pokedex_num = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    Lat = models.FloatField(default=55.5)
    Lon = models.FloatField(default=37.7)
    appeared_at = models.DateTimeField(null=True, blank=True)
    disappeared_at = models.DateTimeField(null=True, blank=True)
    catching_start = models.TimeField(null=True, blank=True)
    catching_end = models.TimeField(null=True, blank=True)
    level = models.IntegerField(blank=True, null=True)
    health = models.IntegerField(blank=True, null=True)
    strength = models.IntegerField(blank=True, null=True)
    defense = models.IntegerField(blank=True, null=True)
    stamina = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.catching_start == self.catching_end is not None:
            return f'''| Pokemon:{self.pokedex_num} |'''  # end string
        elif self.catching_start == self.catching_end:
            return f'''| Pokemon:{self.pokedex_num} |'''  # end string
        return f'''| Pokemon: {self.pokedex_num} |'''  # end string


class Evolution(models.Model):
    pokedex_num = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    next_evolution = models.IntegerField(blank=True, null=True)
    previous_evolution = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if not self.previous_evolution:
            return f'| {self.pokedex_num} | to №{self.next_evolution} |'
        if not self.next_evolution:
            return f'| {self.pokedex_num} | from №{self.previous_evolution} |'
        return f'| {self.pokedex_num} | from №{self.previous_evolution} | to №{self.next_evolution} |'

