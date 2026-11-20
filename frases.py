# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

import random
import unicodedata


def normalizar(texto):
    """Devuelve el texto en minúsculas y sin acentos"""

    texto = texto.lower()

    # quitar los acentos

    texto = unicodedata.normalize("NFKD", texto)
    sin_acentos = ""

    for letra in texto:

        if not unicodedata.combining(letra):
            sin_acentos = sin_acentos + letra

    return sin_acentos


def limpiar_palabra(palabra):
    """Devuelve la palabra en minúsculas y sin signos ni acentos"""

    palabra = normalizar(palabra)
    limpia = ""

    for letra in palabra:

        if letra.isalnum() or letra == " ":
            limpia = limpia + letra

    return limpia.strip()


def a_palabras(texto):
    """Devuelve el texto como lista de palabras limpias"""

    palabras = []
    actual = ""

    for letra in normalizar(texto):

        if letra.isalnum():
            actual = actual + letra

        elif actual != "":
            palabras.append(actual)
            actual = ""

    if actual != "":
        palabras.append(actual)

    return palabras


class FraseClave:
    """Frase suelta que busca dentro de lo que escribe el usuario y captura lo que falta"""

    def __init__(self, texto):

        self._texto = normalizar(texto)
        self._comodin = "*" in self._texto

    def coincide(self, texto):
        """Devuelve la frase si aparece en el texto, o cadena vacía si no"""

        texto = normalizar(texto)

        if self._comodin:
            palabra = self.capturar(texto)

            if palabra == "":
                return ""
            
            return self._texto

        # la frase debe aparecer como palabras seguidas en el texto

        frase = a_palabras(self._texto)
        palabras = a_palabras(texto)

        for inicio in range(len(palabras) - len(frase) + 1):

            if palabras[inicio:inicio + len(frase)] == frase:
                return self._texto
            
        return ""

    def capturar(self, texto):
        """Devuelve la palabra que sigue al comodín, o cadena vacía si no hay nada que tomar"""

        texto = normalizar(texto)

        if not self._comodin:
            return ""

        parte_fija = self._texto.split("*")[0].split()
        palabras = texto.split()

        # recorrer el texto buscando la parte fija palabra por palabra
        for inicio in range(len(palabras) - len(parte_fija)):

            encontrada = True

            for posicion in range(len(parte_fija)):

                if limpiar_palabra(palabras[inicio + posicion]) != parte_fija[posicion]:
                    encontrada = False

            if encontrada:
                palabra = limpiar_palabra(palabras[inicio + len(parte_fija)])

                if palabra != "":
                    return palabra
                
        return ""


class GrupoFrases:
    """Grupo de frases que comparten nombre, prioridad y su respuesta"""

    def __init__(self, nombre, prioridad, frases):
        """Guarda el nombre, la prioridad y la lista de frases"""

        self._nombre = nombre
        self._prioridad = prioridad
        self._frases = frases

    def prioridad(self):
        """Devuelve la prioridad del grupo"""

        return self._prioridad

    def buscar(self, texto):
        """Devuelve lo que se capturó del texto con alguna frase, o cadena vacía si no coincidió ninguna"""

        for frase in self._frases:
            coincidente = frase.coincide(texto)

            if coincidente == "":
                continue
            
            palabra = frase.capturar(texto)

            if palabra == "":
                return coincidente
            
            return palabra
        
        return ""

    def elegir_respuesta(self):
        """Elige un mensaje al azar de la lista"""

        return random.choice(self._frases)


class GrupoEntrada(GrupoFrases):
    """Grupo de frases que busca en lo que escribe el usuario y define qué hacer al coincidir"""

    def __init__(self, nombre, prioridad, frases, accion):

        super().__init__(nombre, prioridad, frases)
        self._accion = normalizar(accion)

    def es_despedida(self):
        """Indica si este grupo es la despedida, la que termina el programa"""

        return self._accion == "fin del programa"


class GrupoSalida(GrupoFrases):
    """Grupo de mensajes con los que responde al usuario y se elige uno al azar"""

    def mensaje_conversacional(self):
        """Elige un mensaje conversacional para cuando no hay nada más que preguntar"""

        return self.elegir_respuesta()
