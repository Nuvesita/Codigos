# Proyecto: El Efecto ELIZA - Algoritmos y Programación (BPTSP05) 2627-1
# Integrantes: [NOMBRE 1] y [NOMBRE 2]
# Archivo: eliza.py
# Descripción: clase Eliza, la coordinadora de toda la conversación.

from archivos import Persistencia
from frases import FraseClave, GrupoEntrada, GrupoSalida, normalizar
from personas import BaseConocimiento, Persona, Usuario
from repositorio import Cliente_API
from salida import GeneradorRespuestas


class Eliza:
    """Coordina la sesión: carga las frases, lee lo que escribe el usuario,
    responde y guarda todo al despedirse.

    Atributos:
        _api (Cliente_API): acceso a los JSON del repositorio.
        _generador (GeneradorRespuestas): elige las respuestas.
        _persistencia (Persistencia): lectura y escritura de archivos.
        _base (BaseConocimiento): personas de la conversación.
        _grupos (list): los 12 grupos de entrada ordenados por prioridad.
        _reconocer (dict): frases para reconocer nombres y orígenes.
        _esperando (bool): True cuando la última pregunta fue por un dato
            que todavía falta.

    Eficiencia: procesar recorre los 12 grupos con sus frases, es decir
    O(g · f · n) con g = 12 grupos, f = frases por grupo y n = palabras
    del texto; los tamaños son pequeños y se siente instantáneo.
    """

    def __init__(self):
        """Crea a Eliza vacía; todo se carga en iniciar()."""
        self._api = None
        self._generador = None
        self._persistencia = Persistencia()
        self._base = None
        self._grupos = []
        self._reconocer = {}
        self._esperando = False

    def iniciar(self):
        """Descarga las frases y arma los grupos.

        Devuelve False si no hay datos (sin internet y sin copia local).

        Eficiencia: cuatro llamadas a la red más recorrer los JSON, O(t)
        donde t es el total de frases.
        """
        self._api = Cliente_API("https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2627-1/main/")
        datos = self._api.cargar_todo()
        if any(dato is None for dato in datos.values()):
            print("No se pudieron cargar las frases: no hay internet ni copia local.")
            return False
        self._armar_grupos(datos)
        self._base = BaseConocimiento()
        self._base.agregar(Usuario(self._persistencia))
        self._esperando = False
        return True

    def ejecutar(self):
        """Corre la conversación hasta la despedida o hasta que no haya datos.

        Eficiencia: depende de las veces que hable el usuario; cada turno
        es O(g · f · n).
        """
        if not self.iniciar():
            return
        while True:
            texto = input("Tú: ")
            if texto.strip() == "":
                print("Escribe algo para que pueda responderte.")
                continue
            respuesta = self.procesar(texto)
            if respuesta is None:
                return
            print("Eliza: " + respuesta)

    def procesar(self, texto):
        """Devuelve la respuesta de Eliza para el texto del usuario.

        Primero busca si el texto completo es una frase conocida (esa
        coincidencia gana siempre); si no, revisa los grupos por
        prioridad. Devuelve None cuando el grupo detectado es de
        despedida: en ese caso guarda el archivo e imprime el adiós.

        Eficiencia: O(g · f · n) con g = 12 grupos, f = frases por grupo
        y n = palabras del texto.
        """
        normalizado = normalizar(texto)
        self._recopilar(normalizado)
        self._revisar_personas(normalizado)
        grupo = self._buscar_grupo(normalizado)
        if grupo is not None:
            if grupo.es_despedida():
                self._guardar()
                print("Eliza: " + self._generador.responder(grupo, self._base))
                return None
            respuesta = self._generador.responder(grupo, self._base)
            if grupo.prioridad() == 3 and self._base.ultima() is not None:
                if self._base.ultima().nombre() == "":
                    self._esperando = True
            return respuesta
        self._esperando = self._falta_algo()
        return self._generador.siguiente_pregunta(self._base)

    def _buscar_grupo(self, texto):
        """Devuelve el grupo que coincide con el texto, o None.

        Busca primero una frase que sea igual a todo el texto ("no sé"
        va al grupo Ayuda y no al Positivismo, que solo tiene la palabra
        "no"). Si no hay coincidencia exacta, gana la prioridad menor.

        Eficiencia: O(g · f · n) con g = 12 grupos y f = frases.
        """
        for grupo in self._grupos:
            if grupo.coincide_completa(texto):
                return grupo
        for grupo in self._grupos:
            if grupo.buscar(texto) != "":
                return grupo
        return None

    def _armar_grupos(self, datos):
        """Crea los grupos de entrada, de salida, de preguntas y las
        frases de reconocimiento a partir de los JSON.

        Eficiencia: O(t) donde t es el total de frases.
        """
        self._grupos = []
        for nombre, info in datos["entrada.json"].items():
            frases = [FraseClave(frase) for frase in info["Frases clave"]]
            accion = info.get("Acción", "")
            self._grupos.append(GrupoEntrada(nombre, info["Prioridad"], frases, accion))
        self._grupos.sort(key=lambda grupo: grupo.prioridad())
        salidas = []
        for nombre, info in datos["salida.json"].items():
            salidas.append(GrupoSalida(nombre, info["Prioridad"], info["Frases clave"]))
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
        """Arma un grupo de salida con las frases de una pregunta.

        Eficiencia: O(1).
        """
        return GrupoSalida("Preguntar", 0, info["Frases clave"])

    def _frases_de(self, info):
        """Arma la lista de frases clave de un grupo del JSON.

        Eficiencia: O(f) con f = frases del grupo.
        """
        return [FraseClave(frase) for frase in info["Frases clave"]]

    def _falta_algo(self):
        """Devuelve True si al usuario o a alguna persona le falta
        algún dato.

        Eficiencia: O(n) con n = personas de la base.
        """
        for persona in self._base.personas():
            if persona.dato_faltante() != "":
                return True
        return False

    def _recopilar(self, texto):
        """Interpreta el texto como respuesta a una pregunta pendiente de
        nombre u origen y guarda el dato si lo reconoce.

        El nombre usa frases de reconocimiento y, si no hay, la primera
        palabra del texto. El origen solo se guarda con frases de
        reconocimiento. Si el texto es una despedida, un pésame o una
        mención de persona, no se interpreta como respuesta.

        Eficiencia: O(r · n) con r = frases de reconocimiento.
        """
        if not self._esperando:
            return
        if self._es_mensaje_especial(texto):
            return
        usuario = self._base.personas()[0]
        if usuario.dato_faltante() == "nombre":
            nombre = self._buscar_nombre(texto, "usuario")
            if nombre == "":
                return
            usuario.poner_nombre(nombre)
            self._cargar_archivo(usuario)
            print("Gracias, continua")
            self._esperando = False
            return
        if usuario.dato_faltante() == "origen":
            origen = self._buscar_origen(texto)
            if origen == "":
                return
            usuario.poner_origen(origen)
            print("Gracias, continua")
            self._esperando = False
            return
        for persona in self._base.incompletas():
            if persona.dato_faltante() == "nombre":
                nombre = self._buscar_nombre(texto, "relacion")
                if nombre == "":
                    return
                persona.poner_nombre(nombre)
            else:
                origen = self._buscar_origen(texto)
                if origen == "":
                    return
                persona.poner_origen(origen)
            print("Gracias, continua")
            self._esperando = False
            return

    def _revisar_personas(self, texto):
        """Revisa siempre la prioridad 3 y guarda la relación detectada.

        Eficiencia: O(f · n) con f = frases de la prioridad 3.
        """
        for grupo in self._grupos:
            if grupo.prioridad() == 3:
                relacion = grupo.buscar(texto)
                if relacion != "":
                    self._base.agregar(Persona(relacion=relacion))
                return

    def _es_mensaje_especial(self, texto):
        """Devuelve True si el texto es despedida, pésame o una mención
        de persona (prioridades 1, 2 y 3).

        Eficiencia: O(f · n) con f = frases de esos tres grupos.
        """
        for grupo in self._grupos:
            if grupo.prioridad() <= 3 and grupo.buscar(texto) != "":
                return True
        return False

    def _buscar_nombre(self, texto, tipo):
        """Devuelve el nombre reconocido en el texto o la primera palabra.

        El tipo dice qué frases usar: "usuario" para el nombre del
        usuario y "relacion" para el de una persona.

        Eficiencia: O(r · n) con r = frases de reconocimiento.
        """
        for frase in self._reconocer[tipo]:
            if frase.coincide(texto) != "":
                return frase.capturar(texto).capitalize()
        palabras = texto.split()
        if len(palabras) == 0:
            return ""
        return palabras[0].capitalize()

    def _buscar_origen(self, texto):
        """Devuelve el origen reconocido en el texto o cadena vacía.

        Busca primero frases de lugar ("de *", "en *") y después de
        gentilicio ("es un *", ...).

        Eficiencia: O(r · n) con r = frases de reconocimiento.
        """
        for tipo in ("lugar", "gentilicio"):
            for frase in self._reconocer[tipo]:
                if frase.coincide(texto) != "":
                    return frase.capturar(texto).capitalize()
        return ""

    def _cargar_archivo(self, usuario):
        """Carga la conversación anterior del usuario si el archivo existe.

        Eficiencia: O(n) con n = personas en el archivo.
        """
        for persona in usuario.cargar():
            self._base.agregar(persona)

    def _guardar(self):
        """Guarda todas las personas en el archivo del usuario.

        La primera persona de la base siempre es el usuario.

        Eficiencia: O(n) con n = personas guardadas.
        """
        personas = self._base.personas()
        personas[0].guardar(personas)
