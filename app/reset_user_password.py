# RUTA: reset_user_password.py
# Este script permite resetear la contraseña de CUALQUIER usuario del sistema.
import pyodbc
from werkzeug.security import generate_password_hash
import getpass
import sys
import os

# Añadir la ruta de la app para poder importar la configuración
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

try:
    from config import Config
except ImportError:
    print("[ERROR] No se pudo importar 'Config' desde 'app.config'.")
    print("Asegúrate de que este script está en la carpeta raíz del proyecto ('sistema_gestion_escolar_pro').")
    sys.exit(1)


def reset_password():
    """
    Script para resetear la contraseña de un usuario específico.
    """
    print("--- Asistente para Resetear Contraseña de Usuario ---")
    
    # 1. Conectar a la base de datos
    try:
        conn_str = (
            f"DRIVER={Config.DB_DRIVER};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE={Config.DB_DATABASE};"
            f"UID={Config.DB_USERNAME};"
            f"PWD={Config.DB_PASSWORD};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("[ÉXITO] Conexión a la base de datos establecida.")
    except Exception as e:
        print(f"\n[ERROR] No se pudo conectar a la base de datos: {e}")
        print("Por favor, verifica que las credenciales en 'app/config.py' son correctas.")
        return

    # 2. Preguntar por el nombre de usuario
    username_to_reset = input("\nIntroduce el nombre de usuario (username) cuya contraseña deseas cambiar: ")
    if not username_to_reset:
        print("[ERROR] No se introdujo un nombre de usuario. Operación cancelada.")
        conn.close()
        return

    # 3. Verificar si el usuario existe
    try:
        cursor.execute("SELECT COUNT(1) FROM Usuarios WHERE username = ?", username_to_reset)
        if cursor.fetchone()[0] == 0:
            print(f"\n[ERROR] El usuario '{username_to_reset}' no existe en la base de datos. Operación cancelada.")
            conn.close()
            return
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error al verificar el usuario: {e}")
        conn.close()
        return

    # 4. Pedir la nueva contraseña de forma segura
    print(f"\nAhora, introduce la nueva contraseña para el usuario '{username_to_reset}'.")
    print("Nota: Lo que escribas no aparecerá en la pantalla por seguridad.")
    new_password = getpass.getpass("Nueva contraseña: ")
    confirm_password = getpass.getpass("Confirma la nueva contraseña: ")

    if not new_password or new_password != confirm_password:
        print("\n[ERROR] Las contraseñas no coinciden o están vacías. Operación cancelada.")
        conn.close()
        return

    # 5. Generar el nuevo hash
    new_hash = generate_password_hash(new_password, method='scrypt')
    print("\nNuevo hash generado. Actualizando la base de datos...")

    # 6. Actualizar la base de datos
    try:
        sql_update_query = "UPDATE Usuarios SET password_hash = ? WHERE username = ?"
        cursor.execute(sql_update_query, new_hash, username_to_reset)
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"\n[ÉXITO] ¡Contraseña para el usuario '{username_to_reset}' actualizada!")
            print(f"Ahora puede iniciar sesión con la contraseña que acabas de establecer.")
        else:
            # Este caso no debería ocurrir gracias a la verificación previa, pero es una buena práctica mantenerlo.
            print(f"\n[ERROR] No se encontró al usuario '{username_to_reset}'. No se realizó ninguna actualización.")

    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error al actualizar la base de datos: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\nConexión a la base de datos cerrada.")


if __name__ == '__main__':
    reset_password()
