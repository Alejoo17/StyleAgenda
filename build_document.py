from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

OUT=Path(__file__).parent/'entregables'
OUT.mkdir(exist_ok=True)
d=Document()
s=d.sections[0]
s.page_width=Inches(8.5); s.page_height=Inches(11)
s.top_margin=s.bottom_margin=s.left_margin=s.right_margin=Inches(1)
s.header_distance=Inches(.5)
for name in ['Normal','Title','Heading 1','Heading 2','Caption']:
 st=d.styles[name]; st.font.name='Times New Roman'; st.font.size=Pt(12); st.font.color.rgb=RGBColor(0,0,0)
 f=st.paragraph_format; f.line_spacing=2; f.space_before=Pt(0); f.space_after=Pt(0)
 f.first_line_indent=Inches(.5) if name=='Normal' else Inches(0)
 if name in ['Title','Heading 1','Heading 2']: st.font.bold=True
d.styles['Title'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
d.styles['Heading 1'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
d.styles['Heading 2'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
for name in ['Heading 1','Heading 2']: d.styles[name].paragraph_format.keep_with_next=True
hp=s.header.paragraphs[0]; hp.alignment=WD_ALIGN_PARAGRAPH.RIGHT; hp.paragraph_format.first_line_indent=Inches(0)
field=OxmlElement('w:fldSimple'); field.set(qn('w:instr'),'PAGE'); hp._p.append(field)
d.core_properties.author='Jefry Alejandro Quijano Rodriguez'
d.core_properties.title='StyleAgenda Aplicación web de reservas para barbería'
d.core_properties.subject='Patrones y Metodologías de Construcción de Software'
def p(t,indent=True):
 a=d.add_paragraph(t)
 if not indent:a.paragraph_format.first_line_indent=Inches(0)
 return a
def h(t,l=1):d.add_heading(t,l)
def table(n,title,heads,rows,widths):
 a=p('Tabla '+str(n),False);a.runs[0].bold=True;a.paragraph_format.keep_with_next=True
 a=p(title,False);a.runs[0].italic=True;a.paragraph_format.keep_with_next=True
 t=d.add_table(rows=1,cols=len(heads));t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Inches(w)
 for c,txt in zip(t.rows[0].cells,heads):c.text=txt
 pr=t.rows[0]._tr.get_or_add_trPr();pr.append(OxmlElement('w:tblHeader'))
 for row in rows:
  cells=t.add_row().cells
  for c,txt in zip(cells,row):c.text=str(txt)
 for i,row in enumerate(t.rows):
  pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
  for j,c in enumerate(row.cells):
   c.width=Inches(widths[j])
   for a in c.paragraphs:
    a.paragraph_format.first_line_indent=Inches(0)
    a.paragraph_format.line_spacing=2
    for r in a.runs:r.bold=i==0
   cp=c._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
   for edge in ['top','bottom']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single' if i==0 or (i==len(t.rows)-1 and edge=='bottom') else 'nil');e.set(qn('w:sz'),'6');b.append(e)
   cp.append(b)
 p('Nota. Elaboración propia a partir del código de StyleAgenda.',False)

for _ in range(3):p('',False)
a=d.add_paragraph('StyleAgenda Aplicación web de reservas para barbería',style='Title')
p('',False)
for txt in ['Jefry Alejandro Quijano Rodriguez','Universidad Manuela Beltrán','Ingeniería de Software','Patrones y Metodologías de Construcción de Software','Docente: Por completar','20 de noviembre de 2026']:
 a=p(txt,False);a.alignment=WD_ALIGN_PARAGRAPH.CENTER
d.add_page_break()
h('Resumen')
p('StyleAgenda es una aplicación web de reservas para barbería orientada a organizar la disponibilidad de los barberos y prevenir cruces de horarios. En este proyecto individual relaciono el análisis del problema mediante Design Thinking con un enfoque académico que articula fases de RUP, organización del trabajo inspirada en Scrum y prácticas técnicas de Extreme Programming. La solución utiliza Python, FastAPI, SQLAlchemy y SQLite, con portales diferenciados para cliente, barbero y administrador. Su estructura separa presentación, servicios, dominio, repositorios e infraestructura. El análisis técnico comprende los cinco principios SOLID, Clean Code y los patrones Singleton, creación mediante fábricas, Strategy y Observer. La disponibilidad se expresa mediante intervalos semiabiertos, y las sesiones emplean cookies firmadas y autorización por rol. La evaluación presenta el resultado de 21 tests aprobados reportado para el proyecto y relaciona los casos existentes con los requerimientos. El alcance demostrado corresponde a un prototipo académico; la concurrencia de reservas, la entrega real de correo y la evaluación con usuarios constituyen líneas de trabajo futuro. Concluyo que la separación de responsabilidades facilita explicar las reglas de negocio y diseñar su verificación, aunque la evidencia disponible no permite afirmar desempeño productivo ni cobertura total.',False)
a=p('Palabras clave: reservas, barbería, patrones de diseño, metodologías de software, pruebas automatizadas',False);a.runs[0].italic=True
h('Abstract',2)
p('StyleAgenda is a web application for managing barbershop appointments and preventing overlapping reservations. This individual project connects Design Thinking with an academic approach combining RUP phases, Scrum inspired work organization, and Extreme Programming practices. The implementation uses Python, FastAPI, SQLAlchemy, and SQLite, with separate portals for clients, barbers, and administrators. Its layers separate presentation, application services, domain rules, repositories, and infrastructure. The analysis examines SOLID principles, Clean Code, Singleton, centralized factories, Strategy, and Observer. Availability relies on half open intervals, while signed cookies and role checks support session access. The evaluation records the reported result of 21 passing tests and maps existing cases to requirements. The demonstrated scope remains an academic prototype. Concurrent reservations, actual email delivery, and user evaluation are future work. Separation of responsibilities supports reasoning about business rules and their verification; the available evidence does not establish production performance or complete test coverage.',False)
p('Keywords: appointments, barbershop, design patterns, software methodologies, automated testing',False)
h('Introducción y Planteamiento del Problema')
p('La coordinación de una barbería requiere relacionar cliente, barbero, servicio, duración y horario. Si la asignación se distribuye entre conversaciones y registros independientes, una misma franja puede ofrecerse más de una vez. En StyleAgenda abordo ese problema mediante una agenda centralizada que valida las reservas y permite consultar, cancelar y reprogramar citas. El propósito académico consiste en vincular decisiones de construcción de software con reglas de negocio verificables.')
h('Empatía y definición del problema',2)
p('Design Thinking propone comprender las necesidades antes de comprometer una solución y revisar las ideas mediante prototipos y evaluación (Hasso Plattner Institute of Design at Stanford University, s. f.). Para este caso identifico tres perspectivas de análisis: el cliente necesita conocer y conservar su reserva; el barbero necesita una agenda coherente; el administrador necesita gestionar el catálogo y supervisar la operación. Estas perspectivas orientan el diseño y no representan entrevistas ni resultados de investigación de campo.')
p('Defino el problema de diseño de la siguiente manera: ¿cómo asignar un servicio a un barbero durante un intervalo determinado sin aceptar una reserva incompatible con otra vigente? El criterio esencial es que dos citas no canceladas del mismo barbero no se superpongan. La duración del servicio determina el final de la cita y evita tratar todas las reservas como franjas de longitud fija.')
h('Ideación y alcance de la solución',2)
p('La alternativa seleccionada es una aplicación web con portales por rol y una regla central de disponibilidad. La ideación incluye mostrar servicios, calcular tarifas, mantener estados de cita y registrar eventos de confirmación, reprogramación y cancelación. El prototipo permite examinar esos flujos; su validación con clientes y barberos reales queda pendiente. No atribuyo al sistema porcentajes de reducción de errores, satisfacción o tiempos de espera porque esos indicadores requieren mediciones específicas.')
h('Objetivos')
h('Objetivo general',2)
p('Desarrollar y documentar un prototipo web individual para gestionar reservas de barbería, con validación de incompatibilidades horarias, acceso por tres roles y verificación automatizada de sus reglas principales.')
h('Objetivos específicos',2)
for txt in ['OE1. Especificar seis historias de usuario y relacionarlas con al menos ocho requerimientos funcionales y cuatro no funcionales mediante criterios verificables.', 'OE2. Modelar los tres actores y el flujo de reserva, identificando entidades, relaciones y colaboraciones mediante vistas de casos de uso, clases y secuencia.', 'OE3. Analizar los cinco principios SOLID y cuatro patrones solicitados, vinculando cada uno con componentes concretos y señalando sus límites de aplicación.', 'OE4. Documentar las pruebas unitarias y de integración y registrar el resultado reportado de 21 tests aprobados, diferenciándolo de métricas de cobertura, concurrencia y desempeño.']:p(txt)
h('Marco Teórico')
h('Procesos de software RUP Scrum y XP',2)
p('RUP organiza el ciclo de vida en inicio, elaboración, construcción y transición. Su carácter iterativo permite examinar requisitos y riesgos con progresiva precisión, mientras los casos de uso y la arquitectura orientan el trabajo (Kruchten, 2004). En StyleAgenda empleo estas fases como estructura académica de análisis, sin asignarles fechas ni hitos ejecutados que no estén documentados.')
p('Scrum articula objetivos, un Product Backlog ordenado, incrementos y revisión mediante inspección y adaptación. La definición de terminado permite explicitar cuándo un incremento cumple las condiciones acordadas (Schwaber & Sutherland, 2020). Al tratarse de autoría única, adapto la organización del backlog y la revisión del avance; no afirmo la existencia de un Scrum Team con responsabilidades independientes ni ceremonias celebradas.')
p('XP relaciona retroalimentación frecuente, diseño sencillo, pruebas automatizadas y refactorización (Beck & Andres, 2005). Su aplicación individual se expresa como criterio técnico: desarrollar cambios pequeños, comprobar reglas y mejorar la estructura sin alterar comportamiento. La existencia de tests no demuestra por sí misma desarrollo guiado por pruebas; tampoco permite afirmar programación en pareja o integración continua automatizada.')
h('Modelado UML',2)
p('UML proporciona elementos para describir estructura y comportamiento de sistemas (Object Management Group [OMG], 2017). Los casos de uso delimitan objetivos de los actores; las clases permiten describir entidades y contratos; la secuencia muestra el orden de mensajes durante una reserva. Estas vistas complementarias ayudan a revisar que la interfaz, los servicios y la persistencia respondan al mismo caso de negocio.')
h('Principios SOLID y Clean Code',2)
p('SOLID reúne responsabilidad única, abierto y cerrado, sustitución de Liskov, segregación de interfaces e inversión de dependencias. Los utilizo como criterios de revisión de cohesión, extensibilidad y acoplamiento, sin interpretarlos como una certificación binaria de calidad (Martin, 2002). Su aplicación debe contrastarse con dependencias concretas y contratos observables.')
p('Clean Code enfatiza nombres expresivos, funciones comprensibles y tratamiento claro de errores (Martin, 2008). En este proyecto esos criterios orientan la lectura de las operaciones de reserva y sus excepciones. Una función breve no garantiza claridad si combina varias instrucciones en una línea; por ello la legibilidad requiere revisar tanto la responsabilidad como la forma del código.')
h('Patrones de diseño GoF',2)
p('Los patrones GoF describen soluciones recurrentes de diseño orientado a objetos. Singleton controla la instancia de una clase; Factory Method delega la elección del producto a una operación de creación redefinible; Strategy encapsula algoritmos intercambiables; Observer comunica cambios a suscriptores (Gamma et al., 1995). Distingo estas intenciones del uso de Repository y de la arquitectura en capas, que no pertenecen a ese catálogo.')
h('Estrategias de testing',2)
p('Las pruebas unitarias ejercitan reglas acotadas con dependencias controladas; las de integración examinan colaboraciones entre componentes. pytest permite organizar tests, parametrizar entradas y compartir preparación mediante fixtures (pytest development team, s. f.). Un caso parametrizado puede generar varias ejecuciones, por lo que contar funciones no equivale a contar tests. La aceptación funcional requiere además contrastar resultados esperados con requerimientos.')
h('Desarrollo del Proyecto')
h('Enfoque híbrido académico',2)
p('Relaciono el inicio de RUP con la delimitación del problema y los actores. La elaboración corresponde a especificar intervalos, estados, permisos y separación de capas. La construcción agrupa los servicios, rutas, plantillas y pruebas presentes en el repositorio. La transición comprende instalación local, datos demostrativos y evaluación del prototipo. Esta correspondencia describe el proyecto; no constituye un registro de ejecución temporal de las fases.')
p('Organizo el backlog dando prioridad a la integridad de la reserva, seguida de consulta, modificación, control de acceso y supervisión. Para iteraciones cortas propongo seleccionar una historia, concretar su criterio de aceptación, implementar un cambio pequeño y revisar los tests relacionados antes de integrar. La refactorización debe conservar las respuestas observables. Esta adaptación combina organización del trabajo y disciplina técnica sin atribuir un historial de sprints al proyecto.')
table(1,'Historias de usuario y criterios de aceptación',['ID','Historia y prioridad','Criterio de aceptación'],[
('HU1','Como cliente quiero reservar un servicio con un barbero. Alta.','Una franja libre genera cita confirmada; un cruce se rechaza.'),
('HU2','Como cliente quiero cancelar mi reserva. Alta.','La cita queda cancelada y deja de bloquear el intervalo.'),
('HU3','Como cliente quiero reprogramar mi reserva. Alta.','La nueva franja se valida excluyendo la propia cita.'),
('HU4','Como barbero quiero consultar mi agenda. Media.','El portal muestra la agenda del barbero autenticado.'),
('HU5','Como administrador quiero gestionar usuarios y servicios. Media.','El acceso administrativo exige el rol ADMIN.'),
('HU6','Como administrador quiero observar eventos. Media.','El panel recibe registros de cambios mediante SSE.')],[.55,2.8,3.15])
h('Requerimientos y trazabilidad',2)
p('Las tablas siguientes convierten las necesidades en condiciones de revisión. La presencia de una función en el código no equivale a su validación completa. Los requisitos no funcionales se expresan como criterios verificables o metas pendientes, sin asignar cifras de rendimiento no medidas.')
table(2,'Requerimientos funcionales',['ID y vínculo','Requerimiento','Verificación prevista'],[
('RF1 HU1','Crear una cita con cliente, barbero, servicio e inicio.','Reserva persistida y estado CONFIRMED.'),('RF2 HU1','Rechazar cruces del mismo barbero.','Casos de solapamiento y contigüidad.'),('RF3 HU2','Cancelar una cita propia.','Estado CANCELLED y franja liberada.'),('RF4 HU3','Reprogramar una cita confirmada.','Cambio de intervalo y evento rescheduled.'),('RF5 HU4 HU5','Autenticar y restringir portales por rol.','Cliente recibe 403 al entrar a administración.'),('RF6 HU1','Calcular precio según estrategia aplicable.','Tarifa regular y descuentos del 10 % y 15 %.'),('RF7 HU6','Registrar y presentar eventos de citas.','Observer y revisión del flujo SSE.'),('RF8 HU5','Administrar catálogo y usuarios.','Revisión funcional de operaciones administrativas.')],[.9,2.8,2.8])
table(3,'Requerimientos no funcionales',['ID','Criterio','Alcance de verificación'],[
('RNF1','Sesión firmada con HttpOnly y SameSite=Lax.','Existe test de login y atributos de cookie.'),('RNF2','Separar reglas, presentación y persistencia.','Revisión de capas y dependencias.'),('RNF3','Conservar datos mediante SQLite.','Test de escritura y lectura de repositorio.'),('RNF4','Facilitar repetibilidad de pruebas.','Fixtures y parametrización; no mide cobertura.'),('RNF5','Evitar doble reserva bajo concurrencia.','Meta pendiente de prueba y control transaccional.'),('RNF6','Proteger el despliegue mediante HTTPS.','Configuración disponible; despliegue pendiente.')],[.6,3,2.9])
h('Modelado de actores clases y secuencia',2)
p('En la vista de casos de uso, Cliente se asocia con consultar servicios, reservar, cancelar y reprogramar; Barbero con consultar su agenda; Administrador con gestionar usuarios, servicios y observar eventos. Autenticarse es una precondición de los portales protegidos. Reservar incluye validar actores, calcular fin, comprobar disponibilidad y calcular precio. La cancelación y la reprogramación deben verificar además la titularidad o los permisos correspondientes.')
table(4,'Vista estructural para el modelo UML de clases',['Elemento','Relación y responsabilidad'],[
('User y roles','Admin, Barber y Client especializan el usuario de dominio.'),('BarberService','Corte, Barba y Combo representan productos de servicio.'),('Appointment','Relaciona un cliente, un barbero y un servicio; cada uno puede intervenir en muchas citas.'),('AppointmentService','Colabora con repositorios, AvailabilityService, PricingService y AppointmentSubject.'),('PricingStrategy','Contrato realizado por las estrategias de tarifa.'),('AppointmentSubject','Mantiene cero o más observadores con operación update.')],[1.8,4.7])
p('La secuencia de reserva se expresa así: Cliente → router → AppointmentService.book → repositorios de usuarios y servicios → AvailabilityService → AppointmentRepository.overlapping → PricingService → AppointmentRepository.add → commit → AppointmentSubject.notify → observadores → respuesta. Si hay cruce, la validación interrumpe el flujo antes de agregar la cita. Si el commit falla, la operación revierte la transacción. La notificación ocurre después de persistir y no convierte un correo demostrativo en una entrega externa real.')
h('Arquitectura Principios SOLID y Patrones de Diseño GoF')
h('Arquitectura limpia en capas y sus límites',2)
p('La presentación reside en app/web, con routers, esquemas y plantillas Jinja2; app/services coordina casos de uso; app/domain contiene entidades, excepciones y contratos; app/repositories encapsula consultas; app/infrastructure contiene SQLite, modelos ORM y adaptadores de notificación. app/core concentra configuración, seguridad y composición. FastAPI atiende HTTP, SQLAlchemy gestiona persistencia y SQLite almacena datos; Bootstrap y JavaScript apoyan los portales.')
p('La solución toma como orientación la separación propia de una arquitectura limpia, pero el desacoplamiento es parcial: AppointmentService importa Session y modelos ORM, y construye repositorios concretos. Por tanto, la lógica de aplicación todavía conoce detalles de persistencia. La mejora consiste en definir puertos de repositorio e inyectar sus implementaciones desde la composición, conservando el dominio independiente de SQLAlchemy.')
h('Seguridad de sesión y autorización',2)
p('SessionMiddleware utiliza styleagenda_session con firma, duración de ocho horas y SameSite=Lax. HttpOnly impide el acceso normal a la cookie desde JavaScript; la firma permite detectar modificaciones, pero no cifra su contenido. La documentación de Starlette diferencia estas propiedades y la opción https_only para marcar Secure (Starlette, s. f.). En StyleAgenda esa opción depende de la configuración del despliegue.')
p('Las vistas consultan de nuevo el usuario en SQLite y verifican el rol. El test de sesión comprueba redirección tras login, acceso del cliente, rechazo del portal administrador y cierre de sesión. Las contraseñas se verifican mediante Argon2. Estas medidas no acreditan una auditoría completa: deben revisarse también los permisos de todas las rutas, la protección contra solicitudes falsificadas y el manejo de secretos antes de un uso público.')
h('Aplicación de los cinco principios SOLID',2)
p('Responsabilidad única. AvailabilityService concentra la validación temporal, PricingService decide la tarifa y los repositorios aíslan consultas. AppointmentService orquesta el caso de uso. Esta distribución permite revisar la regla de cruce sin recorrer plantillas ni mecanismos de notificación.')
p('Abierto y cerrado. PricingStrategy permite agregar algoritmos de precio conservando un contrato común; AppointmentSubject admite nuevos observadores. La selección de estrategias y los registros de las fábricas todavía requieren modificaciones cuando aparecen tipos nuevos, de modo que la extensibilidad tiene puntos de cambio explícitos.')
p('Sustitución de Liskov. Las estrategias deben aceptar el mismo precio base y devolver un Decimal con significado consistente. Los observadores deben responder a update sin exigir datos incompatibles con el evento. Los tests de precios ofrecen ejemplos del contrato, pero no demuestran todas las precondiciones y postcondiciones de cada subtipo.')
p('Segregación de interfaces. PricingStrategy expone calculate y AppointmentObserver expone update. Estos contratos reducidos evitan imponer al cálculo de precio operaciones de persistencia o al observador funciones de agenda. Su tamaño favorece implementaciones enfocadas.')
p('Inversión de dependencias. El sujeto observa un contrato abstracto y el servicio puede recibir un sujeto o un calculador de precios. Sin embargo, la dependencia directa de Session y los repositorios concretos limita el cumplimiento del principio. La arquitectura satisface parcialmente esta orientación y requiere puertos de persistencia para profundizarla.')
h('Clean Code aplicado al proyecto',2)
p('Los nombres book, cancel, reschedule y assert_available comunican la intención de los casos de uso. ConflictError, ValidationError y NotFoundError distinguen fallos de negocio. El método _commit_and_notify concentra una secuencia compartida y reduce duplicación. Como mejora identifico instrucciones compactadas en una sola línea y la captura general de excepciones en la notificación: conviene separar instrucciones, concretar los errores esperados y mantener registros que permitan diagnosticar cada listener.')
h('Singleton en SQLiteDatabase',2)
p('SQLiteDatabase conserva una instancia, un engine y una fábrica de sesiones. El bloqueo en __new__ protege la creación de la instancia; cada unidad de trabajo obtiene su propia Session mediante session(). Esto evita confundir motor compartido con una sesión global. reset_for_tests permite reiniciar el estado entre pruebas. El patrón es de alcance de proceso y no equivale a una instancia única entre múltiples servidores; tampoco demuestra por sí solo seguridad concurrente de toda la inicialización.')
h('Factory Method en UserFactory y ServiceFactory',2)
p('UserFactory.create selecciona Admin, Barber o Client mediante un registro de roles. ServiceFactory.create selecciona Corte, Barba o Combo, normaliza el tipo y aplica valores predeterminados. El repositorio denomina esta solución Factory Method. Frente a la definición GoF, la implementación concreta corresponde principalmente a una fábrica simple parametrizada: no existe una jerarquía de creadores que redefina el método de fabricación. Presento esta precisión para distinguir la intención académica del mecanismo implementado.')
p('La centralización permite comprobar tipos soportados y errores de entrada sin duplicar construcción en cada ruta. Para aplicar Factory Method en su forma canónica podría introducir creadores especializados con una operación de creación redefinida. Esa variante es una posibilidad de evolución y no una estructura presente en el código.')
h('Strategy en PricingStrategy y PricingService',2)
p('PricingStrategy declara calculate y las implementaciones encapsulan tarifa regular, descuento de cliente frecuente y promoción entre semana. PricingService prioriza la promoción del 15 % de lunes a viernes; fuera de ese caso aplica 10 % al cliente frecuente o la tarifa regular. Los descuentos no se acumulan. Con base 20 000, los tests expresan 20 000 en tarifa regular, 18 000 para frecuente en fin de semana y 17 000 en promoción.')
p('La reserva considera frecuente al cliente con al menos cinco registros de cita obtenidos por list_for_client. La consulta actual no filtra por estado; por ello ese umbral no debe describirse como cinco servicios completados. La reprogramación cambia las fechas, pero no recalcula el precio en el método examinado. Ambas decisiones requieren definición de negocio si el prototipo evoluciona.')
h('Observer y transmisión de eventos mediante SSE',2)
p('AppointmentSubject mantiene observadores y distribuye eventos mediante update. La composición registra EmailListener y LogListener. Tras confirmar la transacción se notifican confirmación, cancelación o reprogramación. EmailListener registra un aviso demostrativo; no implementa entrega SMTP ni confirma recepción de correo.')
p('El registro de eventos alimenta un buffer en memoria que el panel administrativo consulta mediante Server-Sent Events. Observer resuelve la colaboración interna y SSE transporta registros hacia el navegador: son responsabilidades distintas. El buffer tiene capacidad limitada y se pierde al reiniciar el proceso, de manera que no funciona como auditoría persistente ni como cola confiable. Si un observador lanza una excepción, el recorrido puede interrumpirse y omitir los posteriores; la cita ya confirmada no se revierte.')
h('Validación matemática de intervalos semiabiertos',2)
p('Represento cada cita como A = [a, b), con a < b. La hora de inicio pertenece al intervalo y la de finalización queda excluida. Para una nueva cita N = [c, d), existe cruce si y solo si a < d y b > c. La consulta aplica estas desigualdades a citas del mismo barbero que no estén canceladas. Al reprogramar se excluye el identificador de la propia cita.')
p('Por ejemplo, [09:00, 09:30) y [09:30, 10:00) son compatibles porque 09:30 > 09:30 es falso en la condición pertinente. En cambio, [09:15, 09:45) se superpone con la primera. AvailabilityService rechaza además un inicio mayor o igual al final. Esta regla resuelve intervalos comparados secuencialmente; la lectura de disponibilidad seguida de inserción no garantiza exclusión mutua entre solicitudes simultáneas.')
p('El código elimina tzinfo de las fechas recibidas sin convertirlas primero a una zona común. En el prototipo ello supone interpretar las horas bajo una convención local. Para operación distribuida propongo normalizar fechas y zona horaria explícitamente, y agregar casos que verifiquen conversiones y límites del día.')
h('Testing y Calidad de Software')
h('Estrategia y evidencia de evaluación',2)
p('La suite se organiza en tests/unit y tests/integration. Las pruebas unitarias verifican fábricas, instancia compartida, precios e intervalos con un repositorio falso. Las de integración combinan servicios, SQLAlchemy, SQLite y un cliente HTTP de prueba. Las fixtures preparan recursos y la parametrización repite verificaciones para roles, servicios y formas de solapamiento.')
p('El resultado reportado para StyleAgenda es de 21 tests aprobados. Este valor se conserva como antecedente de evaluación y no como una ejecución nueva de esta documentación. La tabla identifica familias de casos existentes y sus resultados esperados; no asigna un aprobado individual a cada fila ni supone que el estado actual del repositorio corresponda exactamente a la corrida reportada. Tampoco se dispone de una medición que permita afirmar cobertura porcentual, tiempo de ejecución o ausencia total de defectos.')
table(5,'Casos de prueba identificados y trazabilidad',['Caso y tipo','Condición y resultado esperado','Vínculo'],[
('CP1 Unitaria','Dos solicitudes de SQLiteDatabase conservan instancia, motor y fábrica.','OE3 RNF2'),('CP2 Unitaria','ADMIN, BARBER y CLIENT crean el subtipo esperado.','RF5'),('CP3 Unitaria','Corte, Barba y Combo crean servicios; tipos desconocidos fallan.','RF8'),('CP4 Unitaria','En fin de semana se conserva el precio regular.','RF6'),('CP5 Unitaria','Cliente frecuente en fin de semana obtiene 10 % de descuento.','RF6'),('CP6 Unitaria','La promoción entre semana aplica 15 % con prioridad.','RF6'),('CP7 Unitaria','Los intervalos contiguos se aceptan.','RF2'),('CP8 Unitaria','Cruce parcial, contención e igualdad se rechazan.','RF2'),('CP9 Unitaria','Una cita cancelada no bloquea disponibilidad.','RF3'),('CP10 Integración','La reserva persiste y una reserva superpuesta falla.','RF1 RF2'),('CP11 Integración','Se aceptan citas contiguas y se reutiliza una franja cancelada.','RF2 RF3'),('CP12 Integración','Reservar y reprogramar emiten eventos al observador.','RF4 RF7'),('CP13 Integración','Un usuario escrito puede recuperarse por correo.','RNF3'),('CP14 Integración','Login configura cookie, restringe administración y logout cierra acceso.','RF5 RNF1')],[1.15,4.1,1.25])
h('Interpretación de resultados y límites',2)
p('Los casos identificados son pertinentes para las reglas centrales: continuidad de franjas, rechazo de cruces, cálculo de precio y persistencia de citas. El caso HTTP añade evidencia sobre sesión y restricción de un portal. El número de ejecuciones depende de la parametrización y del estado de la suite; por ello los 21 tests reportados no deben redistribuirse artificialmente entre categorías sin el informe correspondiente.')
p('No se documentan pruebas de carga, reservas simultáneas, recuperación tras reinicio, entrega real de correo ni evaluación de usabilidad. También falta extender la verificación de permisos a todas las operaciones y probar de manera explícita errores de listeners. Para reproducir la evaluación se debe conservar la revisión del código, las dependencias instaladas, el comando python -m pytest -q y el informe íntegro de la corrida. Estos elementos permitirían contrastar futuras regresiones con una base identificable.')
h('Conclusiones y Trabajo Futuro')
p('StyleAgenda materializa un prototipo individual de agenda para barbería con operaciones de reserva, cancelación y reprogramación, roles diferenciados y persistencia en SQLite. La regla de intervalos semiabiertos permite explicar con precisión cuándo dos citas del mismo barbero son incompatibles y por qué las citas contiguas pueden aceptarse.')
p('La articulación académica de Design Thinking, RUP, Scrum y XP ofrece una relación entre necesidades, modelado, organización del trabajo y verificación. Su alcance es una adaptación individual: el proyecto no acredita investigación de campo, una implementación completa de Scrum ni un historial documentado de prácticas XP. Esta distinción permite mantener las conclusiones proporcionales a la evidencia.')
p('La separación de capas y los contratos de estrategias y observadores facilitan el análisis de SOLID. El Singleton tiene alcance de proceso y las fábricas centralizan la creación; su comparación con Factory Method identifica una oportunidad de profundización conceptual. El acoplamiento directo con SQLAlchemy muestra que la inversión de dependencias y la arquitectura limpia son parciales.')
p('Los 21 tests aprobados reportados constituyen el resultado de evaluación disponible, sin justificar extrapolaciones sobre cobertura total o preparación para producción. Como prioridad futura propongo asegurar reservas concurrentes mediante una estrategia transaccional comprobada, normalizar zonas horarias y ampliar las pruebas de autorización. Después conviene incorporar correo real con reintentos, almacenamiento duradero de eventos y evaluación con usuarios, con consentimiento y criterios de éxito definidos.')
p('Para cerrar el ciclo académico, cada mejora debería incorporarse al backlog con criterio de aceptación y evidencia reproducible. La evaluación con barberías podría medir reservas incompatibles rechazadas, tiempo de gestión y comprensión de los portales, pero sus valores deberán obtenerse mediante un protocolo de medición antes de presentarse como resultados.')
d.add_page_break()
h('Referencias Bibliográficas')
refs=[
('Beck, K., & Andres, C. (2005). ','Extreme programming explained: Embrace change',' (2nd ed.). Addison-Wesley. https://www.informit.com/store/extreme-programming-explained-embrace-change-9780321278654'),
('Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1995). ','Design patterns: Elements of reusable object-oriented software','. Addison-Wesley. https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480'),
('Hasso Plattner Institute of Design at Stanford University. (s. f.). ','Get started with design','. https://dschool.stanford.edu/innovate/tools/get-started-with-design'),
('Kruchten, P. (2004). ','The rational unified process: An introduction',' (3rd ed.). Addison-Wesley. https://www.informit.com/store/rational-unified-process-an-introduction-9780321197702'),
('Martin, R. C. (2002). ','Agile software development: Principles, patterns, and practices','. Prentice Hall. https://www.informit.com/store/agile-software-development-principles-patterns-and-9780135974445'),
('Martin, R. C. (2008). ','Clean code: A handbook of agile software craftsmanship','. Prentice Hall. https://www.informit.com/content/images/9780132350884/samplepages/9780132350884.pdf'),
('Object Management Group. (2017). ','OMG Unified Modeling Language',' (Version 2.5.1). https://www.omg.org/spec/UML/2.5.1'),
('pytest development team. (s. f.). ','pytest documentation','. https://docs.pytest.org/en/stable/'),
('Schwaber, K., & Sutherland, J. (2020). ','The Scrum guide: The definitive guide to Scrum: The rules of the game','. https://scrumguides.org/scrum-guide.html'),
('Starlette. (s. f.). ','Middleware','. https://starlette.dev/middleware/')]
for author,title,end in refs:
 a=d.add_paragraph();a.paragraph_format.left_indent=Inches(.5);a.paragraph_format.first_line_indent=Inches(-.5)
 a.add_run(author);a.add_run(title).italic=True;a.add_run(end)
for a in d.paragraphs:
 for r in a.runs:
  r.font.color.rgb=RGBColor(0,0,0)
lang=OxmlElement('w:lang');lang.set(qn('w:val'),'es-CO');d.styles['Normal']._element.get_or_add_rPr().append(lang)
d.save(OUT/'StyleAgenda_documento_academico.docx')
print(OUT/'StyleAgenda_documento_academico.docx')
