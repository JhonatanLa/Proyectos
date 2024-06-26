from django.shortcuts import render, redirect, HttpResponseRedirect
from django.db.models import Count
from django.conf import settings
from .forms import ExcelUploadForm
from .models import *
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import os
import urllib.parse
from django.apps import apps
import io
import urllib, base64
import numpy as np
import unicodedata




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
    fig, ax = plt.subplots(figsize=(12, 6))

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
    fig, ax = plt.subplots(figsize=(12, 6))

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





def generate_pregunta_1_chart(request):
    # Obtener los datos de la pregunta_1
    pregunta_1_data = PreguntasCerradas.objects.values('pregunta_1').annotate(count=Count('pregunta_1')).order_by('pregunta_1')

    # Extraer las opciones de la pregunta_1 y sus frecuencias
    opciones = [item['pregunta_1'] for item in pregunta_1_data]
    frequencies = [item['count'] for item in pregunta_1_data]

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
    ax.set_title('1. La normas que rigen la empresa admiten la expresión de la forma de ser de sus empleados.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 1.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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
    ax.set_title('2. Los empleados contribuyen con ideas en la toma de decisiones de la empresa')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 2.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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
    ax.set_title('3. A usted le interesa participar en la toma de las decisiones de la empresa.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 3.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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
    ax.set_title('4. En la empresa cuando se crea una norma, previamente las directivas hacen consultas con los empleados.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 4.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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
    ax.set_title('5. En la empresa a algunas personas les aplican las normas con bastante rigor mientras a otras les perdonan todo.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 5.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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
    ax.set_title('6. En general, la empresa está mejorando en relación a como era cuando usted ingresó como empleado.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 6.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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
    ax.set_title('7. En relación con el día de su ingreso como empleado, usted nota mejoría en el desempeño de los empleados de la empresa.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 7.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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

    # Crear una nueva figura
    fig, ax = plt.subplots(figsize=(16, 6))

    # Ajustar el ancho de las barras
    bar_width = 0.5

    # Crear la gráfica de barras
    bars = ax.bar(opciones, frequencies, width=bar_width, color='skyblue')

    # Personalizar la apariencia de la gráfica
    ax.set_xlabel('Opciones')
    ax.set_ylabel('Frecuencia')
    ax.set_title('8. La comunicación de trabajo, desde su jefe inmediato hacia usted es fácil.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 8.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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
    ax.set_title('9. La comunicación de trabajo, desde usted hacia su jefe inmediato es fácil.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 9.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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
    ax.set_title('10. La comunicación con los grupos de trabajo con los que usted necesita relacionarse es fácil.')

    # Mostrar la cantidad exacta de veces que se ha respondido cada opción en el eje y y los porcentajes
    for i, rect in enumerate(bars):
        height = rect.get_height()
        ax.annotate('{} ({:.1f}%)'.format(height, percentages[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical del texto
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Descripción al lado derecho de la gráfica
    description = 'Esta gráfica muestra la distribución de respuestas para la pregunta 10.\n\n'
    description += 'Los porcentajes indican la proporción de respuestas en relación con el total de respuestas.'
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






















def view_results(request):

    # Llamar a la función para generar la gráfica de barras y obtener la URL de la imagen
    age_chart_url = generate_age_bar_chart(request)
    gender_chart_url = generate_gender_bar_chart(request)
    area_empresa_chart_url = generate_area_empresa_chart(request)
    antiguedad_empresa_chart_url = generate_antiguedad_empresa_chart(request)
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
    pregunta_43_opcion_1_chart_url = generate_pregunta_43_opcion_1_chart(request)
    pregunta_43_opcion_2_chart_url = generate_pregunta_43_opcion_2_chart(request)










    # Renderizar la plantilla HTML con las URLs de las imágenes
    context = {
        'age_chart_url': age_chart_url,
        'gender_chart_url': gender_chart_url,
        'area_empresa_chart_url': area_empresa_chart_url,
        'antiguedad_empresa_chart_url': antiguedad_empresa_chart_url,
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
        'pregunta_43_opcion_1_chart_url': pregunta_43_opcion_1_chart_url,
        'pregunta_43_opcion_2_chart_url': pregunta_43_opcion_2_chart_url,
    }
    return render(request, 'results.html', context)