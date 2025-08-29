# Modulo-5-Multi-Tenancy

Este proyecto corresponde al **Módulo 5** del sistema, enfocado en la gestión de citas médicas con arquitectura **multi-tenancy** usando **Python**, **Django** y **MySQL**.  
La estructura del módulo permite que varias clínicas (tenants) trabajen de forma aislada y segura dentro de la misma aplicación, cumpliendo todos los criterios del ejercicio solicitado.

---

## Product Backlog – Historias de Usuario

- **HU01 – Configuración del Entorno de Desarrollo**
  - Como desarrollador, quiero configurar el entorno (venv, `requirements.txt`, conexión MySQL en `settings.py`) para ejecutar el proyecto localmente.
  - Criterios de aceptación:
    - Entorno virtual creado y activado.
    - Dependencias instaladas desde `requirements.txt`.
    - Conexión a MySQL operativa y migraciones aplicadas sin errores.

- **HU02 – Gestión de Citas por Clínica (CRUD)**
  - Como recepcionista de una clínica, quiero crear, listar, actualizar y eliminar citas pertenecientes a mi clínica.
  - Criterios de aceptación:
    - Operaciones CRUD disponibles para citas de la clínica del usuario.
    - Validaciones mínimas: fecha/hora obligatoria y relación con paciente.
    - Un usuario no puede ver/editar citas de otras clínicas.

- **HU03 – Multi‑Tenancy en Citas**
  - Como sistema, al crear una cita debe asignarse automáticamente la clínica (tenant) del usuario autenticado, y todas las consultas deben filtrar por dicho tenant.
  - Criterios de aceptación:
    - Asignación automática de `clinica` al crear citas.
    - Aislamiento de datos en `admin.py` y vistas: cada usuario ve solo datos de su clínica.

- **HU04 – Acceso y Visualización (Admin/Calendario)**
  - Como usuario autenticado, quiero acceder al Admin y visualizar las citas filtradas por mi clínica.
  - Criterios de aceptación:
    - Permisos aplicados en `admin.py` por clínica.
    - Listados y filtros del Admin muestran únicamente datos del tenant del usuario.

> Entregable: las citas de Clínica A no se mezclan con las de Clínica B.

---

## Sprint Goal

Implementar la lógica de Multi‑Tenancy para la gestión de citas, asegurando que cada clínica solo vea sus propias citas y que las nuevas se asignen correctamente.

---

## Estructura del Proyecto

```
Modulo-5-Multi-Tenancy/
│
├── .github/                    # Configuración de CI (GitHub Actions)
│   └── workflows/
│       └── ci.yml              # Pipeline: MySQL en Docker + migrate de Django
│
├── inventory_project/         # Configuración global del proyecto Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py            # Configuración de MySQL y variables de entorno
│   ├── urls.py
│   └── wsgi.py
│
├── multi_tenant_citas/        # App principal de citas multi-tenant
│   ├── migrations/            # Migraciones de la app
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py               # Admin: permisos por clínica (tenant)
│   ├── apps.py
│   ├── models.py              # Models: vínculos Clinica, Paciente y Cita
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── requirements.txt
└── README.md                  # Documentación del módulo
```

- **.github/workflows/**: Workflows de GitHub Actions para CI. `ci.yml` levanta MySQL en Docker y valida con `python manage.py migrate`.
- **inventory_project/**: Configuración global del proyecto Django. En `settings.py` se definen la conexión MySQL y el uso de variables de entorno.
- **multi_tenant_citas/**: Lógica de negocio, modelos, vistas, administración y pruebas del módulo de citas multi-tenant.
- **manage.py**: Punto de entrada para ejecutar comandos de Django.
- **requirements.txt**: Dependencias del proyecto (versionadas para reproducibilidad).

---

## Integración Continua (CI) con GitHub Actions

La carpeta `.github/workflows/` contiene el pipeline de validación. El archivo `ci.yml` levanta un contenedor efímero de **MySQL** con Docker y valida la estructura del proyecto ejecutando las migraciones de Django.

- **Archivo**: `.github/workflows/ci.yml`
- **Disparadores**: `push` y `pull_request` a las ramas `Multi-Tenancy` y `Testeo-de-github-actions`.
- **Runner**: `ubuntu-latest`.
- **Servicio Docker (MySQL 8.0)**:
  - Variables del servicio: `MYSQL_ROOT_PASSWORD=mysql`, `MYSQL_DATABASE=multi_tenancy_citas`.
  - Puerto publicado: `3306`.
  - Healthcheck para esperar a que MySQL esté listo.
- **Pasos principales**:
  1. Checkout del repositorio.
  2. Setup de Python 3.11 y instalación de dependencias con `pip install -r requirements.txt`.
  3. Exporta `DATABASE_URL` al entorno de GitHub (variable actualmente no usada por `settings.py`).
  4. Espera breve a que MySQL esté listo.
  5. Ejecuta `python manage.py migrate`.

### ¿Qué valida este pipeline?

La validación real sucede en el paso `python manage.py migrate`. Django lee los modelos de `multi_tenant_citas/models.py` y sus migraciones; si no hay errores, crea todas las tablas en el contenedor MySQL. Que este paso termine con éxito confirma que:

- La configuración de la base de datos es correcta.
- Los modelos y migraciones son coherentes.
- El proyecto es ejecutable en un ambiente limpio y reproducible.

### Variables de entorno y `settings.py`

En `inventory_project/settings.py` se importa `os` y se emplea `os.environ.get()` para leer credenciales y parámetros de conexión:

```python
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'multi_tenancy_citas'),
        'USER': os.environ.get('MYSQL_USER', 'root'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'mysql'),
        'HOST': os.environ.get('MYSQL_HOST', '127.0.0.1'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
    }
}
```

- En GitHub Actions, el workflow levanta MySQL con `MYSQL_ROOT_PASSWORD` y `MYSQL_DATABASE` dentro del servicio Docker. Aunque el job no exporta `MYSQL_*` al entorno del runner, los valores por defecto en `settings.py` coinciden con los del servicio (`root`/`mysql`, DB `multi_tenancy_citas`, host `127.0.0.1`, puerto `3306`), por lo que la conexión funciona.
- Opcionalmente, podrías alinear el workflow para exportar explícitamente `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT` en lugar de `DATABASE_URL`, o adaptar `settings.py` para leer `DATABASE_URL` si prefieres ese patrón.

### ¿Por qué es clave usar `os.environ`?

Sin `import os` y sin leer variables de entorno, el proyecto quedaría rígido y vulnerable:

- No podría adaptarse a distintos entornos (tu máquina local vs. GitHub Actions).
- Forzaría credenciales fijas en el código, dificultando la seguridad y el versionado.
- Impediría reproducibilidad en CI/CD y despliegues, al no poder inyectar configuraciones por ambiente.

Con el enfoque actual, el proyecto funciona tanto localmente (usando los valores por defecto si no existen variables) como en CI (donde puedes sobreescribirlos via variables de entorno).

---

## Enlace del Trello

Tablero del proyecto: https://trello.com/b/3GnQSD8c/modulo-5-multi-tenancy

## Enlace de Video

Video de presentación: https://drive.google.com/drive/folders/18vsA0t_8kClk4LFGlw3Vxr1FjSofkfvx

---

## Proceso de ejecución

Se usa `requirements.txt` para administrar y replicar el entorno de dependencias y ejecutar el proyecto.

- **Crear y activar el entorno virtual (Windows):**
  ```powershell
  python -m venv env
  .\env\Scripts\activate
  ```

- **Instalar todas las dependencias del proyecto:**
  ```powershell
  pip install -r requirements.txt
  ```

- **Ejecutar migraciones después de instalar dependencias:**
  Para crear las tablas desde los modelos de Django
  ```powershell
  python manage.py makemigrations
  python manage.py migrate
  ```

- **Si instalas nuevas librerías, actualiza `requirements.txt`:**
  ```powershell
  pip install nombre-paquete==X.Y.Z
  pip freeze > requirements.txt
  ```

- **Actualizar dependencias existentes según `requirements.txt`:**
  ```powershell
  pip install -r requirements.txt --upgrade
  ```

Notas:
- En Windows, `mysqlclient` puede requerir herramientas de compilación de Visual C++.
- Usa versiones fijas (`==`) para asegurar entornos reproducibles.

---

## ¿Qué es Multi-Tenancy?

Multi-tenancy es una arquitectura donde una sola instancia de la aplicación sirve a múltiples clientes (tenants), en este caso clínicas.  
Cada clínica accede únicamente a sus propios datos, garantizando privacidad y separación total.

---

## Ejercicio Evaluado

- **Relacionar citas con un tenant (clínica):**  
  Cada cita está asociada a una clínica específica.

- **Probar que cada clínica solo pueda ver sus propias citas:**  
  El sistema filtra las citas por clínica, asegurando el aislamiento de datos.

- **Validar que al crear citas nuevas se asignen automáticamente al tenant del usuario que las crea:**  
  Al crear una cita, se asigna automáticamente la clínica del usuario autenticado.

- **Entregable:**  
  Las citas de Clínica A no se mezclan con las de Clínica B.

---

## Base de Datos (MySQL)

El proyecto utiliza **MySQL**.  
Script completo para entorno local (incluye tablas de Django y datos de ejemplo):

```sql
CREATE DATABASE multi_tenancy_citas;
USE multi_tenancy_citas;

CREATE TABLE clinica (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    direccion VARCHAR(255)
);

INSERT INTO clinica (id, nombre, direccion) VALUES
(1, 'Clínica Nova', 'Miraflores'),
(2, 'Bienestar Integral', 'Surco');

CREATE TABLE paciente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    apellido VARCHAR(255) NOT NULL,
    fecha_nacimiento DATE,
    clinica_id INT NOT NULL,
    FOREIGN KEY (clinica_id) REFERENCES clinica(id)
);

INSERT INTO paciente (id, nombre, apellido, fecha_nacimiento, clinica_id) VALUES
(1, 'Ana', 'Pérez', '1990-05-15', 1),
(2, 'Juan', 'Gómez', '1985-11-20', 2);

CREATE TABLE cita (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME NOT NULL,
    motivo TEXT,
    estado VARCHAR(1) NOT NULL DEFAULT 'P',
    paciente_id INT NOT NULL,
    clinica_id INT NOT NULL,
    FOREIGN KEY (paciente_id) REFERENCES paciente(id),
    FOREIGN KEY (clinica_id) REFERENCES clinica(id)
);

INSERT INTO cita (id, fecha_hora, motivo, paciente_id, clinica_id) VALUES
(1, '2025-08-28 10:00:00', 'Consulta general', 1, 1),
(2, '2025-08-28 11:30:00', 'Revisión anual', 2, 2);

CREATE TABLE auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    last_login DATETIME(6) NULL,
    date_joined DATETIME(6) NOT NULL
);

ALTER TABLE auth_user
ADD COLUMN first_name VARCHAR(150) NOT NULL,
ADD COLUMN last_name VARCHAR(150) NOT NULL;

INSERT INTO auth_user (id, password, is_superuser, username, email, is_staff, is_active, date_joined) VALUES
(1, 'hash_contrasena_admin', 1, 'admin', 'admin@ejemplo.com', 1, 1, NOW()),
(2, 'hash_contrasena_clinica_a', 0, 'usuario_clinica_a', 'a@ejemplo.com', 1, 1, NOW()),
(3, 'hash_contrasena_clinica_b', 0, 'usuario_clinica_b', 'b@ejemplo.com', 1, 1, NOW()),
(4, 'hash_contrasena_paciente_a', 0, 'paciente_a', 'paciente_a@ejemplo.com', 0, 1, NOW());

CREATE TABLE user_profile (
    user_id INT NOT NULL,
    clinica_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (clinica_id) REFERENCES clinica(id),
    PRIMARY KEY (user_id, clinica_id)
);

CREATE INDEX idx_user_profile_user_id ON user_profile (user_id);
CREATE INDEX idx_user_profile_clinica_id ON user_profile (clinica_id);
ALTER TABLE user_profile DROP PRIMARY KEY;

ALTER TABLE user_profile
  ADD COLUMN id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;
  
CREATE UNIQUE INDEX uq_user_profile_user_clinica
  ON user_profile (user_id, clinica_id);

-- Accesos del usuario a las clínicas (clave para que el admin muestre esas clínicas)
INSERT INTO user_profile (user_id, clinica_id) VALUES (4, 1);
INSERT INTO user_profile (user_id, clinica_id) VALUES (4, 2);

INSERT INTO user_profile (user_id, clinica_id) VALUES
(1, 1), -- El admin tiene acceso a la Clínica Nova
(1, 2), -- El admin tiene acceso a la Bienestar Integral
(2, 1), -- El usuario de la Clínica Nova solo tiene acceso a la Clínica Nova
(3, 2); -- El usuario de la Bienestar Integral solo tiene acceso a la Bienestar Integral

CREATE TABLE auth_user_groups (
id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT NOT NULL, 
group_id INT NOT NULL, 
FOREIGN KEY (user_id) REFERENCES auth_user(id));

CREATE TABLE auth_user_user_permissions (
id INT AUTO_INCREMENT PRIMARY KEY, 
user_id INT NOT NULL, permission_id INT NOT NULL, 
FOREIGN KEY (user_id) REFERENCES auth_user(id)); 

CREATE TABLE auth_group (
id INT AUTO_INCREMENT PRIMARY KEY, 
name VARCHAR(150) NOT NULL UNIQUE); 

CREATE TABLE auth_permission (
id INT AUTO_INCREMENT PRIMARY KEY, 
name VARCHAR(255) NOT NULL, 
content_type_id INT NOT NULL, 
codename VARCHAR(100) NOT NULL); 

CREATE TABLE django_content_type (
id INT AUTO_INCREMENT PRIMARY KEY,
app_label VARCHAR(100) NOT NULL,
model VARCHAR(100) NOT NULL);
```

Nota: varias tablas del bloque anterior (por ejemplo, `auth_user`, `auth_group`, `auth_permission`, `django_content_type` y relaciones) no están definidas en `multi_tenant_citas/models.py`, pero son necesarias para el correcto funcionamiento de Django (autenticación, permisos y Admin). Por eso se incluyen en el script para ambientes locales.

---

## Modelos principales en Django

- **Clinica:** Representa cada tenant (clínica).
- **Paciente:** Relacionado con una clínica.
- **Cita:** Relacionado con paciente y clínica.
- **UserProfile:** Relaciona usuarios con clínicas.

---

## Librerías utilizadas

- **Django**: Framework principal.
- **mysqlclient** o **PyMySQL**: Conector MySQL.
- **Django TestCase**: Pruebas unitarias.
- **Django Admin**: Gestión visual de modelos.

---

## Documentación de lo realizado

- Se implementó la estructura multi-tenant en los modelos y la base de datos.
- Se configuró el admin y las vistas para filtrar y aislar los datos por clínica.
- Se validó mediante pruebas unitarias que cada clínica solo accede a sus propias citas.
- Se documentó el esquema de base de datos y los pasos para inicializar el sistema.

---

## Requisitos

- Python 3.10+
- Django 5.2+
- MySQL
- mysqlclient o PyMySQL

---

<!-- Sección "Ejecución" eliminada por duplicidad; consolidado en "Proceso de ejecución" -->

**Este módulo garantiza el aislamiento de datos entre clínicas y cumple con todos los criterios del ejercicio de multi-tenancy.**