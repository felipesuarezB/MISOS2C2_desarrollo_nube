"""
Script para ejecutar la aplicación con Uvicorn.
"""
import os
import uvicorn
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    # Obtener configuración del entorno o usar valores por defecto
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", "8000"))
    
    # Configuración de Uvicorn
    uvicorn.run(
        "src.app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 