# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

from archivos import Persistencia
from frases import FraseClave, GrupoEntrada, GrupoSalida, normalizar
from personas import BaseConocimiento, Persona, Usuario
from repositorio import Cliente_API
from salida import GeneradorRespuestas


class Eliza:
    """Coordina la sesión y el flujo del programa hasta que el usuario se despide"""

    def __init__(self):

        self._api = None
        self._generador = None
        self._persistencia = Persistencia()
        self._base = None
        self._grupos = []
        self._reconocer = {}
        self._esperando = False

    def iniciar(self):
        """Descarga las frases de la API y arma los grupos de la conversación"""

        url = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2627-1/main/"
        self._api = Cliente_API(url)
        datos = self._api.cargar_todo()

        nombres = ["entrada.json", "salida.json", "personas.json", "lugares.json"]

        for nombre in nombres:

            if datos[nombre] is None:
                print("No se pudieron cargar las frases de la API")

                return False

        self._armar_grupos(datos)
        self._base = BaseConocimiento()
        self._base.agregar(Usuario(self._persistencia))
        self._esperando = False

        return True

    def ejecutar(self):
        """Corre la conversación hasta la despedida"""

        if not self.iniciar():
            return

        while True:

            try:
                texto = input("Tú: ")

            except EOFError:
                print("\nLa entrada se cortó: termina la conversación")
                return
            
            except KeyboardInterrupt:
                print("\nConversación interrumpida: hasta pronto")
                return
            
            if texto.strip() == "":
                print("Escribe algo para que pueda responderte")
                continue
            
            respuesta = self.procesar(texto)

            if respuesta is None:
                return
            
            print("Eliza: " + respuesta)

    def procesar(self, texto):
        """Devuelve la respuesta de Eliza para el texto del usuario, o None si se despide"""

        normalizado = normalizar(texto)

        mensaje_especial = self._revisar_prioridades_bajas(normalizado)

        self._recopilar(normalizado, mensaje_especial)

        grupo = self._buscar_grupo(normalizado)

        if grupo is None:
            self._esperando = self._falta_algo()
            return self._generador.siguiente_pregunta(self._base)

        if grupo.es_despedida():
            self._guardar()

            print("Eliza: " + self._generador.responder(grupo, self._base))

            return None

        respuesta = self._generador.responder(grupo, self._base)

        if grupo.prioridad() == 3 and self._base.ultima() is not None:

            if self._base.ultima().nombre() == "":
                self._esperando = True

        return respuesta

    def _buscar_grupo(self, texto):
        """Devuelve el primer grupo que coincide con el texto, ya van ordenados por prioridad"""

        for grupo in self._grupos:

            if grupo.buscar(texto) != "":
                return grupo
            
        return None

    def _revisar_prioridades_bajas(self, texto):
        """Revisa los grupos de prioridad 3 o menos y registra a las personas mencionadas"""

        encontro_algo = False

        for grupo in self._grupos:

            if grupo.prioridad() > 3:
                continue
            
            coincidencia = grupo.buscar(texto)

            if coincidencia == "":
                continue
            
            encontro_algo = True

            if grupo.prioridad() == 3:
                self._base.agregar(Persona(relacion=coincidencia))

        return encontro_algo

    def _armar_grupos(self, datos):
        """Crea los grupos de entrada, de salida, de preguntas y las frases de reconocimiento"""

        self._grupos = []

        for nombre, info in datos["entrada.json"].items():

            frases = []

            for texto in info["Frases clave"]:
                frases.append(FraseClave(texto))

            accion = ""

            if "Acción" in info:
                accion = info["Acción"]

            grupo = GrupoEntrada(nombre, info["Prioridad"], frases, accion)
            self._grupos.append(grupo)

        for i in range(len(self._grupos)):

            for j in range(i + 1, len(self._grupos)):

                if self._grupos[j].prioridad() < self._grupos[i].prioridad():

                    temporal = self._grupos[i]
                    self._grupos[i] = self._grupos[j]
                    self._grupos[j] = temporal

        # quedan ordenados por prioridad de menor a mayor; como son pocos grupos
        # el ordenamiento por seleccion no se nota

        salidas = []

        for nombre, info in datos["salida.json"].items():

            grupo = GrupoSalida(nombre, info["Prioridad"], info["Frases clave"])
            salidas.append(grupo)

        preguntas = {
            "nombre usuario": self._grupo_pregunta(datos["personas.json"]["Preguntar usuario"]),
            "origen usuario": self._grupo_pregunta(datos["lugares.json"]["Preguntar usuario"]),
            "origen persona": self._grupo_pregunta(datos["lugares.json"]["Preguntar relación"]),
        }

        self._generador = GeneradorRespuestas(salidas, preguntas)

        self._reconocer = {
            "usuario": self._frases_de(datos["personas.json"]["Reconocer usuario"]),
            "relacion": self._frases_de(datos["personas.json"]["Reconocer relación"]),
            "lugar": self._frases_de(datos["lugares.json"]["Reconocer lugar"]),
            "gentilicio": self._frases_de(datos["lugares.json"]["Reconocer gentilicio"]),
        }

    def _grupo_pregunta(self, info):
        """Arma un grupo de salida con las frases de una pregunta"""

        return GrupoSalida("Preguntar", 0, info["Frases clave"])

    def _frases_de(self, info):
        """Arma la lista de frases clave de un grupo"""

        frases = []

        for texto in info["Frases clave"]:
            frases.append(FraseClave(texto))

        return frases

    def _falta_algo(self):
        """Indica si a alguna persona registrada le falta algún dato"""

        for persona in self._base.personas():

            if persona.dato_faltante() != "":
                return True
            
        return False

    def _recopilar(self, texto, mensaje_especial):
        """Interpreta el texto como respuesta a una pregunta pendiente"""

        if not self._esperando:
            return
        
        if mensaje_especial:
            return

        usuario = self._base.personas()[0]
        persona = usuario
        es_el_usuario = True

        if usuario.dato_faltante() == "":
            incompletas = self._base.incompletas()

            if len(incompletas) == 0:
                return
            
            persona = incompletas[0]
            es_el_usuario = False

        if persona.dato_faltante() == "nombre":

            if es_el_usuario:
                valor = self._buscar_nombre(texto, "usuario")

            else:
                valor = self._buscar_nombre(texto, "relacion")

        else:
            valor = self._buscar_origen(texto)

        if valor == "":
            return

        if persona.dato_faltante() == "nombre":
            persona.poner_nombre(valor)

            if es_el_usuario:
                self._cargar_archivo(usuario)

        else:
            persona.poner_origen(valor)

        print("Gracias, continua")
        self._esperando = False

    def _buscar_nombre(self, texto, tipo):
        """Devuelve el nombre reconocido en el texto o la primera palabra"""

        nombre = self._buscar_dato(texto, [tipo])

        if nombre == "":
            palabras = texto.split()

            if len(palabras) == 0:
                return ""
            
            nombre = palabras[0]

        return nombre.capitalize()

    def _buscar_origen(self, texto):
        """Devuelve el origen reconocido en el texto o la primera palabra"""

        origen = self._buscar_dato(texto, ["lugar", "gentilicio"])

        if origen == "":
            palabras = texto.split()

            if len(palabras) == 0:
                return ""

            origen = palabras[0]

        return origen.capitalize()

    def _buscar_dato(self, texto, tipos):
        """Devuelve lo que capturen las frases de reconocimiento de los tipos pedidos"""

        for tipo in tipos:

            for frase in self._reconocer[tipo]:

                if frase.coincide(texto) != "":
                    return frase.capturar(texto)
                
        return ""

    def _cargar_archivo(self, usuario):
        """Carga la conversación anterior del usuario si el archivo existe"""

        for persona in usuario.cargar():
            self._base.agregar(persona, solo_vacios=True)

    def _guardar(self):
        """Guarda todas las personas en el archivo del usuario"""
        
        personas = self._base.personas()
        personas[0].guardar(personas)
