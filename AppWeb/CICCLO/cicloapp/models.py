from django.db import models

# Modelo para los datos demográficos
class DatosDemograficos(models.Model):
    marca_temporal = models.DateTimeField(auto_now_add=True)
    nombre_usuario = models.CharField(max_length=100)
    edad = models.IntegerField()
    genero = models.CharField(max_length=50)
    cargo_actual = models.CharField(max_length=100)
    area_empresa = models.CharField(max_length=100)
    antiguedad_empresa = models.CharField(max_length=100)

# Modelo para preguntas cerradas de opción múltiple (preguntas 1 a 41)
class PreguntasCerradas(models.Model):
    pregunta_1 = models.CharField(max_length=200)
    pregunta_2 = models.CharField(max_length=200)
    pregunta_3 = models.CharField(max_length=200)
    pregunta_4 = models.CharField(max_length=200)
    pregunta_5 = models.CharField(max_length=200)
    pregunta_6 = models.CharField(max_length=200)
    pregunta_7 = models.CharField(max_length=200)
    pregunta_8 = models.CharField(max_length=200)
    pregunta_9 = models.CharField(max_length=200)
    pregunta_10 = models.CharField(max_length=200)
    pregunta_11 = models.CharField(max_length=200)
    pregunta_12 = models.CharField(max_length=200)
    pregunta_13 = models.CharField(max_length=200)
    pregunta_14 = models.CharField(max_length=200)
    pregunta_15 = models.CharField(max_length=200)
    pregunta_16 = models.CharField(max_length=200)
    pregunta_17 = models.CharField(max_length=200)
    pregunta_18 = models.CharField(max_length=200)
    pregunta_19 = models.CharField(max_length=200)
    pregunta_20 = models.CharField(max_length=200)
    pregunta_21 = models.CharField(max_length=200)
    pregunta_22 = models.CharField(max_length=200)
    pregunta_23 = models.CharField(max_length=200)
    pregunta_24 = models.CharField(max_length=200)
    pregunta_25 = models.CharField(max_length=200)
    pregunta_26 = models.CharField(max_length=200)
    pregunta_27 = models.CharField(max_length=200)
    pregunta_28 = models.CharField(max_length=200)
    pregunta_29 = models.CharField(max_length=200)
    pregunta_30 = models.CharField(max_length=200)
    pregunta_31 = models.CharField(max_length=200)
    pregunta_32 = models.CharField(max_length=200)
    pregunta_33 = models.CharField(max_length=200)
    pregunta_34 = models.CharField(max_length=200)
    pregunta_35 = models.CharField(max_length=200)
    pregunta_36 = models.CharField(max_length=200)
    pregunta_37 = models.CharField(max_length=200)
    pregunta_38 = models.CharField(max_length=200)
    pregunta_39 = models.CharField(max_length=200)
    pregunta_40 = models.CharField(max_length=200)
    pregunta_41 = models.CharField(max_length=200)

# Modelo para preguntas abiertas (pregunta 42)
class PreguntaAbierta(models.Model):
    pregunta_42_situacion_1 = models.CharField(max_length=200, default='default_value')
    pregunta_42_situacion_2 = models.CharField(max_length=200, default='default_value')

# Modelo para preguntas con opciones de selección de importancia y respuesta abierta (pregunta 43 y 44)
class PreguntaImportancia(models.Model):
    pregunta_43_opcion_1 = models.IntegerField(default=0)
    pregunta_43_opcion_2 = models.IntegerField(default=0)
    pregunta_43_opcion_3 = models.IntegerField(default=0)
    pregunta_44_opcion_1 = models.IntegerField(default=0)
    pregunta_44_opcion_2 = models.IntegerField(default=0)
    pregunta_44_opcion_3 = models.IntegerField(default=0)
    pregunta_44_opcion_4 = models.CharField(max_length=300, blank=True)

# Modelo para la pregunta 45: Defectos
class PreguntaAbiertaDefectos(models.Model):
    defecto_1 = models.CharField(max_length=200)
    defecto_2 = models.CharField(max_length=200)
    defecto_3 = models.CharField(max_length=200)

# Modelo para la pregunta 46: Virtudes
class PreguntaAbiertaVirtudes(models.Model):
    virtud_1 = models.CharField(max_length=200)
    virtud_2 = models.CharField(max_length=200)
    virtud_3 = models.CharField(max_length=200)

# Modelo para la pregunta 47: Hábitos diarios
class PreguntaAbiertaHabitos(models.Model):
    habito_1 = models.CharField(max_length=200)
    habito_2 = models.CharField(max_length=200)

# Modelo para la pregunta 48: Hábitos mensuales
class PreguntaAbiertaHabitosMensuales(models.Model):
    habito_1 = models.CharField(max_length=200)
    habito_2 = models.CharField(max_length=200)

# Modelo para la pregunta 49: Hábitos anuales
class PreguntaAbiertaHabitosAnuales(models.Model):
    habito_1 = models.CharField(max_length=200)
    habito_2 = models.CharField(max_length=200)

# Modelo para la pregunta 50: Defectos de personas
class PreguntaAbiertaDefectosPersonas(models.Model):
    defectos_persona_A = models.CharField(max_length=200)
    defectos_persona_B = models.CharField(max_length=200)
    defectos_persona_C = models.CharField(max_length=200)

# Modelo para la pregunta 51: Virtudes de personas
class PreguntaAbiertaVirtudesPersonas(models.Model):
    virtudes_persona_A = models.CharField(max_length=200)
    virtudes_persona_B = models.CharField(max_length=200)
    virtudes_persona_C = models.CharField(max_length=200)

# Modelo para las preguntas abiertas 52 a 61
class PreguntaAbiertaCompaneros(models.Model):
    fiesta_integracion = models.CharField(max_length=200)
    defensa_intereses = models.CharField(max_length=200)
    representante_directivas = models.CharField(max_length=200)
    organizador_equipo_deportivo = models.CharField(max_length=200)
    organizador_equipos_trabajo = models.CharField(max_length=200)
    divulgacion_hechos = models.CharField(max_length=200)
    confianza_secreto = models.CharField(max_length=200)
    resolver_problemas = models.CharField(max_length=200)
    enseñanza_trabajo = models.CharField(max_length=200)
    lider_funcionario = models.CharField(max_length=200)

# Modelo para la pregunta 62
class PreguntaOrden(models.Model):
    pregunta_62_opcion_1 = models.CharField(max_length=200)
    pregunta_62_opcion_2 = models.CharField(max_length=200)
    pregunta_62_opcion_3 = models.CharField(max_length=200)

# Modelo para los comentarios adicionales
class ComentariosAdicionales(models.Model):
    comentarios = models.TextField()

