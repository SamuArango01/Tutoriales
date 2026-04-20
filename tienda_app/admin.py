from django.contrib import admin

from .models import Inventario, Libro, Orden


admin.site.register(Libro)
admin.site.register(Inventario)
admin.site.register(Orden)
