# Proyecto: El Efecto ELIZA - Algoritmos y Programación (BPTSP05) 2627-1
# Integrantes: [NOMBRE 1] y [NOMBRE 2]
# Archivo: frases.py
# Descripción: clases para modelar las frases clave y sus grupos.

import random
import unicodedata


def normalizar(texto):
    """Devuelve el texto en minúsculas, sin acentos, signos ni espacios de más.

    Las frases se guardan así para compararlas igual que el usuario va a
    escribir: en minúsculas y sin acentos.

    Eficiencia: O(n) donde n es la cantidad de caracteres del texto.
    """
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = "".join(c if (c.isalnum() or c.isspace() or c == "*") else " " for c in texto)
    return " ".join(texto.split())


class FraseClave:
    """Frase suelta que Eliza busca dentro de lo que escribe el usuario.

    Puede terminar en * para indicar que la palabra que viene después se
    guarda como dato (relación, nombre o lugar). Se asume que el * está
    al final de la frase.

    Atributos:
        _texto (str): la frase normalizada, con * si tiene comodín.
        _comodin (bool): True si la frase contiene *.

    Eficiencia: las dos comparaciones recorren una sola vez las palabras
    del texto, es decir O(n).
    """

    def __init__(self, texto):
        """Guarda la frase en minúsculas y sin acentos."""
        self._texto = normalizar(texto)
        self._comodin = "*" in self._texto

    def coincide(self, texto):
        """Devuelve la frase si aparece en el texto, o cadena vacía si no.

        Con comodín solo coincide si además hay una palabra después del *:
        "es mi" no coincide, pero "es mi esposa" sí.

        Eficiencia: O(n) donde n es la cantidad de palabras del texto.
        """
        texto = normalizar(texto)
        if self._comodin:
            if self.capturar(texto) == "":
                return ""
            return self._texto
        if self._texto in texto:
            return self._texto
        return ""

    def es_igual(self, texto):
        """Devuelve True si el texto completo es la frase, sin comodín.

        Sirve para que "no sé" prefiera el grupo Ayuda antes que el
        grupo Positivismo, que tendría la palabra "no" dentro del texto.

        Eficiencia: O(n) donde n es la cantidad de caracteres del texto.
        """
        if self._comodin:
            return False
        return self._texto == normalizar(texto)

    def capturar(self, texto):
        """Devuelve la palabra que sigue al *, o cadena vacía si no tiene
        comodín o si el usuario no escribió nada después.

        Eficiencia: O(n) donde n es la cantidad de palabras del texto; se
        compara palabra por palabra hasta encontrar la parte fija.
        """
        texto = normalizar(texto)
        if not self._comodin:
            return ""
        parte_fija = self._texto.split("*")[0].split()
        palabras = texto.split()
        for i in range(len(palabras) - len(parte_fija)):
            if palabras[i:i + len(parte_fija)] == parte_fija:
                return palabras[i + len(parte_fija)]
        return ""


class GrupoFrases:
    """Grupo de frases que comparten nombre y prioridad (del 1 al 12).

    En los grupos de entrada la lista guarda objetos FraseClave; en los de
    salida guarda los mensajes de respuesta en texto.

    Atributos:
        _nombre (str): nombre del grupo, por ejemplo "Personas".
        _prioridad (int): número de prioridad, 1 es la más importante.
        _frases (list): lista de FraseClave o de mensajes de texto.

    Eficiencia: buscar recorre todas las frases del grupo, O(f · n) donde f
    es la cantidad de frases y n la cantidad de palabras del texto.
    """

    def __init__(self, nombre, prioridad, frases):
        """Guarda el nombre, la prioridad y la lista de frases."""
        self._nombre = nombre
        self._prioridad = prioridad
        self._frases = frases

    def prioridad(self):
        """Devuelve la prioridad del grupo (1 es la más importante).

        Eficiencia: O(1).
        """
        return self._prioridad

    def buscar(self, texto):
        """Devuelve la primera frase que coincide con el texto.

        Si esa frase tiene *, devuelve la palabra que capturó; si no, la
        frase completa. Devuelve cadena vacía si ninguna coincide.

        Eficiencia: O(f · n) donde f es la cantidad de frases del grupo.
        """
        for frase in self._frases:
            coincidente = frase.coincide(texto)
            if coincidente != "":
                palabra = frase.capturar(texto)
                if palabra != "":
                    return palabra
                return coincidente
        return ""

    def coincide_completa(self, texto):
        """Devuelve True si el texto completo es alguna frase del grupo.

        Antes de mirar las prioridades, Eliza busca si el usuario escribió
        exactamente una frase conocida: esa coincidencia gana siempre.

        Eficiencia: O(f · n) donde f es la cantidad de frases del grupo.
        """
        for frase in self._frases:
            if frase.es_igual(texto):
                return True
        return False

    def elegir_respuesta(self):
        """Elige un mensaje al azar de la lista.

        Se usa en los grupos de salida, donde la lista tiene mensajes
        de texto y no objetos FraseClave.

        Eficiencia: O(1); random.choice tarda lo mismo con 1 o con 1000 mensajes.
        """
        return random.choice(self._frases)


class GrupoEntrada(GrupoFrases):
    """Grupo de frases que Eliza busca en lo que escribe el usuario.

    Hereda el nombre, la prioridad y las frases de GrupoFrases.

    Atributos:
        _accion (str): qué representa el grupo, por ejemplo "despedida".

    Eficiencia: misma que GrupoFrases.
    """

    def __init__(self, nombre, prioridad, frases, accion):
        """Carga el grupo con sus frases y guarda la acción que representa."""
        super().__init__(nombre, prioridad, frases)
        self._accion = normalizar(accion)

    def es_despedida(self):
        """Devuelve True si el grupo es el de despedida.

        La acción viene del JSON del profesor: "Fin del programa".

        Eficiencia: O(1); solo compara dos cadenas.
        """
        return self._accion == "fin del programa"


class GrupoSalida(GrupoFrases):
    """Grupo de mensajes con los que Eliza responde al usuario.

    Hereda de GrupoFrases; acá la lista de frases contiene mensajes de
    texto y no objetos FraseClave.

    Eficiencia: misma que GrupoFrases.
    """

    def mensaje_conversacional(self):
        """Devuelve un mensaje de este grupo para seguir la conversación
        cuando ninguna frase clave coincidió.

        Eficiencia: O(1); elige un mensaje al azar de la lista.
        """
        return self.elegir_respuesta()
