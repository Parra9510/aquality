"""
fix_columna_password.py
Ejecutar UNA SOLA VEZ desde la carpeta aquality/:
    python fix_columna_password.py

Detecta el nombre real de la columna de contraseña en PostgreSQL
y la renombra a 'password_hash' para que coincida con el modelo ORM.
"""
from sqlalchemy import text
from app.core.database import engine

def fix():
    with engine.begin() as conn:
        # 1. Ver las columnas reales de la tabla usuarios en Postgres
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'usuarios'
            ORDER BY ordinal_position;
        """))
        columnas = [row[0] for row in result]
        print(f"Columnas actuales en 'usuarios': {columnas}")

        # 2. Renombrar si existe con el nombre viejo
        if 'password' in columnas and 'password_hash' not in columnas:
            conn.execute(text('ALTER TABLE usuarios RENAME COLUMN password TO password_hash;'))
            print("✅ Columna 'password' renombrada a 'password_hash'.")
        elif 'password_hash' in columnas:
            print("✅ La columna ya se llama 'password_hash'. No se necesita cambio.")
        else:
            print(f"⚠️  No se encontró columna 'password' ni 'password_hash'.")
            print(f"   Columnas disponibles: {columnas}")
            print(f"   Edita este script y ajusta el nombre viejo manualmente.")

if __name__ == "__main__":
    fix()