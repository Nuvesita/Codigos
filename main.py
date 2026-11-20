# Proyecto: El Efecto ELIZA - Algoritmos y Programación
# Integrantes: Veronica Alexandra Linares Castillo y Luciano Yanes Martínez

from eliza import Eliza

def main():
    """Arranca la conversación hasta que el usuario se despida"""
    eliza = Eliza()
    eliza.ejecutar()

if __name__ == "__main__":
    main()
