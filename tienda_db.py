import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

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
    
    # Close all active connections to the database
    cursor.execute("""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = %s
        AND pid <> pg_backend_pid()
    """, (db_name,))
    
    # Drop database if exists
    cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
    print(f"Database {db_name} dropped")
    
    # Create database again
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    print(f"Database {db_name} recreated successfully")
    
    cursor.close()

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
    
    for usuario in usuarios:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (%s, %s) RETURNING id",
            usuario
        )
    
    # Insert products
    productos = [
        ('Laptop', 'Laptop de alta gama', 1200.00, 10),
        ('Teléfono', 'Smartphone 5G', 800.00, 15),
        ('Auriculares', 'Auriculares inalámbricos', 120.00, 30),
        ('Tablet', 'Tablet de 10 pulgadas', 350.00, 8),
        ('Monitor', 'Monitor 4K de 27 pulgadas', 450.00, 5)
    ]
    
    for producto in productos:
        cursor.execute(
            "INSERT INTO productos (nombre, descripcion, precio, stock) VALUES (%s, %s, %s, %s) RETURNING id",
            producto
        )
    
    # Insert orders
    ordenes = [
        (1, 'completada', 1320.00),  # Juan compra laptop y auriculares
        (2, 'pendiente', 800.00),    # María compra teléfono
        (3, 'enviada', 900.00),      # Carlos compra tablet y auriculares
        (2, 'completada', 450.00)    # María compra monitor
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
        (orden_ids[0], 1, 1, 1200.00),  # Orden 1: 1 laptop
        (orden_ids[0], 3, 1, 120.00),   # Orden 1: 1 auriculares
        (orden_ids[1], 2, 1, 800.00),   # Orden 2: 1 teléfono
        (orden_ids[2], 4, 1, 350.00),   # Orden 3: 1 tablet
        (orden_ids[2], 3, 2, 120.00),   # Orden 3: 2 auriculares
        (orden_ids[3], 5, 1, 450.00)    # Orden 4: 1 monitor
    ]
    
    for orden_producto in orden_productos:
        cursor.execute(
            "INSERT INTO orden_producto (orden_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
            orden_producto
        )
    
    conn.commit()
    cursor.close()
    print("Sample data inserted successfully")

def query_sample_data(conn):
    """Query and display sample data"""
    cursor = conn.cursor()
    
    print("\n--- Usuarios ---")
    cursor.execute("SELECT id, nombre, email FROM usuarios")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Nombre: {row[1]}, Email: {row[2]}")
    
    print("\n--- Productos ---")
    cursor.execute("SELECT id, nombre, precio, stock FROM productos")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Nombre: {row[1]}, Precio: ${row[2]}, Stock: {row[3]}")
    
    print("\n--- Órdenes ---")
    cursor.execute("""
        SELECT o.id, u.nombre, o.fecha_orden, o.estado, o.total 
        FROM ordenes o 
        JOIN usuarios u ON o.usuario_id = u.id
    """)
    for row in cursor.fetchall():
        print(f"Orden ID: {row[0]}, Usuario: {row[1]}, Fecha: {row[2]}, Estado: {row[3]}, Total: ${row[4]}")
    
    print("\n--- Detalles de Órdenes ---")
    cursor.execute("""
        SELECT op.orden_id, p.nombre, op.cantidad, op.precio_unitario, (op.cantidad * op.precio_unitario) as subtotal
        FROM orden_producto op
        JOIN productos p ON op.producto_id = p.id
        ORDER BY op.orden_id
    """)
    for row in cursor.fetchall():
        print(f"Orden ID: {row[0]}, Producto: {row[1]}, Cantidad: {row[2]}, Precio: ${row[3]}, Subtotal: ${row[4]}")

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
        reset_database(conn, args.db_name)
    else:
        # Create new database
        create_database(conn, args.db_name)
    
    # Close connection to default database
    conn.close()
    
    # Connect to our new database
    conn = create_connection(dbname=args.db_name)
    
    # Create tables
    create_tables(conn)
    
    # Insert sample data
    insert_sample_data(conn)
    
    # Query and display sample data
    query_sample_data(conn)
    
    # Close connection
    conn.close()
    print("\nDatabase operations completed successfully!")

if __name__ == "__main__":
    main()