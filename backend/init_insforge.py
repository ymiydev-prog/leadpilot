#!/usr/bin/env python3
"""
Inicializar tablas en Insforge para LeadPilot
Ejecutar una vez para crear la estructura de base de datos
"""
import os
import subprocess

def main():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    
    if not os.path.exists(schema_path):
        print(f"✗ No se encontró el archivo {schema_path}")
        return

    print("Inicializando la base de datos usando Insforge CLI...")
    print(f"Archivo de esquema: {schema_path}")
    
    try:
        # Usamos npx @insforge/cli db query para cargar el schema directamente
        result = subprocess.run(
            ["npx", "@insforge/cli", "db", "query", "-f", schema_path],
            check=True,
            text=True,
            capture_output=True
        )
        print("✓ Tablas verificadas e inicializadas correctamente!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("✗ Error al inicializar las tablas:")
        print(e.stderr)

if __name__ == "__main__":
    main()
