# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

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
        bloques = texto.split("---")
        for bloque in bloques:
            # cada bloque es un conjunto de líneas "Campo: valor"
            campos = {}
            lineas = bloque.split("\n")
            for linea in lineas:
                if ":" in linea:
                    partes = linea.split(":", 1)
                    clave = partes[0].strip()
                    valor = partes[1].strip()
                    campos[clave] = valor

            if "Usuario" in campos:
                origen = ""
                if "Origen" in campos:
                    origen = campos["Origen"]
                personas.append(Persona(campos["Usuario"], origen, ""))
            elif "Persona" in campos:
                nombre = campos.get("Persona", "")
                origen = campos.get("Origen", "")
                relacion = campos.get("Relacion", "")
                personas.append(Persona(nombre, origen, relacion))
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
                bloque = bloque + "\nOrigen: " + persona.lugar_origen()
            else:
                bloque = "Persona: " + persona.nombre()
                bloque = bloque + "\nOrigen: " + persona.lugar_origen()
                bloque = bloque + "\nRelacion: " + persona.relacion()
            bloques.append(bloque)

        # los bloques se unen con la línea "---"
        texto = "\n---\n".join(bloques)
        with open(archivo, "w", encoding="utf-8") as contenido:
            contenido.write(texto + "\n")
