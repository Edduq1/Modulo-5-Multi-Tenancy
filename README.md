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
├── inventory_project/         # Configuración global del proyecto Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
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

- **inventory_project/**: Configuración global y archivos principales del proyecto Django.
- **multi_tenant_citas/**: Lógica de negocio, modelos, vistas, administración y pruebas del módulo de citas multi-tenant.
- **manage.py**: Punto de entrada para ejecutar comandos de Django.
- **requirements.txt**: Archivo con las dependencias del proyecto, con versiones fijadas.

---

## Enlace del Trello

Tablero del proyecto: https://trello.com/b/3GnQSD8c/modulo-5-multi-tenancy

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
Ejemplo de estructura y datos iniciales:

```sql
CREATE DATABASE multi_tenancy_citas;
USE multi_tenancy_citas;

CREATE TABLE clinica (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    direccion VARCHAR(255)
);

CREATE TABLE paciente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    apellido VARCHAR(255) NOT NULL,
    fecha_nacimiento DATE,
    clinica_id INT NOT NULL,
    FOREIGN KEY (clinica_id) REFERENCES clinica(id)
);

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

CREATE TABLE auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    last_login DATETIME(6) NULL,
    date_joined DATETIME(6) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL
);

CREATE TABLE user_profile (
    user_id INT NOT NULL,
    clinica_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (clinica_id) REFERENCES clinica(id),
    PRIMARY KEY (user_id, clinica_id)
);
```

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