from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import date
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType

# Conexión a PostgreSQL
POSTGRES_URL = 'postgresql://postgres:1234567890@192.168.20.38/cicclo'
engine = create_engine(POSTGRES_URL)

Base = declarative_base()

class Entrevista(Base):
    __tablename__ = 'entrevistas'

    id = Column(Integer, primary_key=True)
    correo = Column(String)
    area_empresa = Column(String)
    edad = Column(Integer)
    genero = Column(String)
    antiguedad = [
        ("Menos_de_6_meses", "Menos de 6 meses"),
        ("De_6_meses_a_1_año", "De 6 meses a 1 año"),
        ("De_1_año_a_5_años", "De 1 año a 5 años"),
        ("De_5_años_a_10_años", "De 5 años a 10 años"),
        ("Mas_de_10_años", "Más de 10 años")
    ]
    antiguedad = Column(ChoiceType(antiguedad, impl=String()))

    preguntas_cerradas = relationship("PreguntaCerrada", back_populates="entrevista")
    preguntas_abiertas = relationship("PreguntaAbierta", back_populates="entrevista")

class PreguntaCerrada(Base):
    __tablename__ = 'preguntas_cerradas'

    id = Column(Integer, primary_key=True)
    pregunta = Column(String)
    respuesta = Column(String)
    entrevista_id = Column(Integer, ForeignKey('entrevistas.id'))
    entrevista = relationship("Entrevista", back_populates="preguntas_cerradas")

class PreguntaAbierta(Base):
    __tablename__ = 'preguntas_abiertas'

    id = Column(Integer, primary_key=True)
    pregunta = Column(String)
    respuesta = Column(String)
    entrevista_id = Column(Integer, ForeignKey('entrevistas.id'))
    entrevista = relationship("Entrevista", back_populates="preguntas_abiertas")

# Creación de todas las tablas en la base de datos
Base.metadata.create_all(engine)

# Crear una nueva sesión de SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()

# Crear una nueva entrevista y guardarla en la base de datos
nueva_entrevista = Entrevista(correo='example@example.com', area_empresa='Departamento de Ventas', edad=30, genero='Masculino', antiguedad='De_6_meses_a_1_año')
session.add(nueva_entrevista)
session.commit()

