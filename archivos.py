# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

from personas import Persona, Usuario


class Persistencia:
    """Lee y escribe el archivo de texto con las personas de la sesión, en bloques separados"""

    def cargar(self, archivo):
        """Devuelve las personas guardadas en el archivo, o lista vacía si no existe"""

        try:
            with open(archivo, "r", encoding="utf-8") as contenido:
                texto = contenido.read()

        except OSError:
            return []

        personas = []

        for bloque in texto.split("---"):

            campos = {}

            for linea in bloque.split("\n"):

                if ":" in linea:

                    clave, valor = linea.split(":", 1)
                    campos[clave.strip()] = valor.strip()

            if "Usuario" in campos:
                nombre = campos["Usuario"]
                relacion = ""

            elif "Persona" in campos:
                nombre = campos["Persona"]
                relacion = campos.get("Relacion", "")

            else:
                continue

            personas.append(Persona(nombre, campos.get("Origen", ""), relacion))

        return personas

    def guardar(self, archivo, personas):
        """Guarda la lista de personas en el archivo en formato de bloques"""

        bloques = []

        for persona in personas:

            es_usuario = isinstance(persona, Usuario)
            etiqueta = "Usuario" if es_usuario else "Persona"

            lineas = [etiqueta + ": " + persona.nombre(),
                      "Origen: " + persona.lugar_origen()]

            if not es_usuario:
                lineas.append("Relacion: " + persona.relacion())
            bloques.append("\n".join(lineas))

        texto = "\n---\n".join(bloques)
        with open(archivo, "w", encoding="utf-8") as contenido:
            contenido.write(texto + "\n")
