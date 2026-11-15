# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

from eliza import Eliza


def main():
    """Muestra el menú y arranca la conversación.

    Si el usuario escribe algo que no es 1 ni 2, se lo hace saber y
    vuelve a pedir la opción.

    Eficiencia: O(1); solo imprime y lee lo que escriba el usuario.
    """
    eliza = Eliza()
    while True:
        print("1. Iniciar conversación")
        print("2. Salir")
        opcion = input("Escribe una opción: ").strip()

        # validar la opción antes de usarla
        if opcion == "1":
            eliza.ejecutar()
            return
        elif opcion == "2":
            print("Hasta pronto.")
            return
        else:
            print("Opción inválida: escribe 1 o 2.")


if __name__ == "__main__":
    main()
