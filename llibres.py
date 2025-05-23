class Llibre:
    def __init__(self, titol="None", autor="None", dni_prestec="0"):
        self.titol = titol
        self.autor = autor
        self.dni_prestec = dni_prestec

    def imprimir_dades(self):
        estat = f"Prestat a {self.dni_prestec}" if self.dni_prestec != "0" else "Disponible"
        print(f"{self.titol} ({self.autor}) - {estat}")

    def introduir_dades(self):
        self.titol = input("Títol: ").strip()
        self.autor = input("Autor: ").strip()
