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
    """Classe que representa un usuari amb atributs bàsics com el nom, cognoms i DNI.

    Atributs:
        nom (str): El nom de l'usuari. Per defecte és "None".
        cognoms (str): Els cognoms de l'usuari. Per defecte és "None".
        dni (str): El DNI de l'usuari. Per defecte és "None".

    Mètodes:
        __init__(nom="None", cognoms="None", dni="None"):
            Inicialitza una instància de la classe Usuari amb els atributs especificats.
    """
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
    """Classe que representa un llibre amb títol, autor i possible prestatari (DNI).

    Atributs:
        titol (str): El títol del llibre. Per defecte és "None".
        autor (str): L'autor del llibre. Per defecte és "None".
        dni_prestec (str): DNI de l'usuari que té el llibre en préstec, o None si està disponible.

    Mètodes:
        __init__(titol="None", autor="None", dni_prestec=None):
            Inicialitza una instància de la classe Llibre amb els atributs especificats.

        imprimir_dades():
            Mostra per pantalla les dades del llibre. Indica si està prestat o disponible.

        introduir_dades():
            Permet introduir les dades del llibre manualment mitjançant l'entrada de l'usuari.
            Valida que el títol i l'autor no estiguin buits. Torna a demanar dades si hi ha error.
    """
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
    """Classe que gestiona les operacions de la biblioteca mitjançant SQLite.

    Aquesta classe permet crear la base de dades, gestionar usuaris i llibres,
    així com realitzar operacions com préstecs, devolucions, insercions i eliminacions.

    Atributs:
        conn (sqlite3.Connection): Connexió activa amb la base de dades SQLite.

    Mètodes:
        __init__():
            Inicialitza la connexió amb la base de dades i crea les taules si no existeixen.

        crear_taules():
            Crea les taules 'usuaris' i 'llibres' dins la base de dades.

        afegir_usuari(usuari: Usuari):
            Afegeix un nou usuari a la base de dades. Mostra error si el DNI ja existeix.

        afegir_llibre(llibre: Llibre):
            Afegeix un nou llibre a la base de dades. Mostra error si el títol ja existeix.

        imprimir_usuaris() -> list:
            Retorna una llista de tuples amb tots els usuaris registrats.

        imprimir_llibres(filtre: str = "tots") -> list:
            Retorna llibres segons el filtre indicat: "tots", "disponibles" o "prestats".

        eliminar_usuari(dni: str):
            Elimina un usuari de la base de dades pel seu DNI.

        eliminar_llibre(titol: str):
            Elimina un llibre de la base de dades pel seu títol.

        prestar_llibre(titol: str, dni: str):
            Assigna un préstec d’un llibre a un usuari pel seu DNI.

        tornar_llibre(titol: str):
            Marca un llibre com a retornat, esborrant el DNI del préstec.
    """
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
def menu():
    """
    Mostra un menú interactiu per gestionar usuaris i llibres de la biblioteca.
    Permet afegir, llistar, eliminar usuaris i llibres, i gestionar préstecs.
    """
    biblioteca = Biblioteca()
    while True:
        print("\n--- MENÚ BIBLIOTECA ---")
        print("1. Afegir usuari")
        print("2. Llistar usuaris")
        print("3. Eliminar usuari")
        print("4. Afegir llibre")
        print("5. Llistar llibres")
        print("6. Eliminar llibre")
        print("7. Prestar llibre")     # Opció nova: prestar llibre
        print("8. Tornar llibre")      # Opció nova: tornar llibre
        print("0. Sortir")
        opcio = input("Escull una opció: ").strip()

        if opcio == "1":
            # Afegir usuari nou
            usuari = Usuari()
            usuari.introduir_dades()
            biblioteca.afegir_usuari(usuari)
            print("Usuari afegit.")

        elif opcio == "2":
            # Llistar tots els usuaris
            usuaris = biblioteca.imprimir_usuaris()
            if usuaris:
                print("\n--- Usuaris registrats ---")
                for u in usuaris:
                    print(f"Nom: {u[1]} {u[2]}, DNI: {u[0]}")
            else:
                print("No hi ha usuaris a la base de dades.")

        elif opcio == "3":
            # Eliminar un usuari
            dni = input("Introdueix el DNI de l'usuari a eliminar: ").strip()
            biblioteca.eliminar_usuari(dni)
            print("Usuari eliminat (si existia).")

        elif opcio == "4":
            # Afegir llibre nou
            llibre = Llibre()
            llibre.introduir_dades()
            # Quan s'afegeix, el llibre està disponible (dni_prestec = "0")
            llibre.dni_prestec = "0"
            biblioteca.afegir_llibre(llibre)
            print("Llibre afegit.")

        elif opcio == "5":
            # Llistar tots els llibres
            llibres = biblioteca.imprimir_llibres()
            if llibres:
                print("\n--- Llibres registrats ---")
                for l in llibres:
                    estat = f"Prestat a: {l[2]}" if l[2] and l[2] != "0" else "Disponible"
                    print(f"Títol: {l[0]}, Autor: {l[1]}, {estat}")
            else:
                print("No hi ha llibres a la base de dades.")

        elif opcio == "6":
            # Eliminar un llibre
            titol = input("Introdueix el títol del llibre a eliminar: ").strip()
            biblioteca.eliminar_llibre(titol)
            print("Llibre eliminat (si existia).")

        # --- OPCIÓ 7: Prestar llibre a un usuari ---
        elif opcio == "7":
            titol = input("Títol del llibre a prestar: ").strip()
            dni = input("DNI de l'usuari que el rep: ").strip()
            # Comprova que l'usuari existeix
            usuaris = biblioteca.imprimir_usuaris()
            if not any(u[0] == dni for u in usuaris):
                print("No existeix cap usuari amb aquest DNI.")
                continue
            # Comprova que el llibre existeix i està disponible (dni_prestec == "0")
            cursor = biblioteca.conn.cursor()
            cursor.execute("SELECT dni_prestec FROM llibres WHERE titol = ?", (titol,))
            resultat = cursor.fetchone()
            if not resultat:
                print("No existeix cap llibre amb aquest títol.")
            elif resultat[0] != "0":
                print("Aquest llibre ja està prestat.")
            else:
                biblioteca.prestar_llibre(titol, dni)
                print(f"Llibre '{titol}' prestat a l'usuari {dni}.")

        # --- OPCIÓ 8: Tornar llibre prestat ---
        elif opcio == "8":
            titol = input("Títol del llibre a tornar: ").strip()
            cursor = biblioteca.conn.cursor()
            cursor.execute("SELECT dni_prestec FROM llibres WHERE titol = ?", (titol,))
            resultat = cursor.fetchone()
            if not resultat:
                print("No existeix cap llibre amb aquest títol.")
            elif resultat[0] == "0":
                print("Aquest llibre no està en préstec.")
            else:
                biblioteca.prestar_llibre(titol, "0")  # Torna el llibre posant "0"
                print(f"Llibre '{titol}' retornat correctament.")

        elif opcio == "0":
            print("Sortint del programa...")
            break

        else:
            print("Opció no vàlida. Torna-ho a provar.")

# Executa el menú si aquest arxiu és el principal
if __name__ == "__main__":
    menu()
