# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez


class GeneradorRespuestas:
    """Elige los mensajes que Eliza imprime en pantalla.

    Atributos:
        _grupos (list): grupos de salida del JSON, con los mensajes de
            respuesta de cada prioridad, más el conversacional (0).
        _preguntas (dict): grupos con las preguntas por el nombre y el
            origen del usuario y de las personas.

    Eficiencia: elegir un mensaje es O(1) con random.choice; armar los
    mensajes de personas recorre solo unos pocos campos, O(1).
    """

    def __init__(self, grupos, preguntas):
        """Guarda los grupos de salida y las preguntas pendientes.

        Eficiencia: O(1), solo guarda las dos listas.
        """
        self._grupos = grupos
        self._preguntas = preguntas

    def responder(self, grupo, base):
        """Devuelve la respuesta para el grupo de entrada que coincidió.

        Si el grupo es el de personas (prioridad 3) y ya se sabe algo de
        la última persona referenciada, arma el mensaje con esos datos;
        si no, elige un mensaje al azar del grupo de salida que tiene la
        misma prioridad.

        Eficiencia: O(g) con g = grupos de salida; elegir el mensaje es
        O(1).
        """
        if grupo.prioridad() == 3 and base.ultima() is not None:
            return self._mensaje_persona(base.ultima())

        for salida in self._grupos:

            if salida.prioridad() == grupo.prioridad():
                return salida.elegir_respuesta()

        return ""

    def siguiente_pregunta(self, base):
        """Devuelve la pregunta que sigue cuando ninguna frase coincidió.

        Pregunta primero por el nombre del usuario, después por su origen,
        después por lo que falte de las personas referenciadas y, cuando
        todo esté completo, imprime un mensaje conversacional.

        Eficiencia: O(p) con p = personas de la base.
        """
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
        """Arma el mensaje con los datos que se conocen de la persona.

        Ejemplos: "¿Tu abuela llamada Alicia?" cuando tiene nombre y
        "Háblame de tu abuela, ¿cómo era su nombre?" cuando le falta.

        Eficiencia: O(1); solo arma cadenas con los campos de la persona.
        """
        if persona.nombre() == "":
            return self._mensaje_nombre(persona)

        relacion = self._sin_determinantes(persona.relacion())
        # la relación se guarda sin acentos: "papá" queda como "papa"
        es_hombre = relacion.endswith("o") or relacion in ("padre", "papa", "papá")

        if es_hombre:
            return "¿Tu " + relacion + " llamado " + persona.nombre() + "?"

        else:
            return "¿Tu " + relacion + " llamada " + persona.nombre() + "?"

    def _mensaje_nombre(self, persona):
        """Arma la pregunta por el nombre de la persona referenciada.

        Eficiencia: O(1); solo arma una cadena con la relación.
        """
        relacion = self._sin_determinantes(persona.relacion())

        return "Háblame de tu " + relacion + ", ¿cómo era su nombre?"

    def _sin_determinantes(self, relacion):
        """Quita los artículos de adelante para poder decir "tu abuela".

        De "mi abuela" devuelve "abuela"; si no tiene artículo, devuelve
        la relación tal cual.

        Eficiencia: O(a) con a = cantidad de artículos revisados (3).
        """
        prefijos = ["mi ", "la ", "el "]

        for prefijo in prefijos:

            if relacion.startswith(prefijo):
                return relacion[len(prefijo):]

        return relacion
