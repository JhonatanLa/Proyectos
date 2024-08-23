from django.contrib import admin
from .models import (
    DatosDemograficos,
    PreguntasCerradas,
    PreguntaAbierta,
    PreguntaImportancia,
    PreguntaAbiertaDefectos,
    PreguntaAbiertaVirtudes,
    PreguntaAbiertaHabitos,
    PreguntaAbiertaHabitosMensuales,
    PreguntaAbiertaHabitosAnuales,
    PreguntaAbiertaDefectosPersonas,
    PreguntaAbiertaVirtudesPersonas,
    PreguntaAbiertaCompaneros,
    PreguntaOrden,
    ComentariosAdicionales,
)

# Registro de modelos
admin.site.register(DatosDemograficos)
admin.site.register(PreguntasCerradas)
admin.site.register(PreguntaAbierta)
admin.site.register(PreguntaImportancia)
admin.site.register(PreguntaAbiertaDefectos)
admin.site.register(PreguntaAbiertaVirtudes)
admin.site.register(PreguntaAbiertaHabitos)
admin.site.register(PreguntaAbiertaHabitosMensuales)
admin.site.register(PreguntaAbiertaHabitosAnuales)
admin.site.register(PreguntaAbiertaDefectosPersonas)
admin.site.register(PreguntaAbiertaVirtudesPersonas)
admin.site.register(PreguntaAbiertaCompaneros)
admin.site.register(PreguntaOrden)
admin.site.register(ComentariosAdicionales)
