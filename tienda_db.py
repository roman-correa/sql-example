import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

def create_connection(dbname=None):
    """Create connection to PostgreSQL database using environment variables"""
    # Get connection parameters from environment variables
    db = dbname or os.getenv("DB_NAME", "postgres")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "password")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    
    # Connect to database
    conn = psycopg2.connect(
        dbname=db,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True
    return conn

def create_database(conn, db_name="tienda_db"):
    """Create a new database"""
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Database {db_name} created successfully")
    else:
        print(f"Database {db_name} already exists")
    
    cursor.close()
    return db_name

def reset_database(conn, db_name):
    """Drop and recreate the database to start from scratch"""
    cursor = conn.cursor()
    
    try:
        # First, terminate all active connections to the database
        cursor.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
            AND pid <> pg_backend_pid()
        """, (db_name,))
        
        # We need to connect to a different database (postgres) before dropping
        cursor.close()
        conn.close()
        
        # Connect to the default postgres database
        temp_conn = psycopg2.connect(
            dbname="postgres",
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        temp_conn.autocommit = True
        temp_cursor = temp_conn.cursor()
        
        # Now we can drop and recreate the database
        temp_cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        print(f"Database {db_name} dropped")
        
        temp_cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Database {db_name} recreated successfully")
        
        temp_cursor.close()
        temp_conn.close()
        
        return True
    except Exception as e:
        print(f"Error resetting database: {str(e)}")
        return False

def create_tables(conn):
    """Create tables for users, products, orders, and order_products"""
    cursor = conn.cursor()
    
    # Create tables
    tables = [
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            precio DECIMAL(10, 2) NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ordenes (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id),
            fecha_orden TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(20) DEFAULT 'pendiente',
            total DECIMAL(10, 2) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orden_producto (
            id SERIAL PRIMARY KEY,
            orden_id INTEGER REFERENCES ordenes(id),
            producto_id INTEGER REFERENCES productos(id),
            cantidad INTEGER NOT NULL,
            precio_unitario DECIMAL(10, 2) NOT NULL,
            CONSTRAINT orden_producto_unique UNIQUE (orden_id, producto_id)
        )
        """
    ]
    
    for table in tables:
        cursor.execute(table)
    
    conn.commit()
    cursor.close()
    print("Tables created successfully")

