# RUTA: main.py
# Punto de entrada principal para la aplicación Flask.

from app import create_app

# Crea una instancia de la aplicación Flask llamando a la factory function.
app = create_app()

if __name__ == '__main__':
    # Ejecuta la aplicación en modo de depuración.
    # El puerto se puede cambiar si es necesario.
    # En producción, esto será manejado por un servidor WSGI como Gunicorn.
    app.run(debug=True, port=5001)
