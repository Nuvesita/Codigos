# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez


class GeneradorRespuestas:
    """Elige los mensajes que imprime en pantalla según el grupo y lo que falta"""

    def __init__(self, grupos, preguntas):
        self._grupos = grupos
        self._preguntas = preguntas

    def responder(self, grupo, base):
        """Devuelve la respuesta para el grupo de entrada que coincidió"""

        if (grupo.prioridad() == 3) and (base.ultima() is not None):
            return self._mensaje_persona(base.ultima())

        for salida in self._grupos:

            if salida.prioridad() == grupo.prioridad():
                return salida.elegir_respuesta()

        return ""

    def siguiente_pregunta(self, base):
        """Devuelve la pregunta que sigue cuando ninguna frase coincidió"""

        usuario = base.personas()[0]
        incompletas = base.incompletas()

        if usuario.dato_faltante() == "nombre":
            return self._preguntas["nombre usuario"].elegir_respuesta()

        elif usuario.dato_faltante() == "origen":
            return self._preguntas["origen usuario"].elegir_respuesta()

        elif len(incompletas) > 0:

            persona = incompletas[0]

            if persona.dato_faltante() == "nombre":
                return self._mensaje_nombre(persona)

            else:
                return self._preguntas["origen persona"].elegir_respuesta()

        else:

            for salida in self._grupos:

                if salida.prioridad() == 0:
                    return salida.mensaje_conversacional()

            return ""

    def _mensaje_persona(self, persona):
        """Arma el mensaje con los datos que se conocen de la persona"""

        if persona.nombre() == "":
            return self._mensaje_nombre(persona)

        relacion = self._sin_determinantes(persona.relacion())

        es_hombre = relacion.endswith("o") or relacion in ("padre", "papa", "papá")

        if es_hombre:
            return "¿Tu " + relacion + " llamado " + persona.nombre() + "?"

        else:
            return "¿Tu " + relacion + " llamada " + persona.nombre() + "?"

    def _mensaje_nombre(self, persona):
        """Arma la pregunta por el nombre de la persona referenciada"""

        relacion = self._sin_determinantes(persona.relacion())

        return "Háblame de tu " + relacion + ", ¿cómo era su nombre?"

    def _sin_pref(self, relacion):
        """Quita los prefijos de la relación para que suene natural"""

        prefijos = ["mi ", "la ", "el "]

        for prefijo in prefijos:

            if relacion.startswith(prefijo):
                return relacion[len(prefijo):]

        return relacion
