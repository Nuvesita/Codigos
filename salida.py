# Proyecto: El Efecto ELIZA - Algoritmos y Programación (BPTSP05) 2627-1
# Integrantes: [NOMBRE 1] y [NOMBRE 2]
# Archivo: salida.py
# Descripción: clase que construye las respuestas de Eliza.


class GeneradorRespuestas:
    """Elige los mensajes que Eliza imprime en pantalla.

    Guarda los 13 grupos de salida (los 12 con sus prioridades más el
    conversacional con prioridad 0) y los grupos de preguntas que se usan
    cuando falta información.

    Atributos:
        _grupos (list): lista de los grupos de salida.
        _preguntas (dict): grupos de preguntas con las claves
            "nombre usuario", "origen usuario" y "origen persona".

    Eficiencia: responder y siguiente_pregunta recorren los grupos, es
    decir O(g) con g = 13; elegir un mensaje es O(1).
    """

    def __init__(self, grupos, preguntas):
        """Guarda los grupos de salida y los grupos de preguntas."""
        self._grupos = grupos
        self._preguntas = preguntas

    def responder(self, grupo, base):
        """Devuelve la respuesta para el grupo de entrada que coincidió.

        Si el grupo es el Freudiano (prioridad 3) y hay una persona
        recién mencionada, el mensaje se arma con sus datos: pide el
        nombre si falta o lo muestra si ya se conoce. En los demás
        grupos elige un mensaje al azar del grupo de salida.

        Eficiencia: O(g) con g = cantidad de grupos de salida.
        """
        if grupo.prioridad() == 3 and base.ultima() is not None:
            return self._mensaje_persona(base.ultima())
        for salida in self._grupos:
            if salida.prioridad() == grupo.prioridad():
                return salida.elegir_respuesta()
        return ""

    def siguiente_pregunta(self, base):
        """Devuelve la pregunta que sigue cuando ninguna frase coincidió.

        Pide primero el nombre del usuario, después su origen, luego los
        datos de las personas incompletas y, si está todo completo, usa
        el mensaje conversacional.

        Eficiencia: O(n + g) con n = personas y g = grupos de salida.
        """
        usuario = base.personas()[0]
        if usuario.dato_faltante() == "nombre":
            return self._preguntas["nombre usuario"].elegir_respuesta()
        if usuario.dato_faltante() == "origen":
            return self._preguntas["origen usuario"].elegir_respuesta()
        incompletas = base.incompletas()
        if len(incompletas) > 0:
            persona = incompletas[0]
            if persona.dato_faltante() == "nombre":
                return self._mensaje_nombre(persona)
            return self._preguntas["origen persona"].elegir_respuesta()
        for salida in self._grupos:
            if salida.prioridad() == 0:
                return salida.mensaje_conversacional()
        return ""

    def _mensaje_persona(self, persona):
        """Arma el mensaje del Freudiano con los datos de la persona.

        Si no tiene nombre pide el nombre; si lo tiene, lo muestra en
        la pregunta.

        Eficiencia: O(1).
        """
        if persona.nombre() == "":
            return self._mensaje_nombre(persona)
        relacion = self._sin_determinantes(persona.relacion())
        if relacion.endswith("o") or relacion in ("padre", "papá"):
            return "¿Tu " + relacion + " llamado " + persona.nombre() + "?"
        return "¿Tu " + relacion + " llamada " + persona.nombre() + "?"

    def _mensaje_nombre(self, persona):
        """Arma la pregunta por el nombre de la persona.

        Eficiencia: O(1).
        """
        relacion = self._sin_determinantes(persona.relacion())
        return "Háblame de tu " + relacion + ", ¿cómo era su nombre?"

    def _sin_determinantes(self, relacion):
        """Quita los artículos de adelante para poder decir "tu abuela".

        Eficiencia: O(1).
        """
        for prefijo in ("mi ", "la ", "el "):
            if relacion.startswith(prefijo):
                return relacion[3:]
        return relacion
