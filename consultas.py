import sys
import argparse
from tabulate import tabulate  # Para mostrar resultados en formato de tabla

# Importar la función de conexión desde el archivo principal
try:
    from tienda_db import create_connection
except ImportError:
    print("Error: No se pudo importar create_connection desde tienda_db.py")
    print("Asegúrate de que el archivo tienda_db.py esté en el mismo directorio")
    sys.exit(1)

def execute_query(conn, query, params=None):
    """Ejecuta una consulta SQL y devuelve los resultados"""
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Verificar si la consulta devuelve resultados
        if cursor.description:
            # Obtener los nombres de las columnas
            columns = [desc[0] for desc in cursor.description]
            # Obtener los resultados
            results = cursor.fetchall()
            return columns, results
        else:
            # Para consultas que no devuelven resultados (INSERT, UPDATE, DELETE)
            rows_affected = cursor.rowcount
            return None, f"{rows_affected} filas afectadas"
    except Exception as e:
        return None, f"Error en la consulta: {str(e)}"
    finally:
        cursor.close()

def display_results(columns, results):
    """Muestra los resultados en un formato de tabla"""
    if columns:
        print(tabulate(results, headers=columns, tablefmt="psql"))
    else:
        print(results)

def show_query(query):   
    # Conectar a la base de datos
    try:
        conn = create_connection()
        columns, results = execute_query(conn, query)
        display_results(columns, results)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    query = """
        SELECT *
        FROM ordenes
    """
    show_query(query)