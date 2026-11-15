# Proyecto: El Efecto ELIZA - Algoritmos y Programación (BPTSP05) 2627-1
# Integrantes: [NOMBRE 1] y [NOMBRE 2]
# Archivo: archivos.py
# Descripción: clase que guarda y carga la información en archivos .txt.

from personas import Persona, Usuario


class Persistencia:
    """Lee y escribe el archivo de texto con las personas de la sesión.

    El formato tiene un bloque por persona separado por "---", con los
    campos en forma "Campo: valor":

        Usuario: Juan
        Origen: Caracas
        ---
        Persona: Alicia
        Origen: Valencia
        Relacion: mi abuela

    Eficiencia: cargar y guardar son O(n) con n = cantidad de personas,
    porque se recorre la lista una sola vez.
    """

    def cargar(self, archivo):
        """Devuelve las personas guardadas en el archivo.

        Si el archivo no existe devuelve una lista vacía, que es el caso
        normal en la primera conversación.

        Eficiencia: O(n) con n = personas en el archivo.
        """
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
                personas.append(Persona(campos["Usuario"], campos.get("Origen", ""), ""))
            elif "Persona" in campos:
                personas.append(Persona(campos.get("Persona", ""),
                                        campos.get("Origen", ""),
                                        campos.get("Relacion", "")))
        return personas

    def guardar(self, archivo, personas):
        """Guarda la lista de personas en el archivo en formato de bloques.

        Si la persona es el Usuario se etiqueta como "Usuario" y no lleva
        relación; las demás se etiquetan como "Persona".

        Eficiencia: O(n) con n = personas guardadas.
        """
        bloques = []
        for persona in personas:
            if isinstance(persona, Usuario):
                bloque = "Usuario: " + persona.nombre()
                bloque += "\nOrigen: " + persona.lugar_origen()
            else:
                bloque = "Persona: " + persona.nombre()
                bloque += "\nOrigen: " + persona.lugar_origen()
                bloque += "\nRelacion: " + persona.relacion()
            bloques.append(bloque)
        texto = "\n---\n".join(bloques)
        with open(archivo, "w", encoding="utf-8") as contenido:
            contenido.write(texto + "\n")
