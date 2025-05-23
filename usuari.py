import hashlib

class Usuari:
    def __init__(self, nom="None", cognoms="None", dni="None"):
        self.nom = nom
        self.cognoms = cognoms
        self.dni = dni

    def imprimir_dades(self):
        print(f"{self.nom} {self.cognoms} : {self.dni}")

    def introduir_dades(self):
        self.nom = input("Nom: ").strip()
        self.cognoms = input("Cognoms: ").strip()
        self.dni = input("DNI: ").strip().upper()


class UsuariRegistrat(Usuari):
    def __init__(self, nom="None", cognoms="None", dni="None", contrasenya="", tipus_usuari="normal"):
        super().__init__(nom, cognoms, dni)
        self._contrasenya = self._encripta_contrasenya(contrasenya)
        self.tipus_usuari = tipus_usuari

    def _encripta_contrasenya(self, contrasenya):
        return hashlib.sha256(contrasenya.encode()).hexdigest()

    def verificar_contrasenya(self, contrasenya):
        return self._contrasenya == hashlib.sha256(contrasenya.encode()).hexdigest()

    def introduir_dades(self):
        super().introduir_dades()
        pwd = input("Contrasenya: ").strip()
        self._contrasenya = self._encripta_contrasenya(pwd)
        self.tipus_usuari = input("Tipus usuari (normal/admin): ").strip().lower()
