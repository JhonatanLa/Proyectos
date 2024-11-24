from django.shortcuts import render, redirect, HttpResponseRedirect
from django.db.models import Count
from django.conf import settings
from django.apps import apps
from django.http import JsonResponse
from .forms import ExcelUploadForm
from .models import *
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
from io import BytesIO
import os
import urllib, base64, urllib.parse
import pandas as pd
import seaborn as sns
import numpy as np
from kmodes.kmodes import KModes
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import torch
from transformers import BertTokenizer, BertForSequenceClassification, BertModel
from collections import Counter
from nltk.util import ngrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from transformers import BertModel, BertTokenizer
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import google.generativeai as genai
from IPython.display import Markdown
import textwrap
import sys
import re











def home(request):
    return render(request, 'base_generic.html')

def handle_uploaded_file(f):
    # Obtener la ruta del directorio media
    media_root = os.path.join(settings.BASE_DIR, 'media')
    # Crear el directorio uploads si no existe
    if not os.path.exists(os.path.join(media_root, 'uploads')):
        os.makedirs(os.path.join(media_root, 'uploads'))
    # Guardar el archivo en el sistema de archivos del servidor
    file_path = os.path.join(media_root, 'uploads', f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

column_mappingk = {
    "Marca temporal": "marca_temporal",
    "Nombre de usuario": "nombre_usuario",
    "Edad": "edad",
    "Género": "genero",
    "Mencione en qué área de la empresa se desempeña actualmente": "area_empresa",
    "Indique su antigüedad dentro de la empresa": "antiguedad_empresa",
    "1. La normas que rigen la empresa admiten la expresión de la forma de ser de sus empleados.": "pregunta_1",
    "2. Los empleados contribuyen con ideas en la toma de decisiones de la empresa.": "pregunta_2",
    "3. A usted le interesa participar en la toma de las decisiones de la empresa.": "pregunta_3",
    "4. En la empresa cuando se crea una norma, previamente las directivas hacen consultas con los empleados.": "pregunta_4",
    "5. En la empresa a algunas personas les aplican las normas con bastante rigor mientras a otras les perdonan todo.": "pregunta_5",
    "6. En general, la empresa está mejorando en relación a como era cuando usted ingresó como empleado.": "pregunta_6",
    "7. En relación con el día de su ingreso como empleado, usted nota mejoría en el desempeño de los empleados de la empresa.": "pregunta_7",
    "8. La comunicación de trabajo, desde su jefe inmediato hacia usted es fácil.": "pregunta_8",
    "9. La comunicación de trabajo, desde usted hacia su jefe inmediato es fácil.": "pregunta_9",
    "10. La comunicación con los grupos de trabajo con los que usted necesita relacionarse es fácil.": "pregunta_10",
    "11. Como impresión general, usted considera que en la empresa los empleados conocen sus funciones.": "pregunta_11",
    "12. Normalmente la cantidad de trabajo que tiene su cargo es excesiva.": "pregunta_12",
    "13. Las metas que se proponen en la empresa se cumplen.": "pregunta_13",
    "14. Actualmente hay la tendencia en la empresa a desperdiciar insumos de trabajo.": "pregunta_14",
    "15. En la empresa los problemas entre las personas se resuelven fácilmente.": "pregunta_15",
    "16. La forma como está organizado la empresa, es fácil de entender.": "pregunta_16",
    "17. Las tareas son supervisadas excesivamente.": "pregunta_17",
    "18. En la empresa las relaciones entre las personas son cordiales.": "pregunta_18",
    "19. Al interior de la empresa permanentemente hay conflictos.": "pregunta_19",
    "20. Los empleados son solidarios entre sí.": "pregunta_20",
    "21. Las personas en la empresa son tolerantes.": "pregunta_21",
    "22. Los empleados en la empresa se actualizan en los temas que necesita la organización.": "pregunta_22",
    "23. La empresa apoya la autonomía de sus empleados.": "pregunta_23",
    "24. La empresa apoya el desarrollo de carrera (ascensos) de sus empleados.": "pregunta_24",
    "25. La empresa apoya las sugerencias de los empleados para innovar (en procesos, productos, servicios, etc.).": "pregunta_25",
    "26. En la empresa la libertad de expresión se respeta.": "pregunta_26",
    "27. En general, usted se siente bien trabajando en la dependencia actual.": "pregunta_27",
    "28. Usted se siente bien trabajando en la empresa, en general.": "pregunta_28",
    "29. En general, la empresa paga los salarios que cada quien se merece.": "pregunta_29",
    "30. Frente a entidades parecidas, la empresa es fuerte.": "pregunta_30",
    "31. Esta organización le cumple a sus clientes.": "pregunta_31",
    "32. Si usted recibiera una oferta de trabajo de otra organización se iría, siendo las condiciones de la otra las mismas.": "pregunta_32",
    "33. Si usted recibiera una oferta de trabajo de otra organización se iría, siendo las condiciones de la otra mucho mejores.": "pregunta_33",
    "34. Las condiciones de su sitio de trabajo son adecuadas para desempeñarse bien.": "pregunta_34",
    "35. Es notable la presencia de grupos cerrados en los cuales se refugian sus integrantes.": "pregunta_35",
    "36. La cantidad de tareas que tiene su cargo es mayor a la de otros cargos que se le parecen.": "pregunta_36",
    "37. Su jefe sabe cómo hacer el trabajo de sus subalternos.": "pregunta_37",
    "38. Su jefe sabe cómo premiar a sus subalternos.": "pregunta_38",
    "39. Su jefe sabe cómo sancionar a sus subalternos.": "pregunta_39",
    "40. Su puesto de trabajo tiene variedad en la forma de ejecutar las tareas.": "pregunta_40",
    "41. Usted encuentra congruencia entre lo que busca en su vida laboral y lo que le ofrece su puesto de trabajo.": "pregunta_41",
    "42. Cite dos (2) situaciones, anécdotas, historias internas o algo típico, que refleje lo que distingue la cultura de esta organización frente a las que se le parecen. Algo que permita decir: ""esto solo pasa aquí"".\nSituación 1:": "pregunta_42_situacion_1",
    "42. Cite dos (2) situaciones, anécdotas, historias internas o algo típico, que refleje lo que distingue la cultura de esta organización frente a las que se le parecen. Algo que permita decir: ""esto solo pasa aquí"".\nSituación 2:": "pregunta_42_situacion_2",
    "43. Ordene, de mayor a menor importancia, las tres siguientes razones por las cuales usted trabaja aquí (seleccione 3 en la más importante, 2 en la que sigue y 1 en la menos importante): [Me siento bien con mis compañeros]": "pregunta_43_opcion_1",
    "43. Ordene, de mayor a menor importancia, las tres siguientes razones por las cuales usted trabaja aquí (seleccione 3 en la más importante, 2 en la que sigue y 1 en la menos importante): [Puedo ayudar a organizar los equipos de trabajo]": "pregunta_43_opcion_2",
    "43. Ordene, de mayor a menor importancia, las tres siguientes razones por las cuales usted trabaja aquí (seleccione 3 en la más importante, 2 en la que sigue y 1 en la menos importante): [Puedo avanzar hacia las metas que me he propuesto en la vida]": "pregunta_43_opcion_3",
    "44. Indique cuál de las siguientes fuentes de poder tiene mayor influencia en esta entidad (seleccione 3 en la más importante y 1 en la menos importante, seleccione 0 si no aplica): [Las directivas]": "pregunta_44_opcion_1",
    "44. Indique cuál de las siguientes fuentes de poder tiene mayor influencia en esta entidad (seleccione 3 en la más importante y 1 en la menos importante, seleccione 0 si no aplica): [Los empleados]": "pregunta_44_opcion_2",
    "44. Indique cuál de las siguientes fuentes de poder tiene mayor influencia en esta entidad (seleccione 3 en la más importante y 1 en la menos importante, seleccione 0 si no aplica): [Factores externos a la entidad]": "pregunta_44_opcion_3",
    "44. Indique cuál de las siguientes fuentes de poder tiene mayor influencia en esta entidad (seleccione 3 en la más importante y 1 en la menos importante, seleccione 0 si no aplica): [Factores externos a la entidad]": "pregunta_44_opcion_4",
    "45. Mencione tres (3) defectos de esta entidad.\nDefecto 1:": "pregunta_45_defecto_1",
    "45. Mencione tres (3) defectos de esta entidad.\nDefecto 2:": "pregunta_45_defecto_2",
    "45. Mencione tres (3) defectos de esta entidad.\nDefecto 3:": "pregunta_45_defecto_3",
    "46. Mencione tres (3) virtudes de esta entidad.\nVirtud 1:": "pregunta_46_virtud_1",
    "46. Mencione tres (3) virtudes de esta entidad.\nVirtud 2:": "pregunta_46_virtud_2",
    "46. Mencione tres (3) virtudes de esta entidad.\nVirtud 3:": "pregunta_46_virtud_3",
    "47. Mencione dos (2) hábitos diarios que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados.\nHábito 1:": "pregunta_47_habito_diario_1",
    "47. Mencione dos (2) hábitos diarios que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados.\nHábito 2:": "pregunta_47_habito_diario_2",
    "48. Mencione dos (2) hábitos mensuales que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados.\nHábito 1:": "pregunta_48_habito_mensual_1",
    "48. Mencione dos (2) hábitos mensuales que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados.\nHábito 2:": "pregunta_48_habito_mensual_2",
    "49. Mencione dos (2) hábitos anuales que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados.\nHábito 1:": "pregunta_49_habito_anual_1",
    "49. Mencione dos (2) hábitos anuales que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados.\nHábito 2:": "pregunta_49_habito_anual_2",
    "50. Piense en tres personas que se destacan negativamente dentro de la empresa y señale sólo sus defectos. No diga los nombres, sólo recuérdelas como las personas A, B y C.\nDefectos persona A:": "pregunta_50_defecto_persona_A",
    "50. Piense en tres personas que se destacan negativamente dentro de la empresa y señale sólo sus defectos. No diga los nombres, sólo recuérdelas como las personas A, B y C.\nDefectos persona B:": "pregunta_50_defecto_persona_B",
    "50. Piense en tres personas que se destacan negativamente dentro de la empresa y señale sólo sus defectos. No diga los nombres, sólo recuérdelas como las personas A, B y C.\nDefectos persona C:": "pregunta_50_defecto_persona_C",
    "51. Piense en tres personas que se destacan positivamente dentro de la empresa y señale sólo sus virtudes. No diga los nombres, sólo recuérdelas como las personas A, B y C.\nVirtudes persona A:": "pregunta_51_virtud_persona_A",
    "51. Piense en tres personas que se destacan positivamente dentro de la empresa y señale sólo sus virtudes. No diga los nombres, sólo recuérdelas como las personas A, B y C.\nVirtudes persona B:": "pregunta_51_virtud_persona_B",
    "51. Piense en tres personas que se destacan positivamente dentro de la empresa y señale sólo sus virtudes. No diga los nombres, sólo recuérdelas como las personas A, B y C.\nVirtudes persona C:": "pregunta_51_virtud_persona_C",
    "52. A cuál de sus compañeros elegiría para que organice una fiesta de integración en la empresa.": "pregunta_52",
    "53. A quién de la empresa elegiría para que defienda los intereses de su grupo profesional.": "pregunta_53",
    "54. A quién de la empresa elegiría para que lo represente ante las directivas de esta organización.": "pregunta_54",
    "55. A quién dentro de la empresa elegiría para que organice un equipo deportivo.": "pregunta_55",
    "56. A quién dentro de la empresa elegiría para que organice los equipos de trabajo.": "pregunta_56",
    "57. A quién dentro de la empresa elegiría para comentar y divulgar los hechos de la vida cotidiana de la organización.": "pregunta_57",
    "58. A cuál de sus compañeros le confiaría un secreto.": "pregunta_58",
    "59. A quién dentro de la empresa elegiría para resolver problemas entre compañeros de trabajo.": "pregunta_59",
    "60. A cuál de sus compañeros elegiría para que le enseñara a mejorar la forma de hacer su trabajo.": "pregunta_60",
    "61. Mencione a un funcionario de la empresa que según usted tiene rasgos de líder.": "pregunta_61",
    "62. Coloque 3 en lo que su jefe hace con más frecuencia y 1 en lo que casi nunca hace: (Primero leerle las 3 opciones completas. Y después leérselas una por una, para que las ordene). [Que los subalternos se sientan bien en sus sitios de trabajo aunque no": "pregunta_62_opcion_1",
    "62. Coloque 3 en lo que su jefe hace con más frecuencia y 1 en lo que casi nunca hace: (Primero leerle las 3 opciones completas. Y después leérselas una por una, para que las ordene). [Que las tareas se hagan bien y que los empleados estén bien]": "pregunta_62_opcion_2",
    "62. Coloque 3 en lo que su jefe hace con más frecuencia y 1 en lo que casi nunca hace: (Primero leerle las 3 opciones completas. Y después leérselas una por una, para que las ordene). [Que las tareas se hagan bien aunque los empleados estén mal]": "pregunta_62_opcion_3",
    "Puede escribir algunos comentarios adicionales si lo desea.": "comentarios",
}

column_mapping = [
    "marca_temporal",
    "nombre_usuario",
    "edad",
    "genero",
    "area_empresa",
    "antiguedad_empresa",
    "pregunta_1",
    "pregunta_2",
    "pregunta_3",
    "pregunta_4",
    "pregunta_5",
    "pregunta_6",
    "pregunta_7",
    "pregunta_8",
    "pregunta_9",
    "pregunta_10",
    "pregunta_11",
    "pregunta_12",
    "pregunta_13",
    "pregunta_14",
    "pregunta_15",
    "pregunta_16",
    "pregunta_17",
    "pregunta_18",
    "pregunta_19",
    "pregunta_20",
    "pregunta_21",
    "pregunta_22",
    "pregunta_23",
    "pregunta_24",
    "pregunta_25",
    "pregunta_26",
    "pregunta_27",
    "pregunta_28",
    "pregunta_29",
    "pregunta_30",
    "pregunta_31",
    "pregunta_32",
    "pregunta_33",
    "pregunta_34",
    "pregunta_35",
    "pregunta_36",
    "pregunta_37",
    "pregunta_38",
    "pregunta_39",
    "pregunta_40",
    "pregunta_41",
    "pregunta_42_situacion_1",
    "pregunta_42_situacion_2",
    "pregunta_43_opcion_1",
    "pregunta_43_opcion_2",
    "pregunta_43_opcion_3",
    "pregunta_44_opcion_1",
    "pregunta_44_opcion_2",
    "pregunta_44_opcion_3",
    "pregunta_44_opcion_4",
    "pregunta_45_defecto_1",
    "pregunta_45_defecto_2",
    "pregunta_45_defecto_3",
    "pregunta_46_virtud_1",
    "pregunta_46_virtud_2",
    "pregunta_46_virtud_3",
    "pregunta_47_habito_diario_1",
    "pregunta_47_habito_diario_2",
    "pregunta_48_habito_mensual_1",
    "pregunta_48_habito_mensual_2",
    "pregunta_49_habito_anual_1",
    "pregunta_49_habito_anual_2",
    "pregunta_50_defecto_persona_A",
    "pregunta_50_defecto_persona_B",
    "pregunta_50_defecto_persona_C",
    "pregunta_51_virtud_persona_A",
    "pregunta_51_virtud_persona_B",
    "pregunta_51_virtud_persona_C",
    "pregunta_52",
    "pregunta_53",
    "pregunta_54",
    "pregunta_55",
    "pregunta_56",
    "pregunta_57",
    "pregunta_58",
    "pregunta_59",
    "pregunta_60",
    "pregunta_61",
    "pregunta_62_opcion_1",
    "pregunta_62_opcion_2",
    "pregunta_62_opcion_3",
    "comentarios",
]


def upload_file(request):               
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            # Renombrar las columnas del DataFrame utilizando column_mapping
            df.columns = column_mapping
            # Convertir la columna 'marca_temporal' a un formato válido
            df['marca_temporal'] = pd.to_datetime(df['marca_temporal'])



            # Iterar sobre el DataFrame y guardar los datos en el modelo DatosDemograficos
            for index, row in df.iterrows():
                nuevo_registro = DatosDemograficos(
                    marca_temporal=row['marca_temporal'],
                    nombre_usuario=row['nombre_usuario'],
                    edad=row['edad'],
                    genero=row['genero'],
                    area_empresa=row['area_empresa'],
                    antiguedad_empresa=row['antiguedad_empresa']
                )
                nuevo_registro.save()



            # Iterar solo sobre las columnas específicas que representan preguntas cerradas de opción múltiple (preguntas 1 a 41)
            for index, row in df.iterrows():
                nueva_pregunta = PreguntasCerradas(
                        pregunta_1=row['pregunta_1'],
                        pregunta_2=row['pregunta_2'],
                        pregunta_3=row['pregunta_3'],
                        pregunta_4=row['pregunta_4'],
                        pregunta_5=row['pregunta_5'],
                        pregunta_6=row['pregunta_6'],
                        pregunta_7=row['pregunta_7'],
                        pregunta_8=row['pregunta_8'],
                        pregunta_9=row['pregunta_9'],
                        pregunta_10=row['pregunta_10'],
                        pregunta_11=row['pregunta_11'],
                        pregunta_12=row['pregunta_12'],
                        pregunta_13=row['pregunta_13'],
                        pregunta_14=row['pregunta_14'],
                        pregunta_15=row['pregunta_15'],
                        pregunta_16=row['pregunta_16'],
                        pregunta_17=row['pregunta_17'],
                        pregunta_18=row['pregunta_18'],
                        pregunta_19=row['pregunta_19'],
                        pregunta_20=row['pregunta_20'],
                        pregunta_21=row['pregunta_21'],
                        pregunta_22=row['pregunta_22'],
                        pregunta_23=row['pregunta_23'],
                        pregunta_24=row['pregunta_24'],
                        pregunta_25=row['pregunta_25'],
                        pregunta_26=row['pregunta_26'],
                        pregunta_27=row['pregunta_27'],
                        pregunta_28=row['pregunta_28'],
                        pregunta_29=row['pregunta_29'],
                        pregunta_30=row['pregunta_30'],
                        pregunta_31=row['pregunta_31'],
                        pregunta_32=row['pregunta_32'],
                        pregunta_33=row['pregunta_33'],
                        pregunta_34=row['pregunta_34'],
                        pregunta_35=row['pregunta_35'],
                        pregunta_36=row['pregunta_36'],
                        pregunta_37=row['pregunta_37'],
                        pregunta_38=row['pregunta_38'],
                        pregunta_39=row['pregunta_39'],
                        pregunta_40=row['pregunta_40'],
                        pregunta_41=row['pregunta_41']
                    )
                nueva_pregunta.save()



            # Iterar sobre las columnas especificadas que representan la pregunta 42
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaAbierta
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaAbierta.objects.create(
                    pregunta_42_situacion_1=row['pregunta_42_situacion_1'],
                    pregunta_42_situacion_2=row['pregunta_42_situacion_2']
                )
                nueva_pregunta.save()



            # Iterar sobre las columnas especificadas que representan las preguntas 43 y 44
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaImportancia
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaImportancia.objects.create(
                    pregunta_43_opcion_1=row['pregunta_43_opcion_1'],
                    pregunta_43_opcion_2=row['pregunta_43_opcion_2'],
                    pregunta_43_opcion_3=row['pregunta_43_opcion_3'],
                    pregunta_44_opcion_1=row['pregunta_44_opcion_1'],
                    pregunta_44_opcion_2=row['pregunta_44_opcion_2'],
                    pregunta_44_opcion_3=row['pregunta_44_opcion_3'],
                    pregunta_44_opcion_4=row['pregunta_44_opcion_4']
                )
                nueva_pregunta.save()



            # Iterar sobre las columnas específicas que representan los defectos de la pregunta 45
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaAbiertaDefectos
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaAbiertaDefectos.objects.create(
                    defecto_1=row['pregunta_45_defecto_1'],
                    defecto_2=row['pregunta_45_defecto_2'],
                    defecto_3=row['pregunta_45_defecto_3']
                )
                nueva_pregunta.save()



            # Iterar sobre las columnas específicas que representan las virtudes de la pregunta 46
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaAbiertaVirtudes
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaAbiertaVirtudes.objects.create(
                    virtud_1=row['pregunta_46_virtud_1'],
                    virtud_2=row['pregunta_46_virtud_2'],
                    virtud_3=row['pregunta_46_virtud_3']
                )
                nueva_pregunta.save()



            # Iterar sobre las columnas específicas que representan los hábitos diarios de la pregunta 47
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaAbiertaHabitos
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaAbiertaHabitos.objects.create(
                    habito_1=row['pregunta_47_habito_diario_1'],
                    habito_2=row['pregunta_47_habito_diario_2']
                )
                nueva_pregunta.save()



            # Iterar sobre las columnas específicas que representan los hábitos mensuales de la pregunta 48
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaAbiertaHabitosMensuales
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaAbiertaHabitosMensuales.objects.create(
                    habito_1=row['pregunta_48_habito_mensual_1'],
                    habito_2=row['pregunta_48_habito_mensual_2']
                )
                nueva_pregunta.save()



            # Iterar sobre las columnas específicas que representan los hábitos anuales de la pregunta 49
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaAbiertaHabitosAnuales
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaAbiertaHabitosAnuales.objects.create(
                    habito_1=row['pregunta_49_habito_anual_1'],
                    habito_2=row['pregunta_49_habito_anual_2']
                )
                nueva_pregunta.save()




            # Iterar sobre las columnas específicas que representan los defectos de personas de la pregunta 50
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaAbiertaDefectosPersonas
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaAbiertaDefectosPersonas.objects.create(
                    defectos_persona_A=row['pregunta_50_defecto_persona_A'],
                    defectos_persona_B=row['pregunta_50_defecto_persona_B'],
                    defectos_persona_C=row['pregunta_50_defecto_persona_C']
                )
                nueva_pregunta.save()



            # Iterar sobre las columnas específicas que representan las virtudes de personas de la pregunta 51
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaAbiertaVirtudesPersonas
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaAbiertaVirtudesPersonas.objects.create(
                    virtudes_persona_A=row['pregunta_51_virtud_persona_A'],
                    virtudes_persona_B=row['pregunta_51_virtud_persona_B'],
                    virtudes_persona_C=row['pregunta_51_virtud_persona_C']
                )
                nueva_pregunta.save()



            # Iterar sobre las columnas específicas que representan las preguntas abiertas
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaAbiertaCompaneros
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaAbiertaCompaneros.objects.create(
                    fiesta_integracion=row['pregunta_52'],
                    defensa_intereses=row['pregunta_53'],
                    representante_directivas=row['pregunta_54'],
                    organizador_equipo_deportivo=row['pregunta_55'],
                    organizador_equipos_trabajo=row['pregunta_56'],
                    divulgacion_hechos=row['pregunta_57'],
                    confianza_secreto=row['pregunta_58'],
                    resolver_problemas=row['pregunta_59'],
                    enseñanza_trabajo=row['pregunta_60'],
                    lider_funcionario=row['pregunta_61']
                )
                nueva_pregunta.save()



            # Iterar sobre las columnas específicas que representan las opciones de la pregunta 62
            # Iterar sobre el DataFrame y guardar los datos en el modelo PreguntaOrden
            for index, row in df.iterrows():
                nueva_pregunta = PreguntaOrden.objects.create(
                    pregunta_62_opcion_1=row['pregunta_62_opcion_1'],
                    pregunta_62_opcion_2=row['pregunta_62_opcion_2'],
                    pregunta_62_opcion_3=row['pregunta_62_opcion_3']
                )
                nueva_pregunta.save()


            #Comentarios Adicionales
            for index, row in df.iterrows():
                comentarios = row['comentarios']
                if comentarios.strip():  # Verificar si comentarios no está vacío
                    comentarios_adicionales = ComentariosAdicionales.objects.create(
                        comentarios=comentarios
                    )
                    comentarios_adicionales.save()



                # Redirigir al usuario a la página de resultados
                return redirect('view_results')
        else:
            return render(request, 'upload.html', {'form': form})
    else:
        form = ExcelUploadForm()
        return render(request, 'upload.html', {'form': form})





def base_generic(request):
    return render(request, 'base_generic.html')





def delete_data(request):
    # Eliminar todos los objetos de todos los modelos
    for model in apps.get_app_config('cicloapp').get_models():
        model.objects.all().delete()

    # Eliminar todas las gráficas generadas
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    for chart_file in os.listdir(chart_dir):
        chart_path = os.path.join(chart_dir, chart_file)
        if os.path.isfile(chart_path):
            os.remove(chart_path)

    # Redirigir a la vista base_generic
    return redirect('base_generic')











def view_data(request):
    # Obtener todos los modelos en la aplicación 'cicloapp'
    models = apps.get_app_config('cicloapp').get_models()

    # Crear un diccionario para almacenar los datos de cada modelo
    data = {}

    # Iterar sobre cada modelo
    for model in models:
        # Obtener todos los objetos del modelo actual
        objects = model.objects.all()

        # Obtener los datos como un diccionario
        data_dict = objects.values()

        # Crear un DataFrame especificando los nombres de las columnas
        df = pd.DataFrame(data_dict)

        # Convertir el DataFrame en una lista de diccionarios para poder pasarlo a la plantilla
        data[model.__name__] = df.to_dict(orient='records')


    # Renderizar la plantilla con los datos
    return render(request, 'data.html', {'data': data})








































# Función para generar la gráfica de barras
def generate_age_bar_chart(request):
    # Obtener los datos de la columna edad
    age_data = DatosDemograficos.objects.values('edad').annotate(count=Count('edad')).order_by('edad')

    # Extraer las edades y sus frecuencias
    ages = [item['edad'] for item in age_data]
    frequencies = [item['count'] for item in age_data]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras y la separación entre ellas
    bar_width = 0.8  # Ancho de las barras
    bar_spacing = 0.1  # Espacio entre barras

    # Calcular la ubicación de cada barra
    bar_positions = np.arange(len(ages))

    # Crear la gráfica de barras
    bars = ax.bar(bar_positions, frequencies, width=bar_width, color='skyblue', align='center')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Edad')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribución de Edades')
    ax.set_xticks(bar_positions)  # Establecer las posiciones de las barras como marcas en el eje x
    ax.set_xticklabels(ages)  # Establecer las edades como etiquetas en el eje x

    # Mostrar la cantidad exacta de veces que se repite cada edad en el eje y
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica (horizontal)
    description = 'Esta gráfica muestra la distribución de edades con la frecuencia exacta de cada edad'
    ax.text(1.02, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=10))

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'age_distribution_chart.png')
    fig.tight_layout(pad=4.0)  # Ajuste automático del diseño para que el texto no se corte
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'age_distribution_chart.png')

    return chart_url  # Devolver la URL de la imagen







