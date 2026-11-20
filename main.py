# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

from eliza import Eliza


def main():
    """Arranca la conversación con ELIZA hasta que el usuario se despida.

    Si no se pueden cargar las frases del repositorio, se avisa y el
    programa termina sin errores.

    Eficiencia: O(1); solo crea el objeto y cede el control a la
    conversación.
    """
    eliza = Eliza()
    eliza.ejecutar()


if __name__ == "__main__":
    main()