def insert_sample_data(conn):
    """Insert sample data into tables"""
    cursor = conn.cursor()
    
    # Insert users
    usuarios = [
        ('Juan Pérez', 'juan@example.com'),
        ('María García', 'maria@example.com'),
        ('Carlos López', 'carlos@example.com'),
        ('Ana Martínez', 'ana@example.com')
    ]
    
    usuario_ids = []
    for usuario in usuarios:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (%s, %s) RETURNING id",
            usuario
        )
        usuario_ids.append(cursor.fetchone()[0])
    
    # Insert products
    productos = [
        ('Laptop', 'Laptop de alta gama', 1200.00, 10),
        ('Teléfono', 'Smartphone 5G', 800.00, 15),
        ('Auriculares', 'Auriculares inalámbricos', 120.00, 30),
        ('Tablet', 'Tablet de 10 pulgadas', 350.00, 8),
        ('Monitor', 'Monitor 4K de 27 pulgadas', 450.00, 5),
        ('Teclado', 'Teclado mecánico RGB', 85.00, 20),
        ('Mouse', 'Mouse inalámbrico ergonómico', 45.00, 25),
        ('Impresora', 'Impresora multifuncional', 250.00, 7),
        ('Disco duro', 'Disco duro externo 2TB', 130.00, 12),
        ('Cámara web', 'Cámara web HD', 65.00, 15)
    ]
    
    for producto in productos:
        cursor.execute(
            "INSERT INTO productos (nombre, descripcion, precio, stock) VALUES (%s, %s, %s, %s) RETURNING id",
            producto
        )
    
    # Insert orders
    ordenes = [
        (usuario_ids[0], 'completada', 1320.00),   # Juan: laptop y auriculares
        (usuario_ids[1], 'pendiente', 800.00),     # María: teléfono
        (usuario_ids[2], 'enviada', 590.00),       # Carlos: tablet y auriculares
        (usuario_ids[1], 'completada', 450.00),    # María: monitor
        (usuario_ids[3], 'pendiente', 330.00),     # Ana: impresora y mouse
        (usuario_ids[0], 'completada', 895.00),    # Juan: teléfono, teclado
        (usuario_ids[2], 'cancelada', 195.00),     # Carlos: disco duro, mouse
        (usuario_ids[3], 'enviada', 1250.00),      # Ana: laptop, mouse
        (usuario_ids[0], 'pendiente', 150.00),     # Juan: teclado, cámara web
        (usuario_ids[1], 'completada', 580.00)     # María: tablet, teclado, auriculares
    ]
    
    orden_ids = []
    for orden in ordenes:
        cursor.execute(
            "INSERT INTO ordenes (usuario_id, estado, total) VALUES (%s, %s, %s) RETURNING id",
            orden
        )
        orden_ids.append(cursor.fetchone()[0])
    
    # Insert order details
    orden_productos = [
        # Orden 1: Juan - laptop y auriculares
        (orden_ids[0], 1, 1, 1200.00),
        (orden_ids[0], 3, 1, 120.00),
        
        # Orden 2: María - teléfono
        (orden_ids[1], 2, 1, 800.00),
        
        # Orden 3: Carlos - tablet y auriculares
        (orden_ids[2], 4, 1, 350.00),
        (orden_ids[2], 3, 2, 120.00),
        
        # Orden 4: María - monitor
        (orden_ids[3], 5, 1, 450.00),
        
        # Orden 5: Ana - impresora y mouse
        (orden_ids[4], 8, 1, 250.00),
        (orden_ids[4], 7, 2, 45.00),
        
        # Orden 6: Juan - teléfono, teclado
        (orden_ids[5], 2, 1, 800.00),
        (orden_ids[5], 6, 1, 85.00),
        (orden_ids[5], 10, 1, 65.00),
        
        # Orden 7: Carlos - disco duro, mouse
        (orden_ids[6], 9, 1, 130.00),
        (orden_ids[6], 7, 1, 45.00),
        (orden_ids[6], 10, 1, 65.00),
        
        # Orden 8: Ana - laptop, mouse
        (orden_ids[7], 1, 1, 1200.00),
        (orden_ids[7], 7, 1, 45.00),
        
        # Orden 9: Juan - teclado, cámara web
        (orden_ids[8], 6, 1, 85.00),
        (orden_ids[8], 10, 1, 65.00),
        
        # Orden 10: María - tablet, teclado, auriculares
        (orden_ids[9], 4, 1, 350.00),
        (orden_ids[9], 6, 1, 85.00),
        (orden_ids[9], 3, 1, 120.00),
        (orden_ids[9], 7, 1, 45.00)
    ]
    
    for orden_producto in orden_productos:
        cursor.execute(
            "INSERT INTO orden_producto (orden_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
            orden_producto
        )
    
    conn.commit()
    cursor.close()
    print("Sample data inserted successfully")

def main():
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='PostgreSQL Database Demo')
    parser.add_argument('--reset', action='store_true', help='Reset the database')
    parser.add_argument('--db-name', default='tienda_db', help='Database name')
    args = parser.parse_args()
    
    # Connect to default postgres database
    conn = create_connection()
    
    if args.reset:
        # Reset the database
        reset_success = reset_database(conn, args.db_name)
        if not reset_success:
            print("Error al reiniciar la base de datos. Saliendo...")
            sys.exit(1)
    else:
        # Create new database if it doesn't exist
        create_database(conn, args.db_name)
    
    # Close connection to default database
    if conn:
        conn.close()
    
    # Connect to our database
    conn = create_connection(dbname=args.db_name)
    
    # Create tables
    create_tables(conn)
    
    # Insert sample data
    insert_sample_data(conn)
        
    # Close connection
    if conn:
        conn.close()
    print("\nDatabase operations completed successfully!")

if __name__ == "__main__":
    main()