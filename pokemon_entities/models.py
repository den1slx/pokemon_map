from django.db import models  # noqa F401


class Pokemon(models.Model):
    title = models.CharField(max_length=200, blank=True, unique=True)
    pokedex_num = models.IntegerField(blank=True, null=True)
    poke_image = models.ImageField(blank=True, null=True)

    def __str__(self):
        if self.pokedex_num and self.pokedex_num > 0:
            return f'№{self.pokedex_num} |  {self.title}'

        if self.pokedex_num == 0:
            return f'№0 |  {self.title}'
        return f'???? |  {self.title}'


class PokemonEntity(models.Model):
    title = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    Lat = models.FloatField(default=0.0)
    Lon = models.FloatField(default=0.0)
    appeared_at = models.DateTimeField(null=True, blank=True)
    disappeared_at = models.DateTimeField(null=True, blank=True)
    catching_start = models.TimeField(null=True, blank=True)
    catching_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        if self.catching_start == self.catching_end is not None:
            return f'''Catching time: anytime | Coords: 
{self.Lat}:{self.Lon} | Pokemon:{self.title} |'''  # end string
        return f'''Catching time:
{self.catching_start}-{self.catching_end} | Coords:
{self.Lat}:{self.Lon} | Pokemon: {self.title} |'''  # end string
