# Ejemplos de PostgreSQL con Python

Este repositorio contiene scripts para crear y manipular una base de datos PostgreSQL utilizando Python. Está diseñado como material educativo para aprender los conceptos básicos de bases de datos relacionales, SQL y su integración con Python.

## Requisitos previos

- Python 3.6 o superior
- PostgreSQL instalado y en ejecución en tu sistema, o base de datos externa funcionando
- Conocimientos básicos de SQL y Python

## Instrucciones de instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/jjsantos01/sql-example.git
cd sql-example
```

### 2. Crear un entorno virtual

**En Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**En macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
DB_NAME=tienda_db
DB_USER=user_name
DB_PASSWORD=tu_contraseña
DB_HOST=localhost o host externo
DB_PORT=5432
```

Reemplaza `tu_contraseña` con la contraseña de tu usuario de PostgreSQL y modifica las otras variables si es necesario.

## Uso de los scripts

### Creación de la base de datos

Para crear la base de datos y poblarla con datos de ejemplo:

```bash
python tienda_db.py
```

### Reiniciar la base de datos

Si necesitas reiniciar la base de datos (eliminar y volver a crear):

```bash
python tienda_db.py --reset
```

### Ejecutar consultas

Para ejecutar consultas en la base de datos:

```bash
python consultas.py
```

Puedes modificar la variable `query` en el archivo `consultas.py` para cambiar la consulta que se ejecuta.
También puedes importar la función `show_query()` desde otro script, por ejemplo:

```py
# tarea.py
from consultas import show_query
query = """
SELECT *
FROM ordenes
"""
show_query(query)
```

## Estructura de la base de datos

La base de datos incluye las siguientes tablas:

- **usuarios**: Información de los clientes
- **productos**: Catálogo de productos disponibles
- **ordenes**: Registro de órdenes realizadas por los usuarios
- **orden_producto**: Tabla de relación que conecta órdenes con productos

## Solución de problemas

### Error de conexión a PostgreSQL

Si encuentras errores al conectarte a PostgreSQL, verifica:

1. Que PostgreSQL esté en ejecución en tu sistema o que el servidor externo esté activo
2. Que las credenciales en el archivo `.env` sean correctas
3. Que tengas permisos para crear bases de datos con el usuario proporcionado

### Error al instalar psycopg2

Si encuentras errores al instalar psycopg2, puedes intentar con la versión binaria:

```bash
pip install psycopg2-binary
```
