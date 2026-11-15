# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

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
        url = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2627-1/main/"
        self._api = Cliente_API(url)
        datos = self._api.cargar_todo()

        # si falta algún JSON y no hay copia local no se puede conversar
        nombres = ["entrada.json", "salida.json", "personas.json", "lugares.json"]
        for nombre in nombres:
            if datos[nombre] is None:
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

        Primero se revisan siempre las prioridades 1, 2 y 3 (la 3 detecta
        personas); después, si se estaba esperando un dato, el texto se
        toma como respuesta. Luego se busca la frase clave: gana la que sea
        igual a todo el texto y, si no hay, la prioridad menor. Devuelve
        None cuando el grupo detectado es de despedida: en ese caso guarda
        el archivo e imprime el adiós.

        Eficiencia: O(g · f · n) con g = 12 grupos, f = frases por grupo
        y n = palabras del texto.
        """
        normalizado = normalizar(texto)

        # 1) las prioridades 1, 2 y 3 se revisan siempre; en el paso 3 se
        #    guarda la relación si se detectó una persona
        mensaje_especial = self._revisar_prioridades_bajas(normalizado)

        # 2) si Eliza estaba esperando un dato, el texto es la respuesta
        self._recopilar(normalizado, mensaje_especial)

        # 3) buscar la frase clave que corresponde
        grupo = self._buscar_grupo(normalizado)
        if grupo is None:
            # no coincidió nada: preguntar lo que falte o seguir la charla
            self._esperando = self._falta_algo()
            return self._generador.siguiente_pregunta(self._base)

        if grupo.es_despedida():
            # la prioridad 1 guarda todo y termina el programa
            self._guardar()
            print("Eliza: " + self._generador.responder(grupo, self._base))
            return None

        respuesta = self._generador.responder(grupo, self._base)
        if grupo.prioridad() == 3 and self._base.ultima() is not None:
            if self._base.ultima().nombre() == "":
                self._esperando = True
        return respuesta

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

    def _revisar_prioridades_bajas(self, texto):
        """Revisa los grupos de prioridad 1, 2 y 3 y devuelve True si alguno
        coincidió (despedida, pésame o mención de persona).

        Si coincide la prioridad 3, la relación detectada se guarda como
        una persona nueva en la base. Estas prioridades se revisan siempre,
        antes que todas las demás.

        Eficiencia: O(f · n) con f = frases de los tres grupos.
        """
        encontro_algo = False
        for grupo in self._grupos:
            if grupo.prioridad() > 3:
                continue
            coincidencia = grupo.buscar(texto)
            if coincidencia == "":
                continue
            encontro_algo = True
            # solo la prioridad 3 (Freudiano) crea personas
            if grupo.prioridad() == 3:
                self._base.agregar(Persona(relacion=coincidencia))
        return encontro_algo

    def _armar_grupos(self, datos):
        """Crea los grupos de entrada, de salida, de preguntas y las
        frases de reconocimiento a partir de los JSON.

        Eficiencia: O(t) donde t es el total de frases.
        """
        # grupos de entrada: uno por cada prioridad del 1 al 12
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

        # ordenar los grupos: la prioridad 1 queda primero (burbuja)
        for i in range(len(self._grupos)):
            for j in range(i + 1, len(self._grupos)):
                if self._grupos[j].prioridad() < self._grupos[i].prioridad():
                    temporal = self._grupos[i]
                    self._grupos[i] = self._grupos[j]
                    self._grupos[j] = temporal

        # grupos de salida: los mismos 12 más el conversacional (prioridad 0)
        salidas = []
        for nombre, info in datos["salida.json"].items():
            grupo = GrupoSalida(nombre, info["Prioridad"], info["Frases clave"])
            salidas.append(grupo)

        # preguntas que se usan cuando falta información
        preguntas = {
            "nombre usuario": self._grupo_pregunta(datos["personas.json"]["Preguntar usuario"]),
            "origen usuario": self._grupo_pregunta(datos["lugares.json"]["Preguntar usuario"]),
            "origen persona": self._grupo_pregunta(datos["lugares.json"]["Preguntar relación"]),
        }
        self._generador = GeneradorRespuestas(salidas, preguntas)

        # frases para reconocer nombres, lugares y gentilicios
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
        frases = []
        for texto in info["Frases clave"]:
            frases.append(FraseClave(texto))
        return frases

    def _falta_algo(self):
        """Devuelve True si al usuario o a alguna persona le falta
        algún dato.

        Eficiencia: O(n) con n = personas de la base.
        """
        for persona in self._base.personas():
            if persona.dato_faltante() != "":
                return True
        return False

    def _recopilar(self, texto, mensaje_especial):
        """Interpreta el texto como respuesta a una pregunta pendiente de
        nombre u origen y guarda el dato si lo reconoce.

        El mensaje_especial viene de _revisar_prioridades_bajas: si es
        True el texto es una despedida, un pésame o una mención de
        persona, así que no se toma como respuesta. El nombre usa frases
        de reconocimiento y, si no hay, la primera palabra del texto. El
        origen solo se guarda con frases de reconocimiento.

        Eficiencia: O(r · n) con r = frases de reconocimiento.
        """
        if not self._esperando:
            return
        if mensaje_especial:
            return

        # 1) quién responde: primero el usuario, después la primera
        #    persona a la que le falte algún dato
        usuario = self._base.personas()[0]
        persona = usuario
        es_el_usuario = True
        if usuario.dato_faltante() == "":
            incompletas = self._base.incompletas()
            if len(incompletas) == 0:
                return
            persona = incompletas[0]
            es_el_usuario = False

        # 2) conseguir el valor del dato que falta
        if persona.dato_faltante() == "nombre":
            if es_el_usuario:
                valor = self._buscar_nombre(texto, "usuario")
            else:
                valor = self._buscar_nombre(texto, "relacion")
        else:
            valor = self._buscar_origen(texto)
        if valor == "":
            return

        # 3) guardar el dato, avisar y dejar de esperar respuestas
        if persona.dato_faltante() == "nombre":
            persona.poner_nombre(valor)
            if es_el_usuario:
                self._cargar_archivo(usuario)
        else:
            persona.poner_origen(valor)
        print("Gracias, continua")
        self._esperando = False

    def _buscar_nombre(self, texto, tipo):
        """Devuelve el nombre reconocido en el texto o la primera palabra.

        El tipo dice qué frases usar: "usuario" para el nombre del
        usuario y "relacion" para el de una persona.

        Eficiencia: O(r · n) con r = frases de reconocimiento.
        """
        nombre = self._buscar_dato(texto, [tipo])
        if nombre == "":
            # sin frase de reconocimiento, la primera palabra es el nombre
            palabras = texto.split()
            if len(palabras) == 0:
                return ""
            nombre = palabras[0]
        return nombre.capitalize()

    def _buscar_origen(self, texto):
        """Devuelve el origen reconocido en el texto o cadena vacía.

        Busca primero frases de lugar ("de *", "en *") y después de
        gentilicio ("es un *", ...).

        Eficiencia: O(r · n) con r = frases de reconocimiento.
        """
        origen = self._buscar_dato(texto, ["lugar", "gentilicio"])
        if origen == "":
            return ""
        return origen.capitalize()

    def _buscar_dato(self, texto, tipos):
        """Devuelve la palabra capturada por las frases de reconocimiento,
        o cadena vacía si ninguna coincide.

        Los tipos dicen qué listas recorrer: "usuario", "relacion",
        "lugar" o "gentilicio".

        Eficiencia: O(r · n) con r = frases de reconocimiento.
        """
        for tipo in tipos:
            for frase in self._reconocer[tipo]:
                if frase.coincide(texto) != "":
                    return frase.capturar(texto)
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