def generate_gender_bar_chart(request):
    # Obtener los datos de la columna género
    gender_data = DatosDemograficos.objects.values('genero').annotate(count=Count('genero')).order_by('genero')

    # Extraer los géneros y sus frecuencias
    genders = [item['genero'] for item in gender_data]
    frequencies = [item['count'] for item in gender_data]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras y la separación entre ellas
    bar_width = 0.5  # Ancho de las barras

    # Calcular la ubicación de cada barra
    bar_positions = np.arange(len(genders))

    # Crear la gráfica de barras
    bars = ax.bar(bar_positions, frequencies, width=bar_width, color='lightgreen', align='center')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Género')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribución de Género')
    ax.set_xticks(bar_positions)  # Establecer las posiciones de las barras como marcas en el eje x
    ax.set_xticklabels(genders)  # Establecer los géneros como etiquetas en el eje x

    # Mostrar la cantidad exacta de veces que se repite cada género en el eje y
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica (horizontal)
    description = 'Esta gráfica muestra la distribución de género con la frecuencia exacta de cada género'
    ax.text(1.02, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=10))

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'gender_distribution_chart.png')
    fig.tight_layout(pad=4.0)  # Ajuste automático del diseño para que el texto no se corte
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'gender_distribution_chart.png')

    return chart_url  # Devolver la URL de la imagen










def generate_area_empresa_chart(request):
    # Obtener los datos de la columna "area_empresa"
    area_empresa_data = DatosDemograficos.objects.values('area_empresa').annotate(count=Count('area_empresa')).order_by('area_empresa')

    # Normalizar las áreas de empresa y sus frecuencias
    areas_empresa = [item['area_empresa'] for item in area_empresa_data]
    frequencies = [item['count'] for item in area_empresa_data]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(12, 6))

    # Crear la gráfica de barras
    bars = ax.bar(areas_empresa, frequencies, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Área de Empresa')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribución de Áreas de Empresa')

    # Rotar los nombres de las barras y ajustar el espaciado
    ax.set_xticks(range(len(areas_empresa)))  # Establecer las posiciones de las barras como marcas en el eje x
    ax.set_xticklabels(areas_empresa, rotation=45, ha='right')  # Rotar los nombres de las barras

    # Mostrar la cantidad exacta de veces que se repite cada área de empresa en el eje y
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica (horizontal)
    description = 'Esta gráfica muestra la distribución de áreas de empresa con la frecuencia exacta de cada área'
    ax.text(1.02, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=10))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'area_empresa_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'area_empresa_chart.png')

    return chart_url









