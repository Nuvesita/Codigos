# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez


class Persona:
    """Persona referenciada durante la conversación: el usuario o alguien
    de quien el usuario habla.

    Atributos:
        _nombre (str): nombre de la persona, vacío si aún no se conoce.
        _lugar_origen (str): lugar de origen, vacío si aún no se conoce.
        _relacion (str): relación con el usuario, por ejemplo "mi abuela".

    Eficiencia: todos los métodos son O(1), solo leen o escriben un dato.
    """

    def __init__(self, nombre="", lugar_origen="", relacion=""):
        """Crea una persona con los datos que se conozcan desde el inicio."""
        self._nombre = nombre
        self._lugar_origen = lugar_origen
        self._relacion = relacion

    def nombre(self):
        """Devuelve el nombre, o cadena vacía si todavía no se conoce.

        Eficiencia: O(1).
        """
        return self._nombre

    def lugar_origen(self):
        """Devuelve el lugar de origen, o cadena vacía si no se conoce.

        Eficiencia: O(1).
        """
        return self._lugar_origen

    def relacion(self):
        """Devuelve la relación con el usuario, por ejemplo "mi abuela".

        Eficiencia: O(1).
        """
        return self._relacion

    def poner_nombre(self, nombre):
        """Guarda el nombre de la persona.

        Eficiencia: O(1).
        """
        self._nombre = nombre

    def poner_origen(self, origen):
        """Guarda el lugar de origen de la persona.

        Eficiencia: O(1).
        """
        self._lugar_origen = origen

    def esta_completa(self):
        """Devuelve True si ya tiene nombre y lugar de origen.

        Eficiencia: O(1).
        """
        if self._nombre == "":
            return False
        if self._lugar_origen == "":
            return False
        return True

    def dato_faltante(self):
        """Devuelve "nombre", "origen" o cadena vacía según lo que falte.

        Pide primero el nombre porque es el dato con el que se identifica
        a la persona.

        Eficiencia: O(1).
        """
        if self._nombre == "":
            return "nombre"
        elif self._lugar_origen == "":
            return "origen"
        else:
            return ""


class Usuario(Persona):
    """El usuario de la conversación.

    Hereda de Persona y agrega el archivo donde se guardan sus datos:
    "Juan.txt" cuando se conoce el nombre y "usuario.txt" mientras no.

    Atributos:
        _persistencia (Persistencia): objeto que lee y escribe el archivo.
        _archivo (str): nombre del archivo del usuario.

    Eficiencia: cargar y guardar dependen de la cantidad de personas
    guardadas, es decir O(n).
    """

    def __init__(self, persistencia, nombre="", lugar_origen=""):
        """Crea el usuario con su persistencia y los datos que se conozcan."""
        super().__init__("", "", "usuario")
        self._persistencia = persistencia
        self._archivo = "usuario.txt"
        if nombre != "":
            self.poner_nombre(nombre)
        if lugar_origen != "":
            self.poner_origen(lugar_origen)

    def poner_nombre(self, nombre):
        """Guarda el nombre y arma el nombre del archivo con él.

        Eficiencia: O(1).
        """
        super().poner_nombre(nombre)
        if nombre != "":
            self._archivo = nombre + ".txt"

    def cargar(self):
        """Devuelve las personas del archivo de una conversación anterior.

        Si el archivo no existe devuelve una lista vacía, que es el caso
        normal en la primera conversación.

        Eficiencia: O(n) con n = personas guardadas en el archivo.
        """
        return self._persistencia.cargar(self._archivo)

    def guardar(self, personas):
        """Guarda todas las personas en el archivo del usuario.

        Eficiencia: O(n) con n = personas guardadas.
        """
        self._persistencia.guardar(self._archivo, personas)


class BaseConocimiento:
    """Guarda las personas referenciadas durante la conversación.

    La primera persona de la lista siempre es el usuario.

    Atributos:
        _personas (list): lista de objetos Persona.
        _ultima (Persona): última persona agregada, None si no hay ninguna.

    Eficiencia: agregar es O(n) porque busca si la persona ya existe;
    incompletas es O(n). En una conversación n es pequeño.
    """

    def __init__(self):
        """Crea la base vacía."""
        self._personas = []
        self._ultima = None

    def agregar(self, persona):
        """Agrega una persona o completa la que ya existía.

        Se considera la misma persona a la que coincida en nombre o en
        relación. A la existente solo se le llenan los campos vacíos:
        lo que ya se sabe en la conversación no se pierde.

        Eficiencia: O(n) con n = personas guardadas.
        """
        existente = self._buscar(persona)
        if existente is None:
            self._personas.append(persona)
            self._ultima = persona
            return

        # solo se llenan los campos que están vacíos
        if existente.nombre() == "" and persona.nombre() != "":
            existente.poner_nombre(persona.nombre())
        if existente.lugar_origen() == "" and persona.lugar_origen() != "":
            existente.poner_origen(persona.lugar_origen())
        self._ultima = existente

    def _buscar(self, persona):
        """Devuelve la persona guardada con el mismo nombre o relación,
        o None si no existe.

        Eficiencia: O(n) con n = personas guardadas.
        """
        for guardada in self._personas:
            mismo_nombre = False
            mismo_parentesco = False
            if persona.nombre() != "":
                mismo_nombre = guardada.nombre().lower() == persona.nombre().lower()
            if persona.relacion() != "":
                mismo_parentesco = guardada.relacion().lower() == persona.relacion().lower()
            if mismo_nombre or mismo_parentesco:
                return guardada
        return None

    def incompletas(self):
        """Devuelve las personas a las que les falta algún dato.

        Eficiencia: O(n), recorre todas las personas una sola vez.
        """
        resultado = []
        for persona in self._personas:
            if not persona.esta_completa():
                resultado.append(persona)
        return resultado

    def personas(self):
        """Devuelve la lista completa de personas.

        Eficiencia: O(1), devuelve la lista tal cual.
        """
        return self._personas

    def ultima(self):
        """Devuelve la última persona agregada o None si no hay ninguna.

        Eficiencia: O(1).
        """
        return self._ultima
