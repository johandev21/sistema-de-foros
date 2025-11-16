from django.contrib import admin
from .models import Usuario, Tematica, Foro, Publicacion, Historial, Palabrotas

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Tematica)
admin.site.register(Foro)
admin.site.register(Publicacion)
admin.site.register(Historial)
admin.site.register(Palabrotas)