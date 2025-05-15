import sqlite3
import os

# Ruta absoluta al mateix directori que l'script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "biblioteca.db")

# Comprovem si la base de dades existeix, si no la creem
if not os.path.exists(DB):
    with open(DB, 'w') as f:
        pass

# --- CLASSES ---

# Classe Usuari
class Usuari:
    """Classe que representa un usuari amb atributs bàsics com el nom, cognoms i DNI."""
    def __init__(self, nom="None", cognoms="None", dni="None"):
        self.nom = nom
        self.cognoms = cognoms
        self.dni = dni    

    def imprimir_dades(self):
        print(f"{self.nom} {self.cognoms} : {self.dni}")

    def introduir_dades(self):
        try:
            self.nom = input("Introdueix el nom: ").strip()
            self.cognoms = input("Introdueix els cognoms: ").strip()
            self.dni = input("Introdueix el DNI: ").strip()
            if not self.nom or not self.cognoms or not self.dni:
                raise ValueError("Cap camp pot estar buit!")
        except Exception as e:
            print(f"Error a la introducció de dades: {e}")
            self.introduir_dades()


# Classe Llibre
class Llibre:
    """Classe que representa un llibre amb títol, autor i possible prestatari (DNI)."""
    def __init__(self, titol="None", autor="None", dni_prestec=None):
        self.titol = titol
        self.autor = autor
        self.dni_prestec = dni_prestec

    def imprimir_dades(self):
        if self.dni_prestec:
            print(f"{self.titol} ({self.autor}) - Prestat a: {self.dni_prestec}")
        else:
            print(f"{self.titol} ({self.autor}) - Disponible")

    def introduir_dades(self):
        try:
            self.titol = input("Títol del llibre: ").strip()
            self.autor = input("Autor del llibre: ").strip()
            if not self.titol or not self.autor:
                raise ValueError("El títol i l'autor no poden estar buits.")
        except Exception as e:
            print(f"Error a la introducció de dades: {e}")
            self.introduir_dades()


# Classe Biblioteca
class Biblioteca:
    """Classe que gestiona les operacions de la biblioteca amb SQLite."""
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.crear_taules()

    def crear_taules(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuaris (
                dni TEXT PRIMARY KEY,
                nom TEXT,
                cognoms TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llibres (
                titol TEXT PRIMARY KEY,
                autor TEXT,
                dni_prestec TEXT,
                FOREIGN KEY (dni_prestec) REFERENCES usuaris(dni)
            )
        ''')
        self.conn.commit()

    def afegir_usuari(self, usuari):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO usuaris VALUES (?, ?, ?)", 
                           (usuari.dni, usuari.nom, usuari.cognoms))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("Error: Ja existeix aquest usuari.")

    def afegir_llibre(self, llibre):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO llibres VALUES (?, ?, ?)",
                           (llibre.titol, llibre.autor, llibre.dni_prestec))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("Error: Ja existeix aquest llibre.")

    def imprimir_usuaris(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuaris")
        return cursor.fetchall()

    def imprimir_llibres(self, filtre="tots"):
        cursor = self.conn.cursor()
        if filtre == "disponibles":
            cursor.execute("SELECT * FROM llibres WHERE dni_prestec IS NULL")
        elif filtre == "prestats":
            cursor.execute("SELECT * FROM llibres WHERE dni_prestec IS NOT NULL")
        else:
            cursor.execute("SELECT * FROM llibres")
        return cursor.fetchall()

    def eliminar_usuari(self, dni):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM usuaris WHERE dni = ?", (dni,))
        self.conn.commit()

    def eliminar_llibre(self, titol):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM llibres WHERE titol = ?", (titol,))
        self.conn.commit()

    def prestar_llibre(self, titol, dni):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE llibres SET dni_prestec = ? WHERE titol = ?", (dni, titol))
        self.conn.commit()

    def tornar_llibre(self, titol):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE llibres SET dni_prestec = NULL WHERE titol = ?", (titol,))
        self.conn.commit()
