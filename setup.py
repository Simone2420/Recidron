from cx_Freeze import setup, Executable
import os

setup(
    name="Recidron",
    version="1.0",
    description="Recidron es un juego que promueve el reciclaje y la protección de las plantas",
    options={
        "build_exe": {
            "packages": ["pygame", "mediapipe", "cv2"],  # Paquetes necesarios
            "include_files": ["imagenes/"],  # Carpetas de recursos
            "build_exe": "Proyecto_definitivo"  # Carpeta de salida
        }
    },
    executables=[Executable("main.py", base="Win32GUI", target_name="Recidron.exe")]
)