# Agregar preguntas cerradas
preguntas_cerradas_data = [
    ('La normas que rigen la empresa admiten la expresión de la forma de ser de sus empleados.', 'Totalmente de acuerdo'),
    ('Los empleados contribuyen con ideas en la toma de decisiones de la empresa.', 'Medianamente de acuerdo'),
    ('A usted le interesa participar en la toma de las decisiones de la empresa.', 'Totalmente de acuerdo'),
    ('En la empresa cuando se crea una norma, previamente las directivas hacen consultas con los empleados.', 'Medianamente de acuerdo'),
    ('En la empresa a algunas personas les aplican las normas con bastante rigor mientras a otras les perdonan todo.', 'Totalmente de acuerdo'),
    ('En general, la empresa está mejorando en relación a como era cuando usted ingresó como empleado.', 'Totalmente de acuerdo'),
    ('En relación con el día de su ingreso como empleado, usted nota mejoría en el desempeño de los empleados de la empresa.', 'Medianamente de acuerdo'),
    ('La comunicación de trabajo, desde su jefe inmediato hacia usted es fácil.', 'Totalmente de acuerdo'),
    ('La comunicación de trabajo, desde usted hacia su jefe inmediato es fácil.', 'Medianamente de acuerdo'),
    ('La comunicación con los grupos de trabajo con los que usted necesita relacionarse es fácil.', 'Totalmente de acuerdo'),
    ('Como impresión general, usted considera que en la empresa los empleados conocen sus funciones.', 'Totalmente de acuerdo'),
    ('Normalmente la cantidad de trabajo que tiene su cargo es excesiva.', 'Medianamente de acuerdo'),
    ('Las metas que se proponen en la empresa se cumplen.', 'Medianamente de acuerdo'),
    ('Actualmente hay la tendencia en la empresa a desperdiciar insumos de trabajo.', 'Totalmente de acuerdo'),
    ('En la empresa los problemas entre las personas se resuelven fácilmente.', 'Medianamente de acuerdo'),
    ('La forma como está organizado la empresa, es fácil de entender.', 'Totalmente de acuerdo'),
    ('Las tareas son supervisadas excesivamente.', 'Totalmente de acuerdo'),
    ('En la empresa las relaciones entre las personas son cordiales.', 'Totalmente de acuerdo'),
    ('Al interior de la empresa permanentemente hay conflictos.', 'Totalmente de acuerdo'),
    ('Los empleados son solidarios entre sí.', 'Totalmente de acuerdo'),
    ('Las personas en la empresa son tolerantes.', 'Totalmente de acuerdo'),
    ('Los empleados en la empresa se actualizan en los temas que necesita la organización.', 'Totalmente de acuerdo'),
    ('La empresa apoya la autonomía de sus empleados.', 'Totalmente de acuerdo'),
    ('La empresa apoya el desarrollo de carrera (ascensos) de sus empleados.', 'Totalmente de acuerdo'),
    ('La empresa apoya las sugerencias de los empleados para innovar (en procesos, productos, servicios, etc.).', 'Totalmente de acuerdo'),
    ('En la empresa la libertad de expresión se respeta.', 'Totalmente de acuerdo'),
    ('En general, usted se siente bien trabajando en la dependencia actual.', 'Totalmente de acuerdo'),
    ('Usted se siente bien trabajando en la empresa, en general.', 'Totalmente de acuerdo'),
    ('En general, la empresa paga los salarios que cada quien se merece.', 'Totalmente de acuerdo'),
    ('Frente a entidades parecidas, la empresa es fuerte.', 'Totalmente de acuerdo'),
    ('Esta organización le cumple a sus clientes.', 'Totalmente de acuerdo'),
    ('Si usted recibiera una oferta de trabajo de otra organización se iría, siendo las condiciones de la otra las mismas.', 'Totalmente de acuerdo'),
    ('Si usted recibiera una oferta de trabajo de otra organización se iría, siendo las condiciones de la otra mucho mejores.', 'Totalmente de acuerdo'),
    ('Las condiciones de su sitio de trabajo son adecuadas para desempeñarse bien.', 'Totalmente de acuerdo'),
    ('Es notable la presencia de grupos cerrados en los cuales se refugian sus integrantes.', 'Totalmente de acuerdo'),
    ('La cantidad de tareas que tiene su cargo es mayor a la de otros cargos que se le parecen.', 'Totalmente de acuerdo'),
    ('Su jefe sabe cómo hacer el trabajo de sus subalternos.', 'Totalmente de acuerdo'),
    ('Su jefe sabe cómo premiar a sus subalternos.', 'Totalmente de acuerdo'),
    ('Su jefe sabe cómo sancionar a sus subalternos.', 'Totalmente de acuerdo'),
    ('Su puesto de trabajo tiene variedad en la forma de ejecutar las tareas.', 'Totalmente de acuerdo'),
    ('Usted encuentra congruencia entre lo que busca en su vida laboral y lo que le ofrece su puesto de trabajo.', 'Totalmente de acuerdo')
]

preguntas_cerradas = [PreguntaCerrada(pregunta=pregunta, respuesta=respuesta, entrevista=nueva_entrevista) for pregunta, respuesta in preguntas_cerradas_data]
session.add_all(preguntas_cerradas)
session.commit()

# Agregar preguntas abiertas
preguntas_abiertas_data = [
    ('Cite dos situaciones que reflejen lo que distingue la cultura de esta organización.', 'Situación 1: ...\nSituación 2: ...'),
    ('Ordene, de mayor a menor importancia, las tres razones por las cuales usted trabaja aquí.', '1: Me siento bien con mis compañeros\n2: Puedo avanzar hacia las metas que me he propuesto en la vida\n3: Puedo ayudar a organizar los equipos de trabajo'),
    ('Indique cuál de las siguientes fuentes de poder tiene mayor influencia en esta entidad (seleccione 3 en la más importante y 1 en la menos importante, seleccione 0 si no aplica).', '0\t1\t2\t3\nLas directivas\tLos empleados\tFactores externos a la entidad\t'),
    ('De haber seleccionado factores externos en la pregunta anterior, precise a que factores se refiere, de lo contrario puede saltar esta pregunta.', 'Respuesta abierta'),
    ('Mencione tres defectos de esta entidad.', 'Defecto 1:\nDefecto 2:\nDefecto 3:'),
    ('Mencione tres virtudes de esta entidad.', 'Virtud 1:\nVirtud 2:\nVirtud 3:'),
    ('Mencione dos hábitos diarios que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados.', 'Hábito 1:\nHábito 2:'),
    ('Mencione dos hábitos mensuales que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados.', 'Hábito 1:\nHábito 2:'),
    ('Mencione dos hábitos anuales que usted tenga dentro de la empresa, que le ayudan a obtener mejores resultados.', 'Hábito 1:\nHábito 2:'),
    ('Piense en tres personas que se destacan negativamente dentro de la empresa y señale sólo sus defectos.', 'Defectos persona A:\nDefectos persona B:\nDefectos persona C:'),
    ('Piense en tres personas que se destacan positivamente dentro de la empresa y señale sólo sus virtudes.', 'Virtudes persona A:\nVirtudes persona B:\nVirtudes persona C:'),
    ('A cuál de sus compañeros elegiría para que organice una fiesta de integración en la empresa.', 'Respuesta abierta'),
    ('A quién de la empresa elegiría para que defienda los intereses de su grupo profesional.', 'Respuesta abierta'),
    ('A quién de la empresa elegiría para que lo represente ante las directivas de esta organización.', 'Respuesta abierta'),
    ('A quién dentro de la empresa elegiría para que organice un equipo deportivo.', 'Respuesta abierta'),
    ('A quién dentro de la empresa elegiría para que organice los equipos de trabajo.', 'Respuesta abierta'),
    ('A quién dentro de la empresa elegiría para comentar y divulgar los hechos de la vida cotidiana de la organización.', 'Respuesta abierta'),
    ('A cuál de sus compañeros le confiaría un secreto.', 'Respuesta abierta'),
    ('A quién dentro de la empresa elegiría para resolver problemas entre compañeros de trabajo.', 'Respuesta abierta'),
    ('A cuál de sus compañeros elegiría para que le enseñara a mejorar la forma de hacer su trabajo.', 'Respuesta abierta'),
    ('Mencione a un funcionario de la empresa que según usted tiene rasgos de líder.', 'Respuesta abierta'),
    ('Coloque 3 en lo que su jefe hace con más frecuencia y 1 en lo que casi nunca hace: (Primero leerle las 3 opciones completas. Y después leérselas una por una, para que las ordene).', '1\t2\t3\nQue los subalternos se sientan bien en sus sitios de trabajo aunque no hagan bien sus tareas\tQue las tareas se hagan bien y que los empleados estén bien\tQue las tareas se hagan bien aunque los empleados estén mal')
]

preguntas_abiertas = [PreguntaAbierta(pregunta=pregunta, respuesta=respuesta, entrevista=nueva_entrevista) for pregunta, respuesta in preguntas_abiertas_data]
session.add_all(preguntas_abiertas)
session.commit()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cicclo',  # Nombre de tu base de datos
        'USER': 'postgres',  # Usuario de tu base de datos
        'PASSWORD': '1234567890',  # Contraseña de tu base de datos
        'HOST': '192.168.20.38',  # Dirección IP o nombre de host de tu base de datos
        'PORT': '5432',  # Puerto de tu base de datos (por defecto es 5432)
    }
}

DATABASES=DATABASES