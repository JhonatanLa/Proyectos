from django.contrib import admin
from .models import Entrevista, PreguntaCerrada, PreguntaAbierta

# Registra tus modelos aquí

admin.site.register(Entrevista)
admin.site.register(PreguntaCerrada)
admin.site.register(PreguntaAbierta)