def generate_antiguedad_empresa_chart(request):
    # Obtener los datos de la columna "antiguedad_empresa"
    antiguedad_empresa_data = DatosDemograficos.objects.values('antiguedad_empresa').annotate(count=Count('antiguedad_empresa')).order_by('antiguedad_empresa')

    # Extraer las antigüedades de empresa y sus frecuencias
    antiguedades_empresa = [item['antiguedad_empresa'] for item in antiguedad_empresa_data]
    frequencies = [item['count'] for item in antiguedad_empresa_data]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(12, 6))

    # Crear la gráfica de barras
    bars = ax.bar(antiguedades_empresa, frequencies, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Antigüedad en la Empresa')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribución de Antigüedad en la Empresa')

    # Mostrar la cantidad exacta de veces que se repite cada antigüedad en la empresa en el eje y
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica (horizontal)
    description = 'Esta gráfica muestra la distribución de antigüedad en la empresa con la frecuencia exacta de cada nivel'
    ax.text(1.02, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=10))

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'antiguedad_empresa_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'antiguedad_empresa_chart.png')

    return chart_url







#Monitoreo de datos
def obtener_opciones_y_frecuencias():
    # Obtener todas las instancias del modelo PreguntasCerradas
    preguntas_cerradas = PreguntasCerradas.objects.all()

    # Inicializar un diccionario para almacenar las opciones y sus frecuencias para cada pregunta
    opciones_frecuencias_por_pregunta = {}

    # Iterar sobre cada campo de pregunta en el modelo PreguntasCerradas
    for campo in PreguntasCerradas._meta.fields:
        if campo.name.startswith('pregunta_'):
            # Obtener todas las respuestas para la pregunta actual
            respuestas = [getattr(pregunta, campo.name) for pregunta in preguntas_cerradas]

            # Contar las frecuencias de cada respuesta
            frecuencias = Counter(respuestas)

            # Almacenar las opciones y sus frecuencias en el diccionario
            opciones_frecuencias_por_pregunta[campo.name] = frecuencias

    return opciones_frecuencias_por_pregunta

def tabla_datos(request):
    # Llamar a la función para obtener las opciones y frecuencias
    opciones_frecuencias = obtener_opciones_y_frecuencias()

    # Crear un DataFrame de pandas para mostrar los resultados
    df = pd.DataFrame(opciones_frecuencias).T

    # Calcular el total de encuestados por cada ítem
    df['Total entrevistados'] = df.sum(axis=1)

    # Calcular los porcentajes de cada opción de respuesta para cada ítem
    for columna in df.columns[:-1]:
        df[columna + ' (%)'] = (df[columna] / df['Total entrevistados'] * 100).round(2)  
    # Crear una figura y ejes de tabla con matplotlib.figure.Figure
    fig = Figure(figsize=(30, 20), dpi=100)
    ax = fig.subplots()

    # Ocultar los ejes
    ax.axis('tight')
    ax.axis('off')

    # Crear la tabla en los ejes
    tabla = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     loc='center',
                     cellLoc='center',
                     colWidths=[0.11] * len(df.columns),  # Ajuste de ancho de columnas
                     colColours=["#f5f5f5"] * len(df.columns))

    # Ajustar el diseño de la tabla
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)


    # Crear un lienzo de figura para renderizar la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'tabla_datos.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    table_url = os.path.join(settings.MEDIA_URL, 'charts', 'tabla_datos.png')

    return table_url










