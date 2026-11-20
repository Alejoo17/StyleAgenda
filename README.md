# StyleAgenda

Aplicación web de gestión y reservas para una barbería. El backend utiliza **Python 3.12 o superior**, **FastAPI**, **SQLAlchemy 2.x** y **SQLite**. Los portales web usan **Jinja2**, **Bootstrap 5** y JavaScript.

## Arquitectura

El proyecto organiza el código en capas:

- `app/web/`: rutas HTTP, esquemas y portales.
- `app/services/`: coordinación de los casos de uso.
- `app/domain/`: entidades, reglas de negocio, tarifas y contratos de notificación.
- `app/repositories/`: consultas y persistencia de usuarios, servicios y citas.
- `app/infrastructure/`: SQLite, modelos ORM y adaptadores de notificación.
- `app/core/`: configuración, seguridad, autenticación y dependencias.
- `tests/unit/` y `tests/integration/`: pruebas unitarias y de integración.

Las rutas principales de la interfaz son `/auth/login`, `/appointments/` (cliente), `/barbers/` (barbero) y `/admin/` (administrador). La API se publica bajo `/api`; la documentación interactiva está en `/docs`.

## Patrones de diseño y conceptos aplicados

- **Singleton:** `app/infrastructure/sqlite_database.py` mantiene un motor y una fábrica de sesiones. Cada unidad de trabajo obtiene su propia sesión.
- **Fábricas:** `UserFactory` crea usuarios `ADMIN`, `BARBER` o `CLIENT`; `ServiceFactory` construye servicios `Corte`, `Barba` o `Combo`. En el código son fábricas parametrizadas.
- **Strategy:** `PricingStrategy` define el contrato de cálculo. Se implementan tarifa regular, descuento de cliente frecuente y promoción entre semana. La promoción de lunes a viernes (15 %) prevalece; en otro caso se aplica el descuento frecuente (10 %) o la tarifa regular.
- **Observer:** `AppointmentSubject` notifica cambios de citas a `LogListener` y `EmailListener`. El aviso por correo es demostrativo y queda registrado; no envía correo real. El panel administrativo muestra eventos mediante Server-Sent Events (SSE).
- **Repository y capas:** los repositorios encapsulan consultas SQLAlchemy y las rutas separan presentación de reglas de negocio.

## Requisitos previos

- Python **3.12 o superior**.
- Conexión a Internet durante la instalación de dependencias de PyPI.
- PowerShell en Windows, o una terminal de macOS/Linux.

Ejecute los comandos desde la carpeta raíz del proyecto, donde están `pyproject.toml`, `seed.py` y `README.md`.

## Instalación y ejecución en Windows

### 1. Extraer el código

Descomprima `StyleAgenda_codigo.zip` en una carpeta, por ejemplo `C:\StyleAgenda`, y abra PowerShell en esa carpeta. Confirme que `pyproject.toml` aparece al ejecutar `Get-ChildItem`.

### 2. Crear un entorno e instalar dependencias

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Si el equipo tiene otra versión compatible de Python (3.13 o posterior), sustituya `-3.12` por la versión instalada, por ejemplo `py -3.13`. Si PowerShell bloquea la activación del entorno, no cambie la política del equipo: use el ejecutable del entorno directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

En los siguientes pasos, use `python` si activó el entorno; si no, anteponga `.\.venv\Scripts\python.exe` al comando.

### 3. Crear la base de datos y los datos de demostración

```powershell
python seed.py
```

Este comando crea el esquema SQLite y carga, si aún no existen, las cuentas de demostración, cuatro servicios y citas iniciales. La base de datos local queda en `data/styleagenda.db`. Ejecútelo desde la raíz del proyecto para que la aplicación y el script usen la misma base.

### 4. Iniciar la aplicación

```powershell
python -m uvicorn app.main:app --reload
```

Abra estas direcciones en el navegador:

- Aplicación e inicio de sesión: <http://127.0.0.1:8000/>
- Estado de la aplicación: <http://127.0.0.1:8000/health>
- Documentación de la API: <http://127.0.0.1:8000/docs>

Para detener el servidor, vuelva a PowerShell y presione **Ctrl+C**.

## Instalación y ejecución en macOS o Linux

Desde la carpeta raíz del proyecto:

```bash
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python seed.py
python -m uvicorn app.main:app --reload
```

Luego abra <http://127.0.0.1:8000/>. Detenga el servidor con **Ctrl+C**.

## Cuentas de demostración

Todas las cuentas creadas por `seed.py` usan la contraseña `StyleAgenda123!`.

| Rol | Usuario |
| --- | --- |
| Administrador | `admin@styleagenda.local` |
| Barberos | `barbero1@styleagenda.local`, `barbero2@styleagenda.local`, `barbero3@styleagenda.local` |
| Clientes | `cliente1@styleagenda.local` hasta `cliente8@styleagenda.local` |

Los accesos rápidos de la pantalla de inicio de sesión son para demostraciones locales.

## Ejecutar las pruebas

Con el entorno virtual activo:

```powershell
python -m pytest -q
```

En macOS/Linux se usa el mismo comando. Muestre y reporte exactamente el resultado que aparezca en esa máquina; el número de pruebas puede variar si el código o las dependencias cambian.

La suite cubre Singleton, fábricas, estrategias de precios, intervalos semiabiertos, cancelación, reprogramación, eventos Observer, persistencia y sesiones web.

## Configuración opcional

Para cambiar la configuración local, copie `.env.example` a `.env` y ajuste las variables necesarias:

- `STYLEAGENDA_DATABASE_URL`: URL de la base de datos. Por defecto usa `sqlite:///./data/styleagenda.db`.
- `STYLEAGENDA_SESSION_SECRET`: clave usada para firmar la sesión.
- `STYLEAGENDA_SESSION_HTTPS_ONLY`: use `false` para una demostración local por HTTP. En un despliegue HTTPS debe configurarse `true` y emplearse una clave privada aleatoria.

No reutilice la clave de ejemplo ni las cuentas de demostración en un despliegue público. El correo del `EmailListener` es simulado y el registro SSE se conserva en memoria.



