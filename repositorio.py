# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

import json
import os

import requests


class Cliente_API:
    """Clase encargada del acceso a la API del repositorio del profesor.

    Es el único punto del programa que toca internet: baja los cuatro
    JSON y, si no hay red, se apoya en la copia local de la carpeta
    datos/ que se guarda en cada descarga exitosa.

    Atributos:
        _url_base (str): dirección base del repositorio en GitHub.

    Eficiencia: cada descarga es O(1) en memoria; se hace una sola
    llamada por archivo, únicamente al iniciar el programa.
    """

    def __init__(self, url_base):
        """Guarda la URL base del repositorio."""
        self._url_base = url_base

    def descargar_json(self, archivo):
        """Descarga un JSON del repositorio y lo devuelve como diccionario.

        Cada descarga exitosa guarda una copia en datos/ para usarla
        después si no hay internet. Si falla, devuelve None para que
        cargar_todo() lea la copia local.

        Eficiencia: O(1) en memoria; depende solo de la red
        (timeout de 10 segundos).
        """
        try:
            respuesta = requests.get(self._url_base + archivo, timeout=10)
            respuesta.raise_for_status()
            datos = respuesta.json()
        except Exception:
            # cualquier problema de red o de JSON: nunca se cierra el programa
            print("No se pudo descargar " + archivo + ", uso la copia local.")
            return None

        # guardar la copia local para poder funcionar sin internet
        try:
            os.makedirs("datos", exist_ok=True)
            with open("datos/" + archivo, "w", encoding="utf-8") as copia:
                json.dump(datos, copia, ensure_ascii=False)
        except OSError:
            print("No se pudo guardar la copia local de " + archivo + ".")
        return datos

    def cargar_todo(self):
        """Descarga los cuatro JSON y devuelve todos juntos.

        Si algún archivo no se puede descargar, usa la copia local de
        datos/; si tampoco existe, ese archivo queda en None. El
        diccionario devuelto tiene las claves "entrada.json",
        "salida.json", "personas.json" y "lugares.json".

        Eficiencia: cuatro llamadas a la red, O(1) en memoria por archivo.
        """
        archivos = ["entrada.json", "salida.json", "personas.json", "lugares.json"]
        datos = {}
        for archivo in archivos:
            contenido = self.descargar_json(archivo)
            if contenido is None:
                # sin internet: intentar leer la copia guardada en datos/
                try:
                    with open("datos/" + archivo, "r", encoding="utf-8") as guardado:
                        contenido = json.load(guardado)
                except Exception:
                    contenido = None
            datos[archivo] = contenido
        return datos
