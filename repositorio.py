# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

import requests


class Cliente_API:
    """Cliente de la API del repositorio GitHub con las frases de ELIZA.

    Atributos:
        _url_base (str): dirección donde viven los JSON, terminada en /.

    Eficiencia: cada descarga es una llamada a la red; en memoria solo
    guarda un diccionario por archivo, es decir O(1) por archivo.
    """

    def __init__(self, url_base):
        """Guarda la dirección base de los JSON del repositorio.

        Eficiencia: O(1).
        """
        self._url_base = url_base

    def descargar_json(self, archivo):
        """Descarga un JSON del repositorio y lo devuelve como diccionario.

        Si la descarga falla devuelve None y lo avisa en pantalla.

        Eficiencia: una llamada a la red, O(1) en memoria por archivo.
        """
        try:
            respuesta = requests.get(self._url_base + archivo)
            respuesta.raise_for_status()
            return respuesta.json()
        except Exception:
            print("No se pudo descargar " + archivo + ".")
            return None

    def cargar_todo(self):
        """Descarga los cuatro JSON y devuelve todos juntos.

        Si algún archivo no se puede descargar, ese archivo queda en None.
        El diccionario devuelto tiene las claves "entrada.json",
        "salida.json", "personas.json" y "lugares.json".

        Eficiencia: cuatro llamadas a la red, O(1) en memoria por archivo.
        """
        archivos = ["entrada.json", "salida.json", "personas.json", "lugares.json"]
        datos = {}
        for archivo in archivos:
            datos[archivo] = self.descargar_json(archivo)
        return datos
