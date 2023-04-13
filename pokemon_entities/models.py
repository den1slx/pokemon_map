from django.db import models  # noqa F401


class Pokemon(models.Model):
    title = models.CharField(max_length=200, blank=True)
    pokedex_num = models.IntegerField(default=0)

    def __str__(self):
        if self.pokedex_num > 0:
            return f'№{self.pokedex_num}  {self.title}'
        return self.title
