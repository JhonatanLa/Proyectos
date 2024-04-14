from django.db import models

class Entrevista(models.Model):
    correo = models.CharField(max_length=100)
    area_empresa = models.CharField(max_length=100)
    edad = models.IntegerField()
    genero = models.CharField(max_length=100)
    antiguedad = [
        ("Menos_de_6_meses", "Menos de 6 meses"),
        ("De_6_meses_a_1_año", "De 6 meses a 1 año"),
        ("De_1_año_a_5_años", "De 1 año a 5 años"),
        ("De_5_años_a_10_años", "De 5 años a 10 años"),
        ("Mas_de_10_años", "Más de 10 años")
    ]
    antiguedad = models.CharField(max_length=100, choices=antiguedad)

class PreguntaCerrada(models.Model):
    entrevista = models.ForeignKey(Entrevista, related_name='preguntas_cerradas', on_delete=models.CASCADE)
    pregunta = models.CharField(max_length=255)
    respuesta = models.CharField(max_length=255)

class PreguntaAbierta(models.Model):
    entrevista = models.ForeignKey(Entrevista, related_name='preguntas_abiertas', on_delete=models.CASCADE)
    pregunta = models.CharField(max_length=255)
    respuesta = models.CharField(max_length=255)
    
class Respuesta(models.Model):
        pregunta_cerrada = models.ForeignKey(PreguntaCerrada, related_name='respuestas', on_delete=models.CASCADE)
        respuesta = models.CharField(max_length=255)