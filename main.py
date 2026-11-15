# Proyecto: El Efecto ELIZA - Algoritmos y Programación (BPTSP05) 2627-1
# Integrantes: [NOMBRE 1] y [NOMBRE 2]
# Archivo: main.py
# Descripción: arranque del programa, menú y validación de la entrada.

from eliza import Eliza


def main():
    """Muestra el menú y arranca la conversación.

    Si el usuario escribe algo que no es 1 ni 2, se lo hace saber y
    vuelve a pedir la opción.
    """
    eliza = Eliza()
    while True:
        print("1. Iniciar conversación")
        print("2. Salir")
        opcion = input("Escribe una opción: ").strip()
        if opcion == "1":
            eliza.ejecutar()
            return
        if opcion == "2":
            print("Hasta pronto.")
            return
        print("Opción inválida: escribe 1 o 2.")


if __name__ == "__main__":
    main()