def generate_pregunta_1_chart(request):
    # Obtener los datos de la pregunta_1
    pregunta_1_data = PreguntasCerradas.objects.values('pregunta_1').annotate(count=Count('pregunta_1')).order_by('pregunta_1')

    # Extraer las opciones de la pregunta_1 y sus frecuencias
    opciones = [item['pregunta_1'] for item in pregunta_1_data]
    frequencies = [item['count'] for item in pregunta_1_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('1. Las normas que rigen la empresa admiten la expresión de la forma de ser de sus empleados.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 1.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_1_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_1_chart.png')

    return chart_url









def generate_pregunta_2_chart(request):
    # Obtener los datos de la pregunta_2
    pregunta_2_data = PreguntasCerradas.objects.values('pregunta_2').annotate(count=Count('pregunta_2')).order_by('pregunta_2')

    # Extraer las opciones de la pregunta_2 y sus frecuencias
    opciones = [item['pregunta_2'] for item in pregunta_2_data]
    frequencies = [item['count'] for item in pregunta_2_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('2. Los empleados contribuyen con ideas en la toma de decisiones de la empresa')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 2.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_2_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_2_chart.png')

    return chart_url







def generate_pregunta_3_chart(request):
    # Obtener los datos de la pregunta_3
    pregunta_3_data = PreguntasCerradas.objects.values('pregunta_3').annotate(count=Count('pregunta_3')).order_by('pregunta_3')

    # Extraer las opciones de la pregunta_3 y sus frecuencias
    opciones = [item['pregunta_3'] for item in pregunta_3_data]
    frequencies = [item['count'] for item in pregunta_3_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('3. A usted le interesa participar en la toma de las decisiones de la empresa')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 3.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_3_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_3_chart.png')

    return chart_url







def generate_pregunta_4_chart(request):
    # Obtener los datos de la pregunta_4
    pregunta_4_data = PreguntasCerradas.objects.values('pregunta_4').annotate(count=Count('pregunta_4')).order_by('pregunta_4')

    # Extraer las opciones de la pregunta_4 y sus frecuencias
    opciones = [item['pregunta_4'] for item in pregunta_4_data]
    frequencies = [item['count'] for item in pregunta_4_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('4. En la empresa cuando se crea una norma, previamente las directivas hacen consultas con los empleados.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 4.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_4_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_4_chart.png')

    return chart_url








def generate_pregunta_5_chart(request):
    # Obtener los datos de la pregunta_5
    pregunta_5_data = PreguntasCerradas.objects.values('pregunta_5').annotate(count=Count('pregunta_5')).order_by('pregunta_5')

    # Extraer las opciones de la pregunta_5 y sus frecuencias
    opciones = [item['pregunta_5'] for item in pregunta_5_data]
    frequencies = [item['count'] for item in pregunta_5_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('5. En la empresa a algunas personas les aplican las normas con bastante rigor mientras a otras les perdonan todo.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 5.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_5_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_5_chart.png')

    return chart_url










def generate_pregunta_6_chart(request):
    # Obtener los datos de la pregunta_6
    pregunta_6_data = PreguntasCerradas.objects.values('pregunta_6').annotate(count=Count('pregunta_6')).order_by('pregunta_6')

    # Extraer las opciones de la pregunta_6 y sus frecuencias
    opciones = [item['pregunta_6'] for item in pregunta_6_data]
    frequencies = [item['count'] for item in pregunta_6_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('6. En general, la empresa está mejorando en relación a como era cuando usted ingresó como empleado.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 6.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_6_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_6_chart.png')

    return chart_url








def generate_pregunta_7_chart(request):
    # Obtener los datos de la pregunta_7
    pregunta_7_data = PreguntasCerradas.objects.values('pregunta_7').annotate(count=Count('pregunta_7')).order_by('pregunta_7')

    # Extraer las opciones de la pregunta_7 y sus frecuencias
    opciones = [item['pregunta_7'] for item in pregunta_7_data]
    frequencies = [item['count'] for item in pregunta_7_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('7. En relación con el día de su ingreso como empleado, usted nota mejoría en el desempeño de los empleados de la empresa.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 7.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo para identificar tendencias generales.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_7_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_7_chart.png')

    return chart_url






def generate_pregunta_8_chart(request): 
    # Obtener los datos de la pregunta_8
    pregunta_8_data = PreguntasCerradas.objects.values('pregunta_8').annotate(count=Count('pregunta_8')).order_by('pregunta_8')

    # Extraer las opciones de la pregunta_8 y sus frecuencias
    opciones = [item['pregunta_8'] for item in pregunta_8_data]
    frequencies = [item['count'] for item in pregunta_8_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con todas las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('8. La comunicación de trabajo, desde su jefe inmediato hacia usted es fácil.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 8.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_8_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_8_chart.png')

    return chart_url











def generate_pregunta_9_chart(request):
    # Obtener los datos de la pregunta_9
    pregunta_9_data = PreguntasCerradas.objects.values('pregunta_9').annotate(count=Count('pregunta_9')).order_by('pregunta_9')

    # Extraer las opciones de la pregunta_9 y sus frecuencias
    opciones = [item['pregunta_9'] for item in pregunta_9_data]
    frequencies = [item['count'] for item in pregunta_9_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('9. La comunicación de trabajo, desde usted hacia su jefe inmediato es fácil.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 9.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo para identificar tendencias generales sobre la comunicación con el jefe inmediato.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_9_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_9_chart.png')

    return chart_url










def generate_pregunta_10_chart(request):
    # Obtener los datos de la pregunta_10
    pregunta_10_data = PreguntasCerradas.objects.values('pregunta_10').annotate(count=Count('pregunta_10')).order_by('pregunta_10')

    # Extraer las opciones de la pregunta_10 y sus frecuencias
    opciones = [item['pregunta_10'] for item in pregunta_10_data]
    frequencies = [item['count'] for item in pregunta_10_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('10. La comunicación con los grupos de trabajo con los que usted necesita relacionarse es fácil.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 10.\n\n'
    description += 'Se incluyen sumatorias de respuestas de acuerdo y desacuerdo, permitiendo analizar tendencias sobre la comunicación con los grupos de trabajo necesarios.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_10_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_10_chart.png')

    return chart_url










def generate_pregunta_11_chart(request):
    # Obtener los datos de la pregunta_11
    pregunta_11_data = PreguntasCerradas.objects.values('pregunta_11').annotate(count=Count('pregunta_11')).order_by('pregunta_11')

    # Extraer las opciones de la pregunta_11 y sus frecuencias
    opciones = [item['pregunta_11'] for item in pregunta_11_data]
    frequencies = [item['count'] for item in pregunta_11_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar variables para las sumatorias
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos en el orden deseado
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('11. Como impresión general, usted considera que en la empresa los empleados conocen sus funciones.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 11.\n\n'
    description += 'Se incluyen sumatorias de respuestas de acuerdo y desacuerdo, facilitando un análisis sobre la percepción de los empleados respecto a su conocimiento de funciones.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_11_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_11_chart.png')

    return chart_url







def generate_pregunta_12_chart(request):
    # Obtener los datos de la pregunta_12
    pregunta_12_data = PreguntasCerradas.objects.values('pregunta_12').annotate(count=Count('pregunta_12')).order_by('pregunta_12')

    # Extraer las opciones de la pregunta_12 y sus frecuencias
    opciones = [item['pregunta_12'] for item in pregunta_12_data]
    frequencies = [item['count'] for item in pregunta_12_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar sumatorias
    sumatoria_excesivo = 0
    sumatoria_no_excesivo = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos ordenados
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('12. Normalmente la cantidad de trabajo que tiene su cargo es excesiva.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 12.\n\n'
    description += 'Se incluyen sumatorias para las respuestas de "excesivo" y "no excesivo" para una interpretación más clara de las tendencias.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_12_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_12_chart.png')

    return chart_url











def generate_pregunta_13_chart(request):
    # Obtener los datos de la pregunta_13
    pregunta_13_data = PreguntasCerradas.objects.values('pregunta_13').annotate(count=Count('pregunta_13')).order_by('pregunta_13')

    # Extraer las opciones de la pregunta_13 y sus frecuencias
    opciones = [item['pregunta_13'] for item in pregunta_13_data]
    frequencies = [item['count'] for item in pregunta_13_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar sumatorias para categorías
    sumatoria_alto_cumplimiento = 0
    sumatoria_bajo_cumplimiento = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias de las opciones obtenidas
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos ordenados
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('13. Las metas que se proponen en la empresa se cumplen.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 13.\n\n'
    description += 'Se incluyen sumatorias para las categorías de "alto cumplimiento" y "bajo cumplimiento" para una interpretación más clara.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_13_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_13_chart.png')

    return chart_url












def generate_pregunta_14_chart(request):
    # Obtener los datos de la pregunta_14
    pregunta_14_data = PreguntasCerradas.objects.values('pregunta_14').annotate(count=Count('pregunta_14')).order_by('pregunta_14')

    # Extraer las opciones de la pregunta_14 y sus frecuencias
    opciones = [item['pregunta_14'] for item in pregunta_14_data]
    frequencies = [item['count'] for item in pregunta_14_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar sumatorias para categorías clave
    sumatoria_alta_tendencia = 0
    sumatoria_baja_tendencia = 0

    # Calcular sumatorias por categorías significativas
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Muy frecuente", "Frecuente"]:
            sumatoria_alta_tendencia += count
        elif opcion in ["Poco frecuente", "Rara vez"]:
            sumatoria_baja_tendencia += count

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias reales
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos ordenados
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('14. Actualmente hay la tendencia en la empresa a desperdiciar insumos de trabajo.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 14.\n\n'
    description += 'Se incluyen sumatorias para las categorías "alta tendencia" y "baja tendencia" al desperdicio para una mejor interpretación.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_14_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_14_chart.png')

    return chart_url























def generate_pregunta_15_chart(request):
    # Obtener los datos de la pregunta_15
    pregunta_15_data = PreguntasCerradas.objects.values('pregunta_15').annotate(count=Count('pregunta_15')).order_by('pregunta_15')

    # Extraer las opciones de la pregunta_15 y sus frecuencias
    opciones = [item['pregunta_15'] for item in pregunta_15_data]
    frequencies = [item['count'] for item in pregunta_15_data]

    # Calcular el total de respuestas y los porcentajes
    total_responses = sum(frequencies)
    percentages = [(count / total_responses * 100) if total_responses > 0 else 0 for count in frequencies]

    # Inicializar sumatorias para categorías clave
    sumatoria_resolucion_positiva = 0
    sumatoria_resolucion_negativa = 0

    # Calcular las sumatorias basadas en las categorías
    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Rellenar el diccionario con las frecuencias reales
    for opcion, count in zip(opciones, frequencies):
        if opcion in categorias_ordenadas:
            categorias_ordenadas[opcion] = count

    # Extraer las opciones y frecuencias en el orden deseado
    opciones_ordenadas = list(categorias_ordenadas.keys())
    frequencies_ordenadas = list(categorias_ordenadas.values())
    percentages_ordenadas = [(freq / total_responses * 100) if total_responses > 0 else 0 for freq in frequencies_ordenadas]

    # Crear una nueva figura para la gráfica
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras con los datos ordenados
    bars = ax.bar(opciones_ordenadas, frequencies_ordenadas, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('15. En la empresa los problemas entre las personas se resuelven fácilmente.')

    # Mostrar las frecuencias y porcentajes encima de las barras
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages_ordenadas[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 15.\n\n'
    description += 'Se incluyen sumatorias para las categorías "Resolución positiva" y "Resolución negativa" para facilitar la interpretación de los resultados.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_15_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_15_chart.png')

    return chart_url












def generate_pregunta_16_chart(request):
    # Obtener los datos de la pregunta_16
    pregunta_16_data = PreguntasCerradas.objects.values('pregunta_16').annotate(count=Count('pregunta_16')).order_by('pregunta_16')

    # Extraer las opciones de la pregunta_16 y sus frecuencias
    opciones = [item['pregunta_16'] for item in pregunta_16_data]
    frequencies = [item['count'] for item in pregunta_16_data]

    # Calcular las sumatorias basadas en las categorías
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('16. La forma como está organizada la empresa, es fácil de entender.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 16.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_16_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_16_chart.png')

    return chart_url












def generate_pregunta_17_chart(request):
    # Obtener los datos de la pregunta_17
    pregunta_17_data = PreguntasCerradas.objects.values('pregunta_17').annotate(count=Count('pregunta_17')).order_by('pregunta_17')

    # Extraer las opciones de la pregunta_17 y sus frecuencias
    opciones = [item['pregunta_17'] for item in pregunta_17_data]
    frequencies = [item['count'] for item in pregunta_17_data]

    # Calcular las sumatorias basadas en las categorías
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('17. Las tareas son supervisadas excesivamente.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 17.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_17_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_17_chart.png')

    return chart_url












def generate_pregunta_18_chart(request):
    # Obtener los datos de la pregunta_18
    pregunta_18_data = PreguntasCerradas.objects.values('pregunta_18').annotate(count=Count('pregunta_18')).order_by('pregunta_18')

    # Extraer las opciones de la pregunta_18 y sus frecuencias
    opciones = [item['pregunta_18'] for item in pregunta_18_data]
    frequencies = [item['count'] for item in pregunta_18_data]

    # Calcular las sumatorias basadas en las categorías
    sumatoria_acuerdos = 0
    sumatoria_desacuerdos = 0

    for opcion, count in zip(opciones, frequencies):
        if opcion in ["Totalmente de acuerdo", "Medianamente de acuerdo"]:
            sumatoria_acuerdos += count
        elif opcion in ["Medianamente en desacuerdo", "Totalmente en desacuerdo"]:
            sumatoria_desacuerdos += count

    # Crear un diccionario con las categorías en el orden deseado
    categorias_ordenadas = {
        "Totalmente de acuerdo": 0,
        "Medianamente de acuerdo": 0,
        "Sumatoria acuerdos": sumatoria_acuerdos,
        "Medianamente en desacuerdo": 0,
        "Totalmente en desacuerdo": 0,
        "Sumatoria de desacuerdos": sumatoria_desacuerdos
    }

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('18. En la empresa las relaciones entre las personas son cordiales.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 18.\n\n'
    description += 'Incluye sumatorias de respuestas en las categorías de acuerdo y desacuerdo.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_18_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_18_chart.png')

    return chart_url






















def generate_pregunta_19_chart(request):
    # Obtener los datos de la pregunta_19
    pregunta_19_data = PreguntasCerradas.objects.values('pregunta_19').annotate(count=Count('pregunta_19')).order_by('pregunta_19')

    # Extraer las opciones de la pregunta_19 y sus frecuencias
    opciones = [item['pregunta_19'] for item in pregunta_19_data]
    frequencies = [item['count'] for item in pregunta_19_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('19. Al interior de la empresa permanentemente hay conflictos.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 19.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_19_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_19_chart.png')

    return chart_url






















def generate_pregunta_20_chart(request):
    # Obtener los datos de la pregunta_20
    pregunta_20_data = PreguntasCerradas.objects.values('pregunta_20').annotate(count=Count('pregunta_20')).order_by('pregunta_20')

    # Extraer las opciones de la pregunta_20 y sus frecuencias
    opciones = [item['pregunta_20'] for item in pregunta_20_data]
    frequencies = [item['count'] for item in pregunta_20_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('20. Los empleados son solidarios entre sí.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 20.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_20_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_20_chart.png')

    return chart_url
















def generate_pregunta_21_chart(request):
    # Obtener los datos de la pregunta_21
    pregunta_21_data = PreguntasCerradas.objects.values('pregunta_21').annotate(count=Count('pregunta_21')).order_by('pregunta_21')

    # Extraer las opciones de la pregunta_21 y sus frecuencias
    opciones = [item['pregunta_21'] for item in pregunta_21_data]
    frequencies = [item['count'] for item in pregunta_21_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('21. Las personas en la empresa son tolerantes.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 21.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_21_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_21_chart.png')

    return chart_url











def generate_pregunta_22_chart(request):
    # Obtener los datos de la pregunta_22
    pregunta_22_data = PreguntasCerradas.objects.values('pregunta_22').annotate(count=Count('pregunta_22')).order_by('pregunta_22')

    # Extraer las opciones de la pregunta_22 y sus frecuencias
    opciones = [item['pregunta_22'] for item in pregunta_22_data]
    frequencies = [item['count'] for item in pregunta_22_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('22. Los empleados en la empresa se actualizan en los temas que necesita la organización.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 22.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_22_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_22_chart.png')

    return chart_url








def generate_pregunta_23_chart(request):
    # Obtener los datos de la pregunta_23
    pregunta_23_data = PreguntasCerradas.objects.values('pregunta_23').annotate(count=Count('pregunta_23')).order_by('pregunta_23')

    # Extraer las opciones de la pregunta_23 y sus frecuencias
    opciones = [item['pregunta_23'] for item in pregunta_23_data]
    frequencies = [item['count'] for item in pregunta_23_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('23. La empresa apoya la autonomía de sus empleados.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 23.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_23_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_23_chart.png')

    return chart_url











def generate_pregunta_24_chart(request):
    # Obtener los datos de la pregunta_24
    pregunta_24_data = PreguntasCerradas.objects.values('pregunta_24').annotate(count=Count('pregunta_24')).order_by('pregunta_24')

    # Extraer las opciones de la pregunta_24 y sus frecuencias
    opciones = [item['pregunta_24'] for item in pregunta_24_data]
    frequencies = [item['count'] for item in pregunta_24_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('24. La empresa apoya el desarrollo de carrera (ascensos) de sus empleados.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 24.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_24_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_24_chart.png')

    return chart_url













def generate_pregunta_25_chart(request):
    # Obtener los datos de la pregunta_25
    pregunta_25_data = PreguntasCerradas.objects.values('pregunta_25').annotate(count=Count('pregunta_25')).order_by('pregunta_25')

    # Extraer las opciones de la pregunta_25 y sus frecuencias
    opciones = [item['pregunta_25'] for item in pregunta_25_data]
    frequencies = [item['count'] for item in pregunta_25_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('25. La empresa apoya las sugerencias de los empleados para innovar (en procesos, productos, servicios, etc.).')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 25.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_25_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_25_chart.png')

    return chart_url















def generate_pregunta_26_chart(request):
    # Obtener los datos de la pregunta_26
    pregunta_26_data = PreguntasCerradas.objects.values('pregunta_26').annotate(count=Count('pregunta_26')).order_by('pregunta_26')

    # Extraer las opciones de la pregunta_26 y sus frecuencias
    opciones = [item['pregunta_26'] for item in pregunta_26_data]
    frequencies = [item['count'] for item in pregunta_26_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('26. En la empresa la libertad de expresión se respeta.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 26.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_26_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_26_chart.png')

    return chart_url

















def generate_pregunta_27_chart(request):
    # Obtener los datos de la pregunta_27
    pregunta_27_data = PreguntasCerradas.objects.values('pregunta_27').annotate(count=Count('pregunta_27')).order_by('pregunta_27')

    # Extraer las opciones de la pregunta_27 y sus frecuencias
    opciones = [item['pregunta_27'] for item in pregunta_27_data]
    frequencies = [item['count'] for item in pregunta_27_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('27. En general, usted se siente bien trabajando en la dependencia actual.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 27.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_27_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_27_chart.png')

    return chart_url














def generate_pregunta_28_chart(request):
    # Obtener los datos de la pregunta_28
    pregunta_28_data = PreguntasCerradas.objects.values('pregunta_28').annotate(count=Count('pregunta_28')).order_by('pregunta_28')

    # Extraer las opciones de la pregunta_28 y sus frecuencias
    opciones = [item['pregunta_28'] for item in pregunta_28_data]
    frequencies = [item['count'] for item in pregunta_28_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('28. Usted se siente bien trabajando en la empresa, en general.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 28.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_28_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_28_chart.png')

    return chart_url

















def generate_pregunta_29_chart(request):
    # Obtener los datos de la pregunta_29
    pregunta_29_data = PreguntasCerradas.objects.values('pregunta_29').annotate(count=Count('pregunta_29')).order_by('pregunta_29')

    # Extraer las opciones de la pregunta_29 y sus frecuencias
    opciones = [item['pregunta_29'] for item in pregunta_29_data]
    frequencies = [item['count'] for item in pregunta_29_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('29. En general, la empresa paga los salarios que cada quien se merece.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 29.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_29_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_29_chart.png')

    return chart_url














def generate_pregunta_30_chart(request):
    # Obtener los datos de la pregunta_30
    pregunta_30_data = PreguntasCerradas.objects.values('pregunta_30').annotate(count=Count('pregunta_30')).order_by('pregunta_30')

    # Extraer las opciones de la pregunta_30 y sus frecuencias
    opciones = [item['pregunta_30'] for item in pregunta_30_data]
    frequencies = [item['count'] for item in pregunta_30_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('30. Frente a entidades parecidas, la empresa es fuerte.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 30.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_30_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_30_chart.png')

    return chart_url
















def generate_pregunta_31_chart(request):
    # Obtener los datos de la pregunta_31
    pregunta_31_data = PreguntasCerradas.objects.values('pregunta_31').annotate(count=Count('pregunta_31')).order_by('pregunta_31')

    # Extraer las opciones de la pregunta_31 y sus frecuencias
    opciones = [item['pregunta_31'] for item in pregunta_31_data]
    frequencies = [item['count'] for item in pregunta_31_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('31. Esta organización le cumple a sus clientes.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 31.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_31_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_31_chart.png')

    return chart_url


















def generate_pregunta_32_chart(request):
    # Obtener los datos de la pregunta_32
    pregunta_32_data = PreguntasCerradas.objects.values('pregunta_32').annotate(count=Count('pregunta_32')).order_by('pregunta_32')

    # Extraer las opciones de la pregunta_32 y sus frecuencias
    opciones = [item['pregunta_32'] for item in pregunta_32_data]
    frequencies = [item['count'] for item in pregunta_32_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('32. Si usted recibiera una oferta de trabajo de otra organización se iría, siendo las condiciones de la otra las mismas.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 32.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_32_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_32_chart.png')

    return chart_url

















def generate_pregunta_33_chart(request):
    # Obtener los datos de la pregunta_33
    pregunta_33_data = PreguntasCerradas.objects.values('pregunta_33').annotate(count=Count('pregunta_33')).order_by('pregunta_33')

    # Extraer las opciones de la pregunta_33 y sus frecuencias
    opciones = [item['pregunta_33'] for item in pregunta_33_data]
    frequencies = [item['count'] for item in pregunta_33_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('33. Si usted recibiera una oferta de trabajo de otra organización se iría, siendo las condiciones de la otra mucho mejores.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 33.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_33_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_33_chart.png')

    return chart_url

















def generate_pregunta_34_chart(request):
    # Obtener los datos de la pregunta_34
    pregunta_34_data = PreguntasCerradas.objects.values('pregunta_34').annotate(count=Count('pregunta_34')).order_by('pregunta_34')

    # Extraer las opciones de la pregunta_34 y sus frecuencias
    opciones = [item['pregunta_34'] for item in pregunta_34_data]
    frequencies = [item['count'] for item in pregunta_34_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('34. Las condiciones de su sitio de trabajo son adecuadas para desempeñarse bien.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 34.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_34_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_34_chart.png')

    return chart_url





















def generate_pregunta_35_chart(request):
    # Obtener los datos de la pregunta_35
    pregunta_35_data = PreguntasCerradas.objects.values('pregunta_35').annotate(count=Count('pregunta_35')).order_by('pregunta_35')

    # Extraer las opciones de la pregunta_35 y sus frecuencias
    opciones = [item['pregunta_35'] for item in pregunta_35_data]
    frequencies = [item['count'] for item in pregunta_35_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('35. Es notable la presencia de grupos cerrados en los cuales se refugian sus integrantes.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 35.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_35_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_35_chart.png')

    return chart_url


















def generate_pregunta_36_chart(request):
    # Obtener los datos de la pregunta_36
    pregunta_36_data = PreguntasCerradas.objects.values('pregunta_36').annotate(count=Count('pregunta_36')).order_by('pregunta_36')

    # Extraer las opciones de la pregunta_36 y sus frecuencias
    opciones = [item['pregunta_36'] for item in pregunta_36_data]
    frequencies = [item['count'] for item in pregunta_36_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('36. La cantidad de tareas que tiene su cargo es mayor a la de otros cargos que se le parecen.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 36.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_36_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_36_chart.png')

    return chart_url






















def generate_pregunta_37_chart(request):
    # Obtener los datos de la pregunta_37
    pregunta_37_data = PreguntasCerradas.objects.values('pregunta_37').annotate(count=Count('pregunta_37')).order_by('pregunta_37')

    # Extraer las opciones de la pregunta_37 y sus frecuencias
    opciones = [item['pregunta_37'] for item in pregunta_37_data]
    frequencies = [item['count'] for item in pregunta_37_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('37. Su jefe sabe cómo hacer el trabajo de sus subalternos.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 37.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_37_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_37_chart.png')

    return chart_url



















def generate_pregunta_38_chart(request):
    # Obtener los datos de la pregunta_38
    pregunta_38_data = PreguntasCerradas.objects.values('pregunta_38').annotate(count=Count('pregunta_38')).order_by('pregunta_38')

    # Extraer las opciones de la pregunta_38 y sus frecuencias
    opciones = [item['pregunta_38'] for item in pregunta_38_data]
    frequencies = [item['count'] for item in pregunta_38_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('38. Su jefe sabe cómo premiar a sus subalternos.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 38.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_38_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_38_chart.png')

    return chart_url






















def generate_pregunta_39_chart(request):
    # Obtener los datos de la pregunta_39
    pregunta_39_data = PreguntasCerradas.objects.values('pregunta_39').annotate(count=Count('pregunta_39')).order_by('pregunta_39')

    # Extraer las opciones de la pregunta_39 y sus frecuencias
    opciones = [item['pregunta_39'] for item in pregunta_39_data]
    frequencies = [item['count'] for item in pregunta_39_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('39. Su jefe sabe cómo sancionar a sus subalternos.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 39.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_39_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_39_chart.png')

    return chart_url


















def generate_pregunta_40_chart(request):
    # Obtener los datos de la pregunta_40
    pregunta_40_data = PreguntasCerradas.objects.values('pregunta_40').annotate(count=Count('pregunta_40')).order_by('pregunta_40')

    # Extraer las opciones de la pregunta_40 y sus frecuencias
    opciones = [item['pregunta_40'] for item in pregunta_40_data]
    frequencies = [item['count'] for item in pregunta_40_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('40. Su puesto de trabajo tiene variedad en la forma de ejecutar las tareas.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 40.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_40_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_40_chart.png')

    return chart_url


















def generate_pregunta_41_chart(request):
    # Obtener los datos de la pregunta_41
    pregunta_41_data = PreguntasCerradas.objects.values('pregunta_41').annotate(count=Count('pregunta_41')).order_by('pregunta_41')

    # Extraer las opciones de la pregunta_41 y sus frecuencias
    opciones = [item['pregunta_41'] for item in pregunta_41_data]
    frequencies = [item['count'] for item in pregunta_41_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('41. Usted encuentra congruencia entre lo que busca en su vida laboral y lo que le ofrece su puesto de trabajo.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 41.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
    ax.text(1.2, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_41_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_41_chart.png')

    return chart_url



















# Obtener los datos de la pregunta_42
def procesar_respuestas3(request):
    # Usamos el modelo generativo de la IA 
    modelo = genai.GenerativeModel('gemini-pro')
    # Configuramos la API KEY 
    GOOGLE_API_KEY='AIzaSyCTtp7jYZ0S7zmxa8_o0slr3M2BpAPICJs'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Importamos las respuestas de la base de datos
    respuestas_situacion_1 = PreguntaAbierta.objects.values_list('pregunta_42_situacion_1', flat=True)
    respuestas_situacion_2 = PreguntaAbierta.objects.values_list('pregunta_42_situacion_2', flat=True)
    respuestas = list(respuestas_situacion_1) + list(respuestas_situacion_2)

    # Convertimos las respuestas en un solo texto
    texto_respuestas = '|'.join(respuestas)

# Definimos el prompt
    prompt = ('genera 10 categorias, siempre 10, basadas en los textos suministrados teniendo en cuenta que los titulos de las categorias deben estar relacionados a lo que es una organizacion y el contexto que es:'
              'situaciones, anécdotas, historias internas o algo típico, que refleje lo que distingue la cultura de esta organización frente a las que se le parecen. Algo que permita decir: "esto solo pasa aquí".'
              'usa todos los textos exceptuando los textos que solo dicen "Ninguna, .., N. A, ...,", por nada los vayas a usar para las categorias.'
              'haz un conteo de todos los textos, ten en cuenta que estan separados por "|", ame un conteo y un porcentaje para cada categoria.'
              'los datos siempre seran entregados en el siguiente formato, como si fuera una tabla: | Categoria | Conteo | Porcentaje | , Siempre se va a usar ese formato, siempre.')


    # Generamos la respuesta basada en el prompt y el texto de las respuestas
    respuesta = modelo.generate_content(prompt + texto_respuestas)
    respuesta = respuesta.text

    # Rebajamos el tamaño de la respuesta de la IA 
    respuestaaaas = respuesta.replace('**', '|')
    respuestaaaas = respuesta.replace('*', '|')
    respuestaaaas = respuesta.replace('| |', '|')
    print (respuestaaaas)

    # Extraer las categorías, conteos y porcentajes
    categorias = re.findall(r'\| (.+?) \| (\d+) \| (\d+(?:[,.]\d+)?)% \|', respuestaaaas)
    print (categorias)

    # Convertir porcentajes a números
    conteos = [int(c[1]) for c in categorias]
    porcentajes = [float(c[2].replace(',', '.')) for c in categorias]

    # Convertir las categorías a una lista
    categorias = [c[0] for c in categorias]
 

    # Crear figura
    fig = Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    # Crear gráfica de barras
    bars = ax.bar(categorias, conteos, color='lightgreen')

    # Añadir etiquetas y título
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Conteo')
    ax.set_title('Situaciones, anécdotas, historias internas o algo típico')
    ax.set_xticklabels(categorias, rotation=45, ha='right')

    # Ajustar márgenes
    fig.subplots_adjust(bottom=0.4, top=0.9) 

    # Mostrar porcentajes con decimales en las barras
    for bar, porcentaje in zip(bars, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{porcentaje:.2f}%", ha='center', fontsize=7)

    # Ajustar espacio entre etiquetas del eje x
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Guardar la imagen de la gráfica de barras en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path_bar = os.path.join(chart_dir, 'pregunta_42_chart_bar3.png')
    fig.savefig(chart_path_bar, format='png')

    # Obtener la URL de la imagen de la gráfica de barras
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_42_chart_bar3.png')

    return chart_url

















def generate_pregunta_43_opcion_1_chart(request):
    # Obtener los datos de la pregunta 43, opción 1
    pregunta_43_opcion_1_data = PreguntaImportancia.objects.values('pregunta_43_opcion_1').annotate(count=Count('pregunta_43_opcion_1')).order_by('pregunta_43_opcion_1')

    # Extraer las respuestas y sus frecuencias
    opciones = [item['pregunta_43_opcion_1'] for item in pregunta_43_opcion_1_data]
    frequencies = [item['count'] for item in pregunta_43_opcion_1_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Importancia de la razón por la cual trabaja aquí: "Me siento bien con mis compañeros"')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 43, opción 1.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.\n\n'
    description += '1) La menos importante\n2) Medianamente importante\n3) La más importante'
    ax.text(1.05, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_43_opcion_1_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_43_opcion_1_chart.png')

    return chart_url










def generate_pregunta_43_opcion_2_chart(request):
    # Obtener los datos de la pregunta 43, opción 2
    pregunta_43_opcion_2_data = PreguntaImportancia.objects.values('pregunta_43_opcion_2').annotate(count=Count('pregunta_43_opcion_2')).order_by('pregunta_43_opcion_2')

    # Extraer las respuestas y sus frecuencias
    opciones = [item['pregunta_43_opcion_2'] for item in pregunta_43_opcion_2_data]
    frequencies = [item['count'] for item in pregunta_43_opcion_2_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Importancia de la razón por la cual trabaja aquí: "Puedo ayudar a organizar los equipos de trabajo"')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 43, opción 2.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.\n\n'
    description += '1) La menos importante\n2) Medianamente importante\n3) La más importante'
    ax.text(1.05, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_43_opcion_2_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_43_opcion_2_chart.png')

    return chart_url








def generate_pregunta_43_opcion_3_chart(request):
    # Obtener los datos de la pregunta 43, opción 3
    pregunta_43_opcion_3_data = PreguntaImportancia.objects.values('pregunta_43_opcion_3').annotate(count=Count('pregunta_43_opcion_3')).order_by('pregunta_43_opcion_3')

    # Extraer las respuestas y sus frecuencias
    opciones = [item['pregunta_43_opcion_3'] for item in pregunta_43_opcion_3_data]
    frequencies = [item['count'] for item in pregunta_43_opcion_3_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Importancia de la razón por la cual trabaja aquí: "Puedo avanzar hacia las metas que me he propuesto en la vida"')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 43, opción 3.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.\n\n'
    description += '1) La menos importante\n2) Medianamente importante\n3) La más importante'
    ax.text(1.05, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_43_opcion_3_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_43_opcion_3_chart.png')

    return chart_url



def generate_pregunta_43_chart(request):
    # Obtener los datos de la pregunta 43 para las tres opciones
    pregunta_43_opcion_1_data = PreguntaImportancia.objects.values('pregunta_43_opcion_1').annotate(count=Count('pregunta_43_opcion_1')).order_by('pregunta_43_opcion_1')
    pregunta_43_opcion_2_data = PreguntaImportancia.objects.values('pregunta_43_opcion_2').annotate(count=Count('pregunta_43_opcion_2')).order_by('pregunta_43_opcion_2')
    pregunta_43_opcion_3_data = PreguntaImportancia.objects.values('pregunta_43_opcion_3').annotate(count=Count('pregunta_43_opcion_3')).order_by('pregunta_43_opcion_3')

    # Extraer las respuestas y sus frecuencias para cada opción
    opciones_1 = [item['pregunta_43_opcion_1'] for item in pregunta_43_opcion_1_data]
    opciones_2 = [item['pregunta_43_opcion_2'] for item in pregunta_43_opcion_2_data]
    opciones_3 = [item['pregunta_43_opcion_3'] for item in pregunta_43_opcion_3_data]
    frequencies_1 = [item['count'] for item in pregunta_43_opcion_1_data]
    frequencies_2 = [item['count'] for item in pregunta_43_opcion_2_data]
    frequencies_3 = [item['count'] for item in pregunta_43_opcion_3_data]

    # Calcular porcentajes para cada opción
    total_responses_1 = sum(frequencies_1)
    total_responses_2 = sum(frequencies_2)
    total_responses_3 = sum(frequencies_3)
    percentages_1 = [count / total_responses_1 * 100 for count in frequencies_1]
    percentages_2 = [count / total_responses_2 * 100 for count in frequencies_2]
    percentages_3 = [count / total_responses_3 * 100 for count in frequencies_3]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.2

    # Crear la gráfica de barras
    x = range(len(opciones_1))
    ax.bar(x, frequencies_1, width=bar_width, label='Me siento bien con mis compañeros', color='#1f77b4')
    ax.bar([i + bar_width for i in x], frequencies_2, width=bar_width, label='Puedo ayudar a organizar los equipos de trabajo', color='#ff7f0e')
    ax.bar([i + bar_width * 2 for i in x], frequencies_3, width=bar_width, label='Puedo avanzar hacia las metas que me he propuesto en la vida', color='#808080')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Respuestas a la pregunta 43')
    ax.set_xticks([i + bar_width for i in x])
    ax.set_xticklabels(['Relaciones Interpersonales', 'Liderazgo', 'Logros Personales'])
    ax.legend()

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(ax.patches):
        height = rect.get_height()
        if i < len(opciones_1):
            ax.annotate('{} ({:.1f}%)'.format(height, percentages_1[i]),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # Desplazamiento vertical del texto
                        textcoords="offset points",
                        ha='center', va='bottom')
        elif i < len(opciones_1) * 2:
            ax.annotate('{} ({:.1f}%)'.format(height, percentages_2[i - len(opciones_1)]),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # Desplazamiento vertical del texto
                        textcoords="offset points",
                        ha='center', va='bottom')
        else:
            ax.annotate('{} ({:.1f}%)'.format(height, percentages_3[i - len(opciones_1) * 2]),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # Desplazamiento vertical del texto
                        textcoords="offset points",
                        ha='center', va='bottom')

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_43_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_43_chart.png')

    return chart_url










def generate_pregunta_44_opcion_1_chart(request):
    # Obtener los datos de la pregunta 44, opción 1
    pregunta_44_opcion_1_data = PreguntaImportancia.objects.values('pregunta_44_opcion_1').annotate(count=Count('pregunta_44_opcion_1')).order_by('pregunta_44_opcion_1')

    # Extraer las respuestas y sus frecuencias
    opciones = [item['pregunta_44_opcion_1'] for item in pregunta_44_opcion_1_data]
    frequencies = [item['count'] for item in pregunta_44_opcion_1_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Fuentes de poder tiene mayor influencia en esta entidad: "Las directivas"')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 44, opción 1.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.\n\n'
    description += '1) La menos importante\n2) Medianamente importante\n3) La más importante'
    ax.text(1.05, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_44_opcion_1_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_44_opcion_1_chart.png')

    return chart_url









def generate_pregunta_44_opcion_2_chart(request):
    # Obtener los datos de la pregunta 44, opción 2
    pregunta_44_opcion_2_data = PreguntaImportancia.objects.values('pregunta_44_opcion_2').annotate(count=Count('pregunta_44_opcion_2')).order_by('pregunta_44_opcion_2')

    # Extraer las respuestas y sus frecuencias
    opciones = [item['pregunta_44_opcion_2'] for item in pregunta_44_opcion_2_data]
    frequencies = [item['count'] for item in pregunta_44_opcion_2_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Fuentes de poder tiene mayor influencia en esta entidad: "Los empleados"')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 44, opción 2.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.\n\n'
    description += '1) La menos importante\n2) Medianamente importante\n3) La más importante'
    ax.text(1.05, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_44_opcion_2_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_44_opcion_2_chart.png')

    return chart_url









def generate_pregunta_44_opcion_3_chart(request):
    # Obtener los datos de la pregunta 44, opción 3
    pregunta_44_opcion_3_data = PreguntaImportancia.objects.values('pregunta_44_opcion_3').annotate(count=Count('pregunta_44_opcion_3')).order_by('pregunta_44_opcion_3')

    # Extraer las respuestas y sus frecuencias
    opciones = [item['pregunta_44_opcion_3'] for item in pregunta_44_opcion_3_data]
    frequencies = [item['count'] for item in pregunta_44_opcion_3_data]

    # Calcular porcentajes
    total_responses = sum(frequencies)
    percentages = [count / total_responses * 100 for count in frequencies]

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Fuentes de poder tiene mayor influencia en esta entidad: "Factores externos a la entidad"')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 44, opción 3.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.\n\n'
    description += '1) La menos importante\n2) Medianamente importante\n3) La más importante'
    ax.text(1.05, 0.5, description, transform=ax.transAxes, fontsize=12,
            va='center', ha='left', wrap=True, bbox=dict(facecolor='none', edgecolor='black', pad=20))

    # Ajustar automáticamente los parámetros de la figura
    fig.tight_layout()

    # Guardar la imagen en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_44_opcion_3_chart.png')
    fig.savefig(chart_path)

    # Obtener la URL de la imagen
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_44_opcion_3_chart.png')

    return chart_url

















# Obtener los datos de la pregunta_44 abierta 
def generate_pregunta_44_opcion_4_chart(request):
    # Usamos el modelo generativo de la IA 
    modelo = genai.GenerativeModel('gemini-pro')
    # Configuramos la API KEY 
    GOOGLE_API_KEY='AIzaSyCTtp7jYZ0S7zmxa8_o0slr3M2BpAPICJs'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Importamos las respuestas de la base de datos
    pregunta_44_opcion_4 = PreguntaImportancia.objects.values_list('pregunta_44_opcion_4', flat=True)
    respuestas = list(pregunta_44_opcion_4) + list(pregunta_44_opcion_4)

    # Convertimos las respuestas en un solo texto
    texto_respuestas = '|'.join(respuestas)

# Definimos el prompt
    prompt = ('genera 3 categorias, basadas en los textos suministrados teniendo en cuenta que los titulos de las categorias deben estar relacionados a lo que es una organizacion y el contexto que es:'
              'Fuentes de poder con influencia en esta entidad y que son Factores externos a la entidad.'
              'usa todos los textos exceptuando los textos que solo dicen "Ninguna, .., N. A, ...,", por nada los vayas a usar para las categorias.'
              'Usa solo los textos para crear las categorias, el contexto es solo para darte una idea del tema al cual deben hacer referencia las categorias'
              'para crear las categorias, usa terminos en relacion con una jerga profesional en la psicologia organizacional'
              'haz un conteo de todos los textos, ten en cuenta que estan separados por "|", dame un conteo y un porcentaje para cada categoria.'
              'los datos siempre seran entregados en el siguiente formato, como si fuera una tabla: | Categoria | Conteo | Porcentaje | , SIEMPRE se va a usar ese formato sin alteraciones, siempre.'
              'no olvide el formato de entrega')

    # Generamos la respuesta basada en el prompt y el texto de las respuestas
    respuesta = modelo.generate_content(prompt + texto_respuestas)
    respuesta = respuesta.text

    # Rebajamos el tamaño de la respuesta de la IA 
    respuestaaaas = respuesta.replace('**', '|')
    respuestaaaas = respuesta.replace('*', '|')
    respuestaaaas = respuesta.replace('| |', '|')
    print (respuestaaaas)

    # Extraer las categorías, conteos y porcentajes
    categorias = re.findall(r'\| (.+?) \| (\d+) \| (\d+(?:[,.]\d+)?)% \|', respuestaaaas)
    print (categorias)


    # Convertir porcentajes a números
    conteos = [int(c[1]) for c in categorias]
    porcentajes = [float(c[2].replace(',', '.')) for c in categorias]

    # Convertir las categorías a una lista
    categorias = [c[0] for c in categorias]
 

    # Crear figura
    fig = Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    # Crear gráfica de barras
    bars = ax.bar(categorias, conteos, color='lightgreen')

    # Añadir etiquetas y título
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Conteo')
    ax.set_title('Textos por Categoría')
    ax.set_xticklabels(categorias, rotation=45, ha='right')

    # Ajustar márgenes
    fig.subplots_adjust(bottom=0.4, top=0.9) 

    # Mostrar porcentajes con decimales en las barras
    for bar, porcentaje in zip(bars, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{porcentaje:.2f}%", ha='center', fontsize=7)

    # Ajustar espacio entre etiquetas del eje x
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Guardar la imagen de la gráfica de barras en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path_bar = os.path.join(chart_dir, 'pregunta_44_opcion_4_chart.png')
    fig.savefig(chart_path_bar, format='png')

    # Obtener la URL de la imagen de la gráfica de barras
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_44_opcion_4_chart.png')

    return chart_url








def generate_pregunta_44_chart(request):
    # Definir las categorías y los niveles de influencia
    categorias = ["Directivas", "Empleados", "Factores externos a la entidad"]
    niveles_influencia = ["Menor influencia", "Mediana influencia", "Mayor influencia"]

    # Inicialización de conteos de influencias para cada categoría
    conteos = {
        "Directivas": [0, 0, 0],  # [Menor influencia, Mediana influencia, Mayor influencia]
        "Empleados": [0, 0, 0],
        "Factores externos a la entidad": [0, 0, 0]
    }

    # Obtener los datos y contar respuestas por nivel de influencia para cada categoría
    datos_opciones = {
        "Directivas": "pregunta_44_opcion_1",
        "Empleados": "pregunta_44_opcion_2",
        "Factores externos a la entidad": "pregunta_44_opcion_3"
    }

    for categoria, campo in datos_opciones.items():
        datos = PreguntaImportancia.objects.values(campo).annotate(count=Count(campo))
        
        for item in datos:
            valor = item[campo]
            if valor in [1, 2, 3]:  # Mapear 1 -> Menor, 2 -> Mediana, 3 -> Mayor
                conteos[categoria][valor - 1] = item['count']

    # Calcular porcentajes y conteos para cada nivel de influencia
    porcentajes = {categoria: [] for categoria in categorias}
    conteos_totales = {categoria: [] for categoria in categorias}

    for categoria in categorias:
        total_respuestas = sum(conteos[categoria])
        for idx in range(3):
            porcentaje = (conteos[categoria][idx] / total_respuestas * 100) if total_respuestas > 0 else 0
            porcentajes[categoria].append(porcentaje)
            conteos_totales[categoria].append(conteos[categoria][idx])

    # Preparar los datos para la gráfica
    menor_influencia = [porcentajes["Directivas"][0], porcentajes["Empleados"][0], porcentajes["Factores externos a la entidad"][0]]
    mediana_influencia = [porcentajes["Directivas"][1], porcentajes["Empleados"][1], porcentajes["Factores externos a la entidad"][1]]
    mayor_influencia = [porcentajes["Directivas"][2], porcentajes["Empleados"][2], porcentajes["Factores externos a la entidad"][2]]

    menor_conteo = [conteos_totales["Directivas"][0], conteos_totales["Empleados"][0], conteos_totales["Factores externos a la entidad"][0]]
    mediana_conteo = [conteos_totales["Directivas"][1], conteos_totales["Empleados"][1], conteos_totales["Factores externos a la entidad"][1]]
    mayor_conteo = [conteos_totales["Directivas"][2], conteos_totales["Empleados"][2], conteos_totales["Factores externos a la entidad"][2]]

    # Crear el gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.2
    x = np.arange(len(categorias))  # Posiciones de las categorías principales

    # Graficar barras para cada nivel de influencia dentro de cada localización
    bars_menor = ax.bar(x - bar_width, menor_influencia, width=bar_width, color='#1f77b4', label='Menor influencia')
    bars_mediana = ax.bar(x, mediana_influencia, width=bar_width, color='#ff7f0e', label='Mediana influencia')
    bars_mayor = ax.bar(x + bar_width, mayor_influencia, width=bar_width, color='#7f7f7f', label='Mayor influencia')

    # Etiquetas y título
    ax.set_xlabel('Localización')
    ax.set_ylabel('Porcentaje (%)')
    ax.set_title('Distribución de influencia según la localización del poder')
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend(title='Nivel de Influencia')

    # Anotaciones para porcentaje y conteo en cada barra
    for bars, counts, percentages in zip([bars_menor, bars_mediana, bars_mayor], [menor_conteo, mediana_conteo, mayor_conteo], [menor_influencia, mediana_influencia, mayor_influencia]):
        for bar, count, percentage in zip(bars, counts, percentages):
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{percentage:.2f}%\n({count})',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom')

    fig.tight_layout()

    # Guardar la imagen
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'pregunta_44_chart.png')
    fig.savefig(chart_path)

    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_44_chart.png')
    return chart_url



































# Obtener los datos de la pregunta_45
def generate_pregunta_45_chart(request):
    # Usamos el modelo generativo de la IA 
    modelo = genai.GenerativeModel('gemini-pro')
    # Configuramos la API KEY 
    GOOGLE_API_KEY='AIzaSyCTtp7jYZ0S7zmxa8_o0slr3M2BpAPICJs'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Importamos las respuestas de la base de datos
    defecto_1 = PreguntaAbiertaDefectos.objects.values_list('defecto_1', flat=True)
    defecto_2 = PreguntaAbiertaDefectos.objects.values_list('defecto_2', flat=True)
    defecto_3 = PreguntaAbiertaDefectos.objects.values_list('defecto_3', flat=True)
    respuestas = list(defecto_1) + list(defecto_2) + list(defecto_3) 

    # Convertimos las respuestas en un solo texto
    texto_respuestas = '|'.join(respuestas)

# Definimos el prompt
    prompt = ('genera 10 categorias, siempre 10, basadas en los textos suministrados teniendo en cuenta que los titulos de las categorias deben estar relacionados a lo que es una organizacion y el contexto que es:'
              'Mencione defectos de esta entidad.'
              'usa todos los textos exceptuando los textos que solo dicen "Ninguna, .., N. A, ...,", por nada los vayas a usar para las categorias.'
              'para crear las categorias, usa terminos en relacion con una jerga profesional en la psicologia organizacional.'
              'haz un conteo de todos los textos, ten en cuenta que estan separados por "|", dame un conteo y un porcentaje para cada categoria. Si hay categorias con 0%, no crearlas, es innecesario.'
              'los datos siempre seran entregados en el siguiente formato, como si fuera una tabla: | Categoria | Conteo | Porcentaje | , SIEMPRE se va a usar ese formato sin alteraciones, siempre.'
              'no es necesario entregar más informacion ademas de las categorias el conteo y el porcentaje en el formato solicitado.')


    # Generamos la respuesta basada en el prompt y el texto de las respuestas
    respuesta = modelo.generate_content(prompt + texto_respuestas)
    respuesta = respuesta.text

    # Rebajamos el tamaño de la respuesta de la IA 
    respuestaaaas = respuesta.replace('**', '|')
    respuestaaaas = respuesta.replace('*', '|')
    respuestaaaas = respuesta.replace('| |', '|')
    print (respuestaaaas)

    # Extraer las categorías, conteos y porcentajes
    categorias = re.findall(r'\| (.+?) \| (\d+) \| (\d+(?:[,.]\d+)?)% \|', respuestaaaas)
    print (categorias)

    # Convertir porcentajes a números
    conteos = [int(c[1]) for c in categorias]
    porcentajes = [float(c[2].replace(',', '.')) for c in categorias]

    # Convertir las categorías a una lista
    categorias = [c[0] for c in categorias]
 

    # Crear figura
    fig = Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    # Crear gráfica de barras
    bars = ax.bar(categorias, conteos, color='lightgreen')

    # Añadir etiquetas y título
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Conteo')
    ax.set_title('45. Defectos de la entidad')
    ax.set_xticklabels(categorias, rotation=45, ha='right')

    # Ajustar márgenes
    fig.subplots_adjust(bottom=0.4, top=0.9) 

    # Mostrar porcentajes con decimales en las barras
    for bar, porcentaje in zip(bars, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{porcentaje:.2f}%", ha='center', fontsize=7)

    # Ajustar espacio entre etiquetas del eje x
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Guardar la imagen de la gráfica de barras en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path_bar = os.path.join(chart_dir, 'pregunta_45_chart.png')
    fig.savefig(chart_path_bar, format='png')

    # Obtener la URL de la imagen de la gráfica de barras
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_45_chart.png')

    return chart_url










# Obtener los datos de la pregunta_46
def generate_pregunta_46_chart(request):
    # Usamos el modelo generativo de la IA 
    modelo = genai.GenerativeModel('gemini-pro')
    # Configuramos la API KEY 
    GOOGLE_API_KEY='AIzaSyCTtp7jYZ0S7zmxa8_o0slr3M2BpAPICJs'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Importamos las respuestas de la base de datos
    virtud_1 = PreguntaAbiertaVirtudes.objects.values_list('virtud_1', flat=True)
    virtud_2 = PreguntaAbiertaVirtudes.objects.values_list('virtud_2', flat=True)
    virtud_3 = PreguntaAbiertaVirtudes.objects.values_list('virtud_3', flat=True)
    respuestas = list(virtud_1) + list(virtud_2) + list(virtud_3) 

    # Convertimos las respuestas en un solo texto
    texto_respuestas = '|'.join(respuestas)

# Definimos el prompt
    prompt = ('genera 10 categorias, siempre 10, de almenos dos palabras, basadas en los textos suministrados teniendo en cuenta que los titulos de las categorias deben estar relacionados a lo que es una organizacion y el contexto que es:'
              'Mencione virtudes de esta entidad.'
              'para crear las categorias, usa los terminos en relacion con una jerga profesional en la psicologia organizacional'
              'usa todos los textos exceptuando los textos que solo dicen "Ninguna, .., N. A, ...,", por nada los vayas a usar para las categorias. No cree una categoria llamada "otros"'
              'haz un conteo de todos los textos, ten en cuenta que estan separados por "|", dame un conteo y un porcentaje para cada categoria.'
              'los datos siempre seran entregados en el siguiente formato, como si fuera una tabla: | Categoria | Conteo | Porcentaje | . SIEMPRE se va a usar ese formato sin alteraciones, siempre.'
              'no es necesario entregar más informacion ademas de las categorias, el conteo y el porcentaje en  el formato solicitado.')


    # Generamos la respuesta basada en el prompt y el texto de las respuestas
    respuesta = modelo.generate_content(prompt + texto_respuestas)
    respuesta = respuesta.text

    # Rebajamos el tamaño de la respuesta de la IA 
    respuestaaaas = respuesta.replace('**', '|')
    respuestaaaas = respuesta.replace('*', '|')
    respuestaaaas = respuesta.replace('| |', '|')
    print (respuestaaaas)

    # Extraer las categorías, conteos y porcentajes
    categorias = re.findall(r'\| (.+?) \| (\d+) \| (\d+(?:[,.]\d+)?)% \|', respuestaaaas)
    print (categorias)

    # Convertir porcentajes a números
    conteos = [int(c[1]) for c in categorias]
    porcentajes = [float(c[2].replace(',', '.')) for c in categorias]

    # Convertir las categorías a una lista
    categorias = [c[0] for c in categorias]
 

    # Crear figura
    fig = Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    # Crear gráfica de barras
    bars = ax.bar(categorias, conteos, color='lightgreen')

    # Añadir etiquetas y título
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Conteo')
    ax.set_title('46. Virtudes de la entidad')
    ax.set_xticklabels(categorias, rotation=45, ha='right')

    # Ajustar márgenes
    fig.subplots_adjust(bottom=0.4, top=0.9) 

    # Mostrar porcentajes con decimales en las barras
    for bar, porcentaje in zip(bars, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{porcentaje:.2f}%", ha='center', fontsize=7)

    # Ajustar espacio entre etiquetas del eje x
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Guardar la imagen de la gráfica de barras en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path_bar = os.path.join(chart_dir, 'pregunta_46_chart.png')
    fig.savefig(chart_path_bar, format='png')

    # Obtener la URL de la imagen de la gráfica de barras
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_46_chart.png')

    return chart_url











# Obtener los datos de la pregunta_47
def generate_pregunta_47_chart(request):
    # Usamos el modelo generativo de la IA 
    modelo = genai.GenerativeModel('gemini-pro')
    # Configuramos la API KEY 
    GOOGLE_API_KEY='AIzaSyCTtp7jYZ0S7zmxa8_o0slr3M2BpAPICJs'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Importamos las respuestas de la base de datos
    habito_1 = PreguntaAbiertaHabitos.objects.values_list('habito_1', flat=True)
    habito_2 = PreguntaAbiertaHabitos.objects.values_list('habito_2', flat=True)
    respuestas = list(habito_1) + list(habito_2)

    # Convertimos las respuestas en un solo texto
    texto_respuestas = '|'.join(respuestas)

# Definimos el prompt
    prompt = ('genera 10 categoriasque describan habitos diarios, siempre 10, basadas en los textos suministrados teniendo en cuenta que los titulos de las categorias deben estar relacionados a lo que es una organizacion y el contexto que es:'
              '"Mencione hábitos diarios que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados."'
              'para crear las categorias usa los terminos en relacion con una jerga profesional en la PSICOLOGÍA ORGANIZACIONAL'
              'usa todos los textos exceptuando los textos que solo dicen "Ninguna, .., N. A, ...,", por nada los vayas a usar para las categorias.'
              'Los titulos de las categorias deben ser de más de una palabra para describir mejor el tema del que se habla'
              'haz un conteo de todos los textos, ten en cuenta que estan separados por "|", dame un conteo y un porcentaje para cada categoria.'
              'El formato debe ser estricto, los datos siempre seran entregados en el siguiente formato, como si fuera una tabla: | Categoria | Conteo | Porcentaje | , SIEMPRE se va a usar ese formato sin alteraciones, siempre.'
              'no es necesario entregar más informacion ademas de las categorias, el conteo y el porcentaje en el formato solicitado.'
              'Por favor, que las categorias sean coherentes')


    # Generamos la respuesta basada en el prompt y el texto de las respuestas
    respuesta = modelo.generate_content(prompt + texto_respuestas)
    respuesta = respuesta.text

    # Rebajamos el tamaño de la respuesta de la IA 
    respuestaaaas = respuesta.replace('**', '|')
    respuestaaaas = respuesta.replace('*', '|')
    respuestaaaas = respuesta.replace('| |', '|')
    print (respuestaaaas)

    # Extraer las categorías, conteos y porcentajes
    categorias = re.findall(r'\| (.+?) \| (\d+) \| (\d+(?:[,.]\d+)?)% \|', respuestaaaas)
    print (categorias)

    # Convertir porcentajes a números
    conteos = [int(c[1]) for c in categorias]
    porcentajes = [float(c[2].replace(',', '.')) for c in categorias]

    # Convertir las categorías a una lista
    categorias = [c[0] for c in categorias]
 

    # Crear figura
    fig = Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    # Crear gráfica de barras
    bars = ax.bar(categorias, conteos, color='lightgreen')

    # Añadir etiquetas y título
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Conteo')
    ax.set_title('47. Hábitos diarios')
    ax.set_xticklabels(categorias, rotation=45, ha='right')

    # Ajustar márgenes
    fig.subplots_adjust(bottom=0.4, top=0.9) 

    # Mostrar porcentajes con decimales en las barras
    for bar, porcentaje in zip(bars, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{porcentaje:.2f}%", ha='center', fontsize=7)

    # Ajustar espacio entre etiquetas del eje x
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Guardar la imagen de la gráfica de barras en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path_bar = os.path.join(chart_dir, 'pregunta_47_chart.png')
    fig.savefig(chart_path_bar, format='png')

    # Obtener la URL de la imagen de la gráfica de barras
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_47_chart.png')

    return chart_url









# Obtener los datos de la pregunta_48
def generate_pregunta_48_chart(request):
    # Usamos el modelo generativo de la IA 
    modelo = genai.GenerativeModel('gemini-pro')
    # Configuramos la API KEY 
    GOOGLE_API_KEY='AIzaSyCTtp7jYZ0S7zmxa8_o0slr3M2BpAPICJs'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Importamos las respuestas de la base de datos
    habito_1 = PreguntaAbiertaHabitosMensuales.objects.values_list('habito_1', flat=True)
    habito_2 = PreguntaAbiertaHabitosMensuales.objects.values_list('habito_2', flat=True)
    respuestas = list(habito_1) + list(habito_2)

    # Convertimos las respuestas en un solo texto
    texto_respuestas = '|'.join(respuestas)

# Definimos el prompt
    prompt = ('genera 10 categorias que describan habitos mensuales, siempre 10, basadas en los textos suministrados teniendo en cuenta que los titulos de las categorias deben estar relacionados a lo que es una organizacion y el contexto que es:'
              '"Mencione hábitos mensuales que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados."'
              'para crear las categorias usa los terminos en relacion con una jerga profesional en la PSICOLOGÍA ORGANIZACIONAL, haz un buen analisis del lenguaje'
              'usa todos los textos exceptuando los textos que solo dicen "Ninguna, .., N. A, ...,", por nada los vayas a usar para las categorias.'
              'Los titulos de las categorias deben ser de más de una palabra para describir mejor el tema del que se habla'
              'haz un conteo de todos los textos, ten en cuenta que estan separados por "|", dame un conteo y un porcentaje para cada categoria.'
              'El formato debe ser estricto, los datos siempre seran entregados en el siguiente formato, como si fuera una tabla: | Categoria | Conteo | Porcentaje | , SIEMPRE se va a usar ese formato sin alteraciones, siempre. No agregues espacios adicionales o caracteres.'
              'no es necesario entregar más informacion ademas de las categorias, el conteo y el porcentaje en el formato solicitado.'
              'Por favor, que las categorias sean coherentes')


    # Generamos la respuesta basada en el prompt y el texto de las respuestas
    respuesta = modelo.generate_content(prompt + texto_respuestas)
    respuesta = respuesta.text

    # Rebajamos el tamaño de la respuesta de la IA 
    respuestaaaas = respuesta.replace('**', '|')
    respuestaaaas = respuesta.replace('*', '|')
    respuestaaaas = respuesta.replace('| |', '|')
    print (respuestaaaas)

    # Extraer las categorías, conteos y porcentajes
    categorias = re.findall(r'\| (.+?) \| (\d+) \| (\d+(?:[,.]\d+)?)% \|', respuestaaaas)
    print (categorias)

    # Convertir porcentajes a números
    conteos = [int(c[1]) for c in categorias]
    porcentajes = [float(c[2].replace(',', '.')) for c in categorias]

    # Convertir las categorías a una lista
    categorias = [c[0] for c in categorias]
 

    # Crear figura
    fig = Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    # Crear gráfica de barras
    bars = ax.bar(categorias, conteos, color='lightgreen')

    # Añadir etiquetas y título
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Conteo')
    ax.set_title('48. Hábitos mensuales')
    ax.set_xticklabels(categorias, rotation=45, ha='right')

    # Ajustar márgenes
    fig.subplots_adjust(bottom=0.4, top=0.9) 

    # Mostrar porcentajes con decimales en las barras
    for bar, porcentaje in zip(bars, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{porcentaje:.2f}%", ha='center', fontsize=7)

    # Ajustar espacio entre etiquetas del eje x
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Guardar la imagen de la gráfica de barras en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path_bar = os.path.join(chart_dir, 'pregunta_48_chart.png')
    fig.savefig(chart_path_bar, format='png')

    # Obtener la URL de la imagen de la gráfica de barras
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_48_chart.png')

    return chart_url















# Obtener los datos de la pregunta_49
def generate_pregunta_49_chart(request):
    # Usamos el modelo generativo de la IA 
    modelo = genai.GenerativeModel('gemini-pro')
    # Configuramos la API KEY 
    GOOGLE_API_KEY='AIzaSyCTtp7jYZ0S7zmxa8_o0slr3M2BpAPICJs'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Importamos las respuestas de la base de datos
    habito_1 = PreguntaAbiertaHabitosAnuales.objects.values_list('habito_1', flat=True)
    habito_2 = PreguntaAbiertaHabitosAnuales.objects.values_list('habito_2', flat=True)
    respuestas = list(habito_1) + list(habito_2)

    # Convertimos las respuestas en un solo texto
    texto_respuestas = '|'.join(respuestas)

# Definimos el prompt
    prompt = ('genera 10 categorias que describan habitos anuales, siempre 10, basadas en los textos suministrados teniendo en cuenta que los titulos de las categorias deben estar relacionados a lo que es una organizacion y el contexto que es:'
              '"Mencione hábitos anuales que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados."'
              'para crear las categorias usa los terminos en relacion con una jerga profesional en la PSICOLOGÍA ORGANIZACIONAL'
              'usa todos los textos exceptuando los textos que solo dicen "Ninguna, .., N. A, ...,", por nada los vayas a usar para las categorias.'
              'Los titulos de las categorias deben ser de más de una palabra para describir mejor el tema del que se habla'
              'haz un conteo de todos los textos, ten en cuenta que estan separados por "|", dame un conteo y un porcentaje para cada categoria.'
              'El formato debe ser estricto, los datos siempre seran entregados en el siguiente formato, como si fuera una tabla: | Categoria | Conteo | Porcentaje | , SIEMPRE se va a usar ese formato sin alteraciones, siempre.'
              'no es necesario entregar más informacion ademas de las categorias, el conteo y el porcentaje en el formato solicitado.'
              'Por favor, que las categorias sean coherentes')


    # Generamos la respuesta basada en el prompt y el texto de las respuestas
    respuesta = modelo.generate_content(prompt + texto_respuestas)
    respuesta = respuesta.text

    # Rebajamos el tamaño de la respuesta de la IA 
    respuestaaaas = respuesta.replace('**', '|')
    respuestaaaas = respuesta.replace('*', '|')
    respuestaaaas = respuesta.replace('| |', '|')
    print (respuestaaaas)

    # Extraer las categorías, conteos y porcentajes
    categorias = re.findall(r'\| (.+?) \| (\d+) \| (\d+(?:[,.]\d+)?)% \|', respuestaaaas)
    print (categorias)

    # Convertir porcentajes a números
    conteos = [int(c[1]) for c in categorias]
    porcentajes = [float(c[2].replace(',', '.')) for c in categorias]

    # Convertir las categorías a una lista
    categorias = [c[0] for c in categorias]
 

    # Crear figura
    fig = Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    # Crear gráfica de barras
    bars = ax.bar(categorias, conteos, color='lightgreen')

    # Añadir etiquetas y título
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Conteo')
    ax.set_title('49. Hábitos anuales')
    ax.set_xticklabels(categorias, rotation=45, ha='right')

    # Ajustar márgenes
    fig.subplots_adjust(bottom=0.4, top=0.9) 

    # Mostrar porcentajes con decimales en las barras
    for bar, porcentaje in zip(bars, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{porcentaje:.2f}%", ha='center', fontsize=7)

    # Ajustar espacio entre etiquetas del eje x
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Guardar la imagen de la gráfica de barras en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path_bar = os.path.join(chart_dir, 'pregunta_49_chart.png')
    fig.savefig(chart_path_bar, format='png')

    # Obtener la URL de la imagen de la gráfica de barras
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_49_chart.png')

    return chart_url












# Obtener los datos de la pregunta_50
def generate_pregunta_50_chart(request):
    # Usamos el modelo generativo de la IA 
    modelo = genai.GenerativeModel('gemini-pro')
    # Configuramos la API KEY 
    GOOGLE_API_KEY='AIzaSyCTtp7jYZ0S7zmxa8_o0slr3M2BpAPICJs'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Importamos las respuestas de la base de datos
    defectos_persona_A = PreguntaAbiertaDefectosPersonas.objects.values_list('defectos_persona_A', flat=True)
    defectos_persona_B = PreguntaAbiertaDefectosPersonas.objects.values_list('defectos_persona_B', flat=True)
    defectos_persona_C = PreguntaAbiertaDefectosPersonas.objects.values_list('defectos_persona_C', flat=True)
    respuestas = list(defectos_persona_A) + list(defectos_persona_B) + list(defectos_persona_C)

    # Convertimos las respuestas en un solo texto
    texto_respuestas = '|'.join(respuestas)

# Definimos el prompt
    prompt = ('genera 10 categorias que describan sus defectos, siempre 10, basadas en los textos suministrados teniendo en cuenta que los titulos de las categorias deben estar relacionados a lo que es una organizacion y el contexto que es:'
              '"Piense en personas que se destacan negativamente dentro de la empresa y señale sólo sus defectos."'
              'para crear las categorias usa los terminos en relacion con una jerga profesional en la PSICOLOGÍA ORGANIZACIONAL'
              'usa todos los textos exceptuando los textos que solo dicen "Ninguna, .., N. A, ...,", por nada los vayas a usar para las categorias.'
              'Los titulos de las categorias deben ser de más de una palabra para describir mejor el tema del que se habla'
              'haz un conteo de todos los textos, ten en cuenta que estan separados por "|", dame un conteo y un porcentaje para cada categoria.'
              'El formato debe ser estricto, los datos siempre seran entregados en el siguiente formato, como si fuera una tabla: | Categoria | Conteo | Porcentaje | , SIEMPRE se va a usar ese formato sin alteraciones, siempre.'
              'no es necesario entregar más informacion ademas de las categorias, el conteo y el porcentaje en el formato solicitado.'
              'Por favor, que las categorias sean coherentes')


    # Generamos la respuesta basada en el prompt y el texto de las respuestas
    respuesta = modelo.generate_content(prompt + texto_respuestas)
    respuesta = respuesta.text

    # Rebajamos el tamaño de la respuesta de la IA 
    respuestaaaas = respuesta.replace('**', '|')
    respuestaaaas = respuesta.replace('*', '|')
    print (respuestaaaas)

    # Extraer las categorías, conteos y porcentajes
    categorias = re.findall(r'\| (.+?) \| (\d+) \| (\d+(?:[,.]\d+)?)% \|', respuestaaaas)
    print (categorias)

    # Convertir porcentajes a números
    conteos = [int(c[1]) for c in categorias]
    porcentajes = [float(c[2].replace(',', '.')) for c in categorias]

    # Convertir las categorías a una lista
    categorias = [c[0] for c in categorias]
 

    # Crear figura
    fig = Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    # Crear gráfica de barras
    bars = ax.bar(categorias, conteos, color='lightgreen')

    # Añadir etiquetas y título
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Conteo')
    ax.set_title('50. Antihéroes')
    ax.set_xticklabels(categorias, rotation=45, ha='right')

    # Ajustar márgenes
    fig.subplots_adjust(bottom=0.4, top=0.9) 

    # Mostrar porcentajes con decimales en las barras
    for bar, porcentaje in zip(bars, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{porcentaje:.2f}%", ha='center', fontsize=7)

    # Ajustar espacio entre etiquetas del eje x
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Guardar la imagen de la gráfica de barras en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path_bar = os.path.join(chart_dir, 'pregunta_50_chart.png')
    fig.savefig(chart_path_bar, format='png')

    # Obtener la URL de la imagen de la gráfica de barras
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_50_chart.png')

    return chart_url











# Obtener los datos de la pregunta_51
def generate_pregunta_51_chart(request):
    # Usamos el modelo generativo de la IA 
    modelo = genai.GenerativeModel('gemini-pro')
    # Configuramos la API KEY 
    GOOGLE_API_KEY='AIzaSyCTtp7jYZ0S7zmxa8_o0slr3M2BpAPICJs'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Importamos las respuestas de la base de datos
    virtudes_persona_A = PreguntaAbiertaVirtudesPersonas.objects.values_list('virtudes_persona_A', flat=True)
    virtudes_persona_B = PreguntaAbiertaVirtudesPersonas.objects.values_list('virtudes_persona_B', flat=True)
    virtudes_persona_C = PreguntaAbiertaVirtudesPersonas.objects.values_list('virtudes_persona_C', flat=True)
    respuestas = list(virtudes_persona_A) + list(virtudes_persona_B) + list(virtudes_persona_C)

    # Convertimos las respuestas en un solo texto
    texto_respuestas = '|'.join(respuestas)

# Definimos el prompt
    prompt = ('genera 10 categorias que describan sus virtudes, siempre 10, basadas en los textos suministrados teniendo en cuenta que los titulos de las categorias deben estar relacionados a lo que es una organizacion y el contexto que es:'
              '"Piense personas que se destacan positivamente dentro de la empresa y señale sólo sus virtudes."'
              'para crear las categorias usa los terminos en relacion con una jerga profesional en la PSICOLOGÍA ORGANIZACIONAL'
              'usa todos los textos exceptuando los textos que solo dicen "Ninguna, .., N. A, ...,", por nada los vayas a usar para las categorias.'
              'Los titulos de las categorias deben ser de más de una palabra para describir mejor el tema del que se habla'
              'haz un conteo de todos los textos, ten en cuenta que estan separados por "|", dame un conteo y un porcentaje para cada categoria.'
              'El formato debe ser estricto, los datos siempre seran entregados en el siguiente formato, como si fuera una tabla: | Categoria | Conteo | Porcentaje | , SIEMPRE se va a usar ese formato sin alteraciones, siempre.'
              'no es necesario entregar más informacion ademas de las categorias, el conteo y el porcentaje en el formato solicitado.'
              'Por favor, que las categorias sean coherentes')


    # Generamos la respuesta basada en el prompt y el texto de las respuestas
    respuesta = modelo.generate_content(prompt + texto_respuestas)
    respuesta = respuesta.text

    # Rebajamos el tamaño de la respuesta de la IA 
    respuestaaaas = respuesta.replace('**', '|')
    respuestaaaas = respuesta.replace('*', '|')
    print (respuestaaaas)

    # Extraer las categorías, conteos y porcentajes
    categorias = re.findall(r'\| (.+?) \| (\d+) \| (\d+(?:[,.]\d+)?)% \|', respuestaaaas)
    print (categorias)

    # Convertir porcentajes a números
    conteos = [int(c[1]) for c in categorias]
    porcentajes = [float(c[2].replace(',', '.')) for c in categorias]

    # Convertir las categorías a una lista
    categorias = [c[0] for c in categorias]
 

    # Crear figura
    fig = Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    # Crear gráfica de barras
    bars = ax.bar(categorias, conteos, color='lightgreen')

    # Añadir etiquetas y título
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Conteo')
    ax.set_title('51. Héroes')
    ax.set_xticklabels(categorias, rotation=45, ha='right')

    # Ajustar márgenes
    fig.subplots_adjust(bottom=0.4, top=0.9) 

    # Mostrar porcentajes con decimales en las barras
    for bar, porcentaje in zip(bars, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{porcentaje:.2f}%", ha='center', fontsize=7)

    # Ajustar espacio entre etiquetas del eje x
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Guardar la imagen de la gráfica de barras en un directorio
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path_bar = os.path.join(chart_dir, 'pregunta_51_chart.png')
    fig.savefig(chart_path_bar, format='png')

    # Obtener la URL de la imagen de la gráfica de barras
    chart_url = os.path.join(settings.MEDIA_URL, 'charts', 'pregunta_51_chart.png')

    return chart_url








#Postulacion frente a premisas preguntas 52 a 61
# Función para obtener datos de las preguntas 52 a 61
def generar_tabla_liderazgo(request):
    """
    Obtiene los datos desde el modelo, los anonimiza, calcula frecuencias y genera una tabla de resultados.
    Retorna la URL de la imagen generada.
    """

    # **Paso 1: Obtener los datos desde el modelo**
    respuestas = PreguntaAbiertaCompaneros.objects.filter(
        fiesta_integracion__isnull=False, 
        defensa_intereses__isnull=False, 
        representante_directivas__isnull=False, 
        organizador_equipo_deportivo__isnull=False,
        organizador_equipos_trabajo__isnull=False,
        divulgacion_hechos__isnull=False,
        confianza_secreto__isnull=False,
        resolver_problemas__isnull=False,
        enseñanza_trabajo__isnull=False,
        lider_funcionario__isnull=False
    ).values(
        'fiesta_integracion', 'defensa_intereses', 'representante_directivas', 
        'organizador_equipo_deportivo', 'organizador_equipos_trabajo',
        'divulgacion_hechos', 'confianza_secreto', 'resolver_problemas', 
        'enseñanza_trabajo', 'lider_funcionario'
    )

    # Convertir a DataFrame de pandas
    df = pd.DataFrame(respuestas)

    # Verificar si hay datos disponibles
    if df.empty:
        print("No se encontraron datos.")
        return None

    print("Datos obtenidos del modelo:", df)

    # **Paso 2: Calcular frecuencias y porcentajes** para cada columna (Pregunta)
    porcentajes_dict = {}
    for col in df.columns:
        frecuencias = df[col].value_counts()
        total = frecuencias.sum()
        porcentajes = (frecuencias / total * 100).round(2)
        porcentajes_dict[col] = pd.DataFrame({
            'Nombre': frecuencias.index,
            'Porcentaje': porcentajes.values
        })

    print("Porcentajes calculados:", porcentajes_dict)

    # **Paso 3: Crear y guardar la tabla usando pandas y matplotlib**
    # Crear un DataFrame para la tabla final
    tabla_final = pd.DataFrame()

    # Iterar sobre las columnas y construir los datos para la tabla
    for col in porcentajes_dict:
        df_col = porcentajes_dict[col]
        df_col.columns = [f"{col}_Nombre", f"{col}_Porcentaje"]
        tabla_final = pd.concat([tabla_final, df_col], axis=1)

    print(type(tabla_final))

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('off')  # Desactivamos los ejes para mostrar solo la tabla

    # Dibujar la tabla usando pandas.plotting.table
    from pandas.plotting import table
    tabla = table(ax, tabla_final, loc='center', cellLoc='center', colWidths=[0.1] * len(tabla_final.columns))
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(12)
    tabla.scale(1.2, 1.2)

    # **Paso 4: Guardar la imagen en la carpeta media/charts**
    chart_dir = os.path.join(settings.BASE_DIR, 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, 'tabla_liderazgo.png')
    fig.savefig(chart_path, bbox_inches='tight', dpi=300)

    # Retornar la URL de la imagen generada
    table_url = os.path.join(settings.MEDIA_URL, 'charts', 'tabla_liderazgo.png')
    return table_url




#Sintesis





















def view_results(request):

    # Llamar a la función para generar la gráfica de barras y obtener la URL de la imagen
    age_chart_url = generate_age_bar_chart(request)
    gender_chart_url = generate_gender_bar_chart(request)
    area_empresa_chart_url = generate_area_empresa_chart(request)
    antiguedad_empresa_chart_url = generate_antiguedad_empresa_chart(request)
    table_url = tabla_datos(request)
    pregunta_1_chart_url = generate_pregunta_1_chart(request)
    pregunta_2_chart_url = generate_pregunta_2_chart(request)
    pregunta_3_chart_url = generate_pregunta_3_chart(request)
    pregunta_4_chart_url = generate_pregunta_4_chart(request)
    pregunta_5_chart_url = generate_pregunta_5_chart(request)
    pregunta_6_chart_url = generate_pregunta_6_chart(request)
    pregunta_7_chart_url = generate_pregunta_7_chart(request)
    pregunta_8_chart_url = generate_pregunta_8_chart(request)
    pregunta_9_chart_url = generate_pregunta_9_chart(request)
    pregunta_10_chart_url = generate_pregunta_10_chart(request)
    pregunta_11_chart_url = generate_pregunta_11_chart(request)
    pregunta_12_chart_url = generate_pregunta_12_chart(request)
    pregunta_13_chart_url = generate_pregunta_13_chart(request)
    pregunta_14_chart_url = generate_pregunta_14_chart(request)
    pregunta_15_chart_url = generate_pregunta_15_chart(request)
    pregunta_16_chart_url = generate_pregunta_16_chart(request)
    pregunta_17_chart_url = generate_pregunta_17_chart(request)
    pregunta_18_chart_url = generate_pregunta_18_chart(request)
    pregunta_19_chart_url = generate_pregunta_19_chart(request)
    pregunta_20_chart_url = generate_pregunta_20_chart(request)
    pregunta_21_chart_url = generate_pregunta_21_chart(request)
    pregunta_22_chart_url = generate_pregunta_22_chart(request)
    pregunta_23_chart_url = generate_pregunta_23_chart(request)
    pregunta_24_chart_url = generate_pregunta_24_chart(request)
    pregunta_25_chart_url = generate_pregunta_25_chart(request)
    pregunta_26_chart_url = generate_pregunta_26_chart(request)
    pregunta_27_chart_url = generate_pregunta_27_chart(request)
    pregunta_28_chart_url = generate_pregunta_28_chart(request)
    pregunta_29_chart_url = generate_pregunta_29_chart(request)
    pregunta_30_chart_url = generate_pregunta_30_chart(request)
    pregunta_31_chart_url = generate_pregunta_31_chart(request)
    pregunta_32_chart_url = generate_pregunta_32_chart(request)
    pregunta_33_chart_url = generate_pregunta_33_chart(request)
    pregunta_34_chart_url = generate_pregunta_34_chart(request)
    pregunta_35_chart_url = generate_pregunta_35_chart(request)
    pregunta_36_chart_url = generate_pregunta_36_chart(request)
    pregunta_37_chart_url = generate_pregunta_37_chart(request)
    pregunta_38_chart_url = generate_pregunta_38_chart(request)
    pregunta_39_chart_url = generate_pregunta_39_chart(request)
    pregunta_40_chart_url = generate_pregunta_40_chart(request)
    pregunta_41_chart_url = generate_pregunta_41_chart(request)
    pregunta_42_chart_bar3_url = procesar_respuestas3(request)
    pregunta_43_opcion_1_chart_url = generate_pregunta_43_opcion_1_chart(request)
    pregunta_43_opcion_2_chart_url = generate_pregunta_43_opcion_2_chart(request)
    pregunta_43_opcion_3_chart_url = generate_pregunta_43_opcion_3_chart(request)
    pregunta_43_chart_url = generate_pregunta_43_chart(request)
    pregunta_44_opcion_1_chart_url = generate_pregunta_44_opcion_1_chart(request)
    pregunta_44_opcion_2_chart_url = generate_pregunta_44_opcion_2_chart(request)
    pregunta_44_opcion_3_chart_url = generate_pregunta_44_opcion_3_chart(request)
    pregunta_44_opcion_4_chart_url = generate_pregunta_44_opcion_4_chart(request)
    pregunta_44_chart_url = generate_pregunta_44_chart(request)
    pregunta_45_chart_url = generate_pregunta_45_chart(request)
    pregunta_46_chart_url = generate_pregunta_46_chart(request)
    pregunta_47_chart_url = generate_pregunta_47_chart(request)
    pregunta_48_chart_url = generate_pregunta_48_chart(request)
    pregunta_49_chart_url = generate_pregunta_49_chart(request)
    pregunta_50_chart_url = generate_pregunta_50_chart(request)
    pregunta_51_chart_url = generate_pregunta_51_chart(request)
    preguntas_52_a_61_table_url = generar_tabla_liderazgo(request)









    # Renderizar la plantilla HTML con las URLs de las imágenes
    context = {
        'age_chart_url': age_chart_url,
        'gender_chart_url': gender_chart_url,
        'area_empresa_chart_url': area_empresa_chart_url,
        'antiguedad_empresa_chart_url': antiguedad_empresa_chart_url,
        'data_table_url': table_url,
        'pregunta_1_chart_url': pregunta_1_chart_url,
        'pregunta_2_chart_url': pregunta_2_chart_url,
        'pregunta_3_chart_url': pregunta_3_chart_url,
        'pregunta_4_chart_url': pregunta_4_chart_url,
        'pregunta_5_chart_url': pregunta_5_chart_url,
        'pregunta_6_chart_url': pregunta_6_chart_url,
        'pregunta_7_chart_url': pregunta_7_chart_url,
        'pregunta_8_chart_url': pregunta_8_chart_url,
        'pregunta_9_chart_url': pregunta_9_chart_url,
        'pregunta_10_chart_url': pregunta_10_chart_url,
        'pregunta_11_chart_url': pregunta_11_chart_url,
        'pregunta_12_chart_url': pregunta_12_chart_url,
        'pregunta_13_chart_url': pregunta_13_chart_url,
        'pregunta_14_chart_url': pregunta_14_chart_url,
        'pregunta_15_chart_url': pregunta_15_chart_url,
        'pregunta_16_chart_url': pregunta_16_chart_url,
        'pregunta_17_chart_url': pregunta_17_chart_url,
        'pregunta_18_chart_url': pregunta_18_chart_url,
        'pregunta_19_chart_url': pregunta_19_chart_url,
        'pregunta_20_chart_url': pregunta_20_chart_url,
        'pregunta_21_chart_url': pregunta_21_chart_url,
        'pregunta_22_chart_url': pregunta_22_chart_url,
        'pregunta_23_chart_url': pregunta_23_chart_url,
        'pregunta_24_chart_url': pregunta_24_chart_url,
        'pregunta_25_chart_url': pregunta_25_chart_url,
        'pregunta_26_chart_url': pregunta_26_chart_url,
        'pregunta_27_chart_url': pregunta_27_chart_url,
        'pregunta_28_chart_url': pregunta_28_chart_url,
        'pregunta_29_chart_url': pregunta_29_chart_url,
        'pregunta_30_chart_url': pregunta_30_chart_url,
        'pregunta_31_chart_url': pregunta_31_chart_url,
        'pregunta_32_chart_url': pregunta_32_chart_url,
        'pregunta_33_chart_url': pregunta_33_chart_url,
        'pregunta_34_chart_url': pregunta_34_chart_url,
        'pregunta_35_chart_url': pregunta_35_chart_url,
        'pregunta_36_chart_url': pregunta_36_chart_url,
        'pregunta_37_chart_url': pregunta_37_chart_url,
        'pregunta_38_chart_url': pregunta_38_chart_url,
        'pregunta_39_chart_url': pregunta_39_chart_url,
        'pregunta_40_chart_url': pregunta_40_chart_url,
        'pregunta_41_chart_url': pregunta_41_chart_url,
        'pregunta_42_chart_bar3_url' : pregunta_42_chart_bar3_url,
        'pregunta_43_opcion_1_chart_url': pregunta_43_opcion_1_chart_url,
        'pregunta_43_opcion_2_chart_url': pregunta_43_opcion_2_chart_url,
        'pregunta_43_opcion_3_chart_url': pregunta_43_opcion_3_chart_url,
        'pregunta_43_chart_url': pregunta_43_chart_url,
        'pregunta_44_opcion_1_chart_url': pregunta_44_opcion_1_chart_url,
        'pregunta_44_opcion_2_chart_url': pregunta_44_opcion_2_chart_url,
        'pregunta_44_opcion_3_chart_url': pregunta_44_opcion_3_chart_url,
        'pregunta_44_opcion_4_chart_url': pregunta_44_opcion_4_chart_url,
        'pregunta_44_chart_url': pregunta_44_chart_url,
        'pregunta_45_chart_url': pregunta_45_chart_url,
        'pregunta_46_chart_url': pregunta_46_chart_url,
        'pregunta_47_chart_url': pregunta_47_chart_url,
        'pregunta_48_chart_url': pregunta_48_chart_url,
        'pregunta_49_chart_url': pregunta_49_chart_url,
        'pregunta_50_chart_url': pregunta_50_chart_url,
        'pregunta_51_chart_url': pregunta_51_chart_url,
        'preguntas_52_a_61_table_url' : preguntas_52_a_61_table_url,
    }
    return render(request, 'results.html', context)
