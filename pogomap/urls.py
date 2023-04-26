from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from pokemon_entities import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.show_all_pokemons, name='mainpage'),
    path('pokemon/<pokemon_id>/', views.show_pokemon, name='pokemon'),
    path('debug/', include('debug_toolbar.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
