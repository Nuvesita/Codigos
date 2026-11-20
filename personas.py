# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez


class Persona:
    """Persona referenciada con nombre, lugar de origen y relación"""

    def __init__(self, nombre="", lugar_origen="", relacion=""):
        # Crea una persona con los datos que se conozcan desde el inicio

        self._nombre = nombre
        self._lugar_origen = lugar_origen
        self._relacion = relacion

    def nombre(self):
        # Devuelve el nombre, o cadena vacía si todavía no se conoce

        return self._nombre

    def lugar_origen(self):
        # Devuelve el lugar de origen

        return self._lugar_origen

    def relacion(self):
        # Devuelve la relación con el usuario

        return self._relacion

    def poner_nombre(self, nombre):
        # Guarda el nombre de la persona

        self._nombre = nombre

    def poner_origen(self, origen):
        # Guarda el lugar de origen de la persona

        self._lugar_origen = origen

    def esta_completa(self):

        if self._nombre == "":
            return False
        
        if self._lugar_origen == "":
            return False
        
        return True

    def dato_faltante(self):

        if self._nombre == "":
            return "nombre"
        
        elif self._lugar_origen == "":
            return "origen"
        
        else:
            return ""


class Usuario(Persona):
    """El usuario de la conversación, carga y guarda sus datos en el archivo"""

    def __init__(self, persistencia, nombre="", lugar_origen=""):
        # Crea el usuario con su persistencia y los datos que se conozcan

        super().__init__("", "", "usuario")

        self._persistencia = persistencia
        self._archivo = "usuario.txt"

        if nombre != "":
            self.poner_nombre(nombre)

        if lugar_origen != "":
            self.poner_origen(lugar_origen)

    def poner_nombre(self, nombre):
        # Guarda el nombre y arma el nombre del archivo con él

        super().poner_nombre(nombre)

        if nombre != "":
            self._archivo = nombre + ".txt"

    def cargar(self):
        # Devuelve las personas del archivo de una conversación anterior

        return self._persistencia.cargar(self._archivo)

    def guardar(self, personas):
        # Guarda todas las personas en el archivo del usuario

        self._persistencia.guardar(self._archivo, personas)


class BaseConocimiento:
    """Guarda las personas referenciadas durante la conversación y recuerda la última"""

    def __init__(self):

        self._personas = []
        self._ultima = None

    def agregar(self, persona, solo_vacios=False):
        # Agrega una persona o actualiza la que ya existía

        existente = self._buscar(persona)

        if existente is None:
            self._personas.append(persona)
            self._ultima = persona

            return

        if solo_vacios:
            # solo se llenan los campos que están vacíos

            if existente.nombre() == "" and persona.nombre() != "":
                existente.poner_nombre(persona.nombre())

            if existente.lugar_origen() == "" and persona.lugar_origen() != "":
                existente.poner_origen(persona.lugar_origen())

        else:
            # lo más reciente tiene prioridad sobre lo anterior

            if persona.nombre() != "":
                existente.poner_nombre(persona.nombre())

            if persona.lugar_origen() != "":
                existente.poner_origen(persona.lugar_origen())

        self._ultima = existente

    def _buscar(self, persona):
        # Devuelve la persona guardada con el mismo nombre o relación

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
        # Devuelve las personas a las que les falta algún dato

        resultado = []

        for persona in self._personas:

            if not persona.esta_completa():
                resultado.append(persona)

        return resultado

    def personas(self):
        return self._personas

    def ultima(self):
        return self._ultima