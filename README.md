# StyleAgenda

Aplicación web de gestión y reservas para barbería. El backend usa **Python 3.12+**, **FastAPI**, **SQLAlchemy 2.x** y **SQLite**; los portales HTML usan **Jinja2**, **Bootstrap 5** y JavaScript.

## Arquitectura

La solución organiza el código en capas: `app/web/` recibe peticiones HTTP y presenta las vistas; `app/services/` coordina los casos de uso; `app/domain/` contiene reglas, entidades y patrones; `app/repositories/` encapsula consultas; `app/infrastructure/` implementa SQLite y adaptadores de notificación; `app/core/` contiene configuración, seguridad y dependencias.

Las rutas web son `/auth/login`, `/appointments/` (cliente), `/barbers/` (barbero) y `/admin/` (administrador). Las sesiones se firman con `SessionMiddleware`, guardan el ID de usuario, usan cookies `HttpOnly` con `SameSite=Lax` y expiran a las ocho horas. Las vistas vuelven a comprobar el usuario contra SQLite y aplican control de acceso por rol. En despliegue HTTPS, establecer `STYLEAGENDA_SESSION_HTTPS_ONLY=true` y reemplazar `STYLEAGENDA_SESSION_SECRET` por una clave aleatoria privada. Los accesos rápidos del login son para demostración local.

## Patrones de diseño en código

- **Singleton:** `app/infrastructure/sqlite_database.py` — `SQLiteDatabase` mantiene un motor y fábrica de sesiones únicos. Cada solicitud abre su propia sesión.
- **Factory Method:** `app/services/user_factory.py` — `UserFactory` crea `ADMIN`, `BARBER` o `CLIENT`; `app/services/service_factory.py` — `ServiceFactory` construye `Corte`, `Barba` o `Combo`.
- **Strategy:** `app/domain/pricing/strategy.py` define `PricingStrategy`; `regular.py`, `frequent_client.py` y `weekday_promotion.py` implementan las tarifas concretas. `app/services/pricing_service.py` elige estrategia: promoción de lunes a viernes (15%) prevalece; si no, cliente frecuente (10% tras cinco citas); de lo contrario, tarifa regular. El portal consulta esta misma lógica para mostrar precio y nombre de estrategia.
- **Observer:** `app/domain/notifications/appointment_subject.py` mantiene observadores; `app/domain/notifications/observer.py` define la interfaz; `app/infrastructure/notifications/log_listener.py` y `email_listener.py` escuchan confirmación, reprogramación y cancelación. El listener email es demostrativo y registra el aviso (no envía correo). `event_log.py` mantiene un buffer en memoria y el panel administrador lo muestra mediante Server-Sent Events.
- **Repository:** `app/repositories/` encapsula lecturas y escrituras SQLAlchemy para usuarios, servicios y citas.
- **Capas / MVC:** routers y esquemas en `app/web/`, plantillas en `app/web/templates/`, JavaScript/CSS en `app/static/`, reglas de negocio en `app/services/` y `app/domain/`.

## Instalación y ejecución local (PowerShell)

```powershell
python --version  # debe ser 3.12 o superior
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Poblar la base SQLite con un administrador, tres barberos, ocho clientes, cuatro servicios y ocho citas iniciales:

```powershell
python seed.py
```

Todas las cuentas usan `StyleAgenda123!`:

- Admin: `admin@styleagenda.local`
- Barberos: `barbero1@styleagenda.local`, `barbero2@styleagenda.local`, `barbero3@styleagenda.local`
- Clientes: `cliente1@styleagenda.local` hasta `cliente8@styleagenda.local`

Iniciar la aplicación:

```powershell
uvicorn app.main:app --reload
```

Abrir <http://127.0.0.1:8000/> para iniciar sesión; `/docs` muestra la API y `/health` informa estado. La cookie de sesión se configura localmente sin requisito HTTPS. Para otro secreto o base de datos, copiar `.env.example` a `.env` y configurar `STYLEAGENDA_SESSION_SECRET`, `STYLEAGENDA_SESSION_HTTPS_ONLY` o `STYLEAGENDA_DATABASE_URL`.

## Pruebas

```powershell
python -m pytest -q
```

La suite comprueba singleton, fábricas, estrategias de precios, intervalos semiabiertos, cancelaciones, reprogramación, eventos Observer y persistencia.
