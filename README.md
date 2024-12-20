# TimeTracker Project

Este es un proyecto de seguimiento de tiempo para empleados, desarrollado con Django. Permite a los empleados registrar sus horas de trabajo y descanso, y a los administradores ver y gestionar estos registros.
## Estructura del Proyecto

```
timeTrackerProject/
    .gitignore
    attendance/
        __init__.py
        admin.py
        apps.py
        migrations/
        models.py
        static/
            css/
                flowbite.css
                styles.css
            js/
                flowbite.js
        templates/
            base.html
            home.html
            login.html
            week.html
        tests.py
        urls.py
        views.py
    db.sqlite3
    manage.py
    timeTracker/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    venv/
```

## Instalación

1. Clona el repositorio:
    ``` sh
    git clone https://github.com/beatkapo/timeTracker.git
    cd timeTracker
    ```

2. Crea y activa un entorno virtual:
    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias:
    ```sh
    cd timeTrackerProject
    pip install -r requirements.txt
    ```

4. Realiza las migraciones de la base de datos:
    ```sh
    python manage.py migrate
    ```

5. Crea un usuario administrador:
    ```sh
    python manage.py createsuperuser
    ```

6. Inicia el servidor de desarrollo:
    ```sh
    python manage.py runserver
    ```

## Uso

#### Administrador

- Accede a la aplicación en `http://127.0.0.1:8000/admin`.
- Inicia sesión con tus credenciales de administrador.
- Gestiona los usuarios y empleados.

#### Usuario

- Accede a la aplicación en `http://127.0.0.1:8000/`.
- Inicia sesión con tus credenciales.
- Registra tus horas de trabajo y descanso.
- Consulta las horas trabajadas desde el menú `Ver semana`

## Archivos Clave

- `attendance/views.py`: Contiene las vistas principales para la gestión de asistencia.
- `attendance/templates/`: Contiene las plantillas HTML para las páginas de la aplicación.
- `attendance/static/css/flowbite.css`: Archivo CSS para estilos.
- `attendance/static/js/flowbite.js`: Archivo JavaScript para funcionalidades interactivas.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cualquier cambio que desees realizar.

