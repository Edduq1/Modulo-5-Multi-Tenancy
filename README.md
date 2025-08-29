# Modulo-5-Multi-Tenancy

Este proyecto corresponde al **Módulo 5** del sistema, enfocado en la gestión de citas médicas con arquitectura **multi-tenancy** usando **Python**, **Django** y **MySQL**.  
La estructura del módulo permite que varias clínicas (tenants) trabajen de forma aislada y segura dentro de la misma aplicación, cumpliendo todos los criterios del ejercicio solicitado.

---

## Gestión de dependencias con `requirements.txt`

Se usa `requirements.txt` para administrar y replicar el entorno de dependencias.

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

## Estructura del Módulo 5

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

## Migraciones en Django

Para crear las tablas desde los modelos de Django:

```sh
python manage.py makemigrations
python manage.py migrate
```

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

## Ejecución

1. Instala dependencias:
   ```sh
   pip install -r requirements.txt
   ```
2. Configura la base de datos en `settings.py`.
3. Ejecuta migraciones:
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Inicia el servidor:
   ```sh
   python manage.py runserver
   ```
5. Accede al admin en `/admin/` para gestionar clínicas, pacientes y citas.

---

**Este módulo garantiza el aislamiento de datos entre clínicas y cumple con todos los criterios del ejercicio de multi-tenancy.**