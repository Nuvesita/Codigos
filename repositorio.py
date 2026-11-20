# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

import requests


class Cliente_API:
    """Cliente de la API, descarga los Json con las frases y las respuestas"""

    def __init__(self, url_base):
        self._url_base = url_base

    def descargar_json(self, archivo):
        """Descarga el Json del repositorio y lo devuelve como diccionario"""

        try:
            respuesta = requests.get(self._url_base + archivo)
            respuesta.raise_for_status()

            return respuesta.json()
        
        except Exception:
            print("Error")
            return None

    def cargar_todo(self):
        """Descarga los datos y devuelve todos juntos"""

        archivos = ["entrada.json", "salida.json", "personas.json", "lugares.json"]
        datos = {}
        
        for archivo in archivos:
            datos[archivo] = self.descargar_json(archivo)

        return datos
