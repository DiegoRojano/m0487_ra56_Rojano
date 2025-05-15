import sqlite3
import os
import re
import datetime

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

        dni_valid(dni: str) -> bool:
            Comprova si el DNI compleix el patró espanyol.

        actualitzar_dades(nou_nom, nous_cognoms):
            Actualitza les dades del nom i cognoms de l'usuari.
    """
    DNI_PATTERN = r'^\d{8}[A-HJ-NP-TV-Z]$'

    def __init__(self, nom="None", cognoms="None", dni="None"):
        self.nom = nom
        self.cognoms = cognoms
        self.dni = dni    

    def imprimir_dades(self):
        print(f"{self.nom} {self.cognoms} : {self.dni}")

    @staticmethod
    def dni_valid(dni):
        """Valida si un DNI té el patró correcte (8 dígits + lletra vàlida)"""
        return bool(re.match(Usuari.DNI_PATTERN, dni.upper()))

    def introduir_dades(self):
        try:
            self.nom = input("Introdueix el nom: ").strip()
            self.cognoms = input("Introdueix els cognoms: ").strip()
            self.dni = input("Introdueix el DNI: ").strip().upper()
            if not self.nom or not self.cognoms or not self.dni:
                raise ValueError("Cap camp pot estar buit!")
            if not Usuari.dni_valid(self.dni):
                raise ValueError("El DNI no compleix el patró espanyol (8 xifres + lletra).")
        except Exception as e:
            print(f"Error a la introducció de dades: {e}")
            self.introduir_dades()

    def actualitzar_dades(self, nou_nom, nous_cognoms):
        self.nom = nou_nom
        self.cognoms = nous_cognoms


# Classe Llibre
class Llibre:
    """Classe que representa un llibre amb títol, autor i possible prestatari (DNI).

    Atributs:
        titol (str): El títol del llibre. Per defecte és "None".
        autor (str): L'autor del llibre. Per defecte és "None".
        dni_prestec (str): DNI de l'usuari que té el llibre en préstec, o "0" si està disponible.
        data_prestec (str): Data de préstec en format "YYYY-MM-DD", o None.

    Mètodes:
        actualitzar_dades(nou_titol, nou_autor):
            Actualitza les dades del llibre.
    """
    def __init__(self, titol="None", autor="None", dni_prestec="0", data_prestec=None):
        self.titol = titol
        self.autor = autor
        self.dni_prestec = dni_prestec
        self.data_prestec = data_prestec

    def imprimir_dades(self):
        if self.dni_prestec and self.dni_prestec != "0":
            print(f"{self.titol} ({self.autor}) - Prestat a: {self.dni_prestec} des de {self.data_prestec}")
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

    def actualitzar_dades(self, nou_titol, nou_autor):
        self.titol = nou_titol
        self.autor = nou_autor

# Classe Biblioteca
class Biblioteca:
    """Classe que gestiona les operacions de la biblioteca mitjançant SQLite.

    Ara permet actualitzar usuaris/llibres, controlar màxim 3 llibres/usuari,
    i préstec màxim 1 mes.
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
                dni_prestec TEXT DEFAULT "0",
                data_prestec TEXT DEFAULT NULL,
                FOREIGN KEY (dni_prestec) REFERENCES usuaris(dni)
            )
        ''')
        self.conn.commit()

    # --- USUARIS ---
    def afegir_usuari(self, usuari):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO usuaris VALUES (?, ?, ?)", 
                           (usuari.dni, usuari.nom, usuari.cognoms))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("Error: Ja existeix aquest usuari.")

    def actualitzar_usuari(self, dni, nou_nom, nous_cognoms):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE usuaris SET nom = ?, cognoms = ? WHERE dni = ?",
                       (nou_nom, nous_cognoms, dni))
        self.conn.commit()

    def imprimir_usuaris(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuaris")
        return cursor.fetchall()

    def eliminar_usuari(self, dni):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM usuaris WHERE dni = ?", (dni,))
        self.conn.commit()

    # --- LLIBRES ---
    def afegir_llibre(self, llibre):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO llibres VALUES (?, ?, ?, ?)",
                           (llibre.titol, llibre.autor, llibre.dni_prestec, llibre.data_prestec))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("Error: Ja existeix aquest llibre.")

    def actualitzar_llibre(self, titol, nou_titol, nou_autor):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE llibres SET titol = ?, autor = ? WHERE titol = ?",
                       (nou_titol, nou_autor, titol))
        self.conn.commit()

    def imprimir_llibres(self, filtre="tots"):
        cursor = self.conn.cursor()
        if filtre == "disponibles":
            cursor.execute("SELECT * FROM llibres WHERE dni_prestec = '0'")
        elif filtre == "prestats":
            cursor.execute("SELECT * FROM llibres WHERE dni_prestec != '0'")
        else:
            cursor.execute("SELECT * FROM llibres")
        return cursor.fetchall()

    def eliminar_llibre(self, titol):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM llibres WHERE titol = ?", (titol,))
        self.conn.commit()

    # --- PRÉSTECS I VALIDACIONS ---
    def llibres_en_prestec(self, dni):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM llibres WHERE dni_prestec = ?", (dni,))
        return cursor.fetchone()[0]

    def prestar_llibre(self, titol, dni):
        if self.llibres_en_prestec(dni) >= 3:
            print("Error: L'usuari ja té 3 llibres en préstec.")
            return
        avui = datetime.date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute("UPDATE llibres SET dni_prestec = ?, data_prestec = ? WHERE titol = ?", (dni, avui, titol))
        self.conn.commit()

    def tornar_llibre(self, titol):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE llibres SET dni_prestec = '0', data_prestec = NULL WHERE titol = ?", (titol,))
        self.conn.commit()

    def llibre_passat_de_temps(self):
        """Llista llibres en préstec més de 30 dies"""
        cursor = self.conn.cursor()
        avui = datetime.date.today()
        cursor.execute("SELECT titol, dni_prestec, data_prestec FROM llibres WHERE dni_prestec != '0'")
        resultats = []
        for titol, dni, data in cursor.fetchall():
            if data:
                dies = (avui - datetime.datetime.strptime(data, "%Y-%m-%d").date()).days
                if dies > 30:
                    resultats.append((titol, dni, data, dies))
        return resultats

# --- MENÚ INTERACTIU ---
def menu():
    """
    Mostra un menú interactiu per gestionar usuaris i llibres de la biblioteca.
    Permet afegir, llistar, eliminar, actualitzar usuaris i llibres, i gestionar préstecs.
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
        print("7. Prestar llibre")
        print("8. Tornar llibre")
        print("9. Actualitzar usuari")       # NOVA: Actualitzar usuari
        print("10. Actualitzar llibre")      # NOVA: Actualitzar llibre
        print("11. Llibres amb préstec > 1 mes") # NOVA: Llibres passat de temps
        print("0. Sortir")
        opcio = input("Escull una opció: ").strip()

        if opcio == "1":
            usuari = Usuari()
            usuari.introduir_dades()
            biblioteca.afegir_usuari(usuari)
            print("Usuari afegit.")

        elif opcio == "2":
            usuaris = biblioteca.imprimir_usuaris()
            if usuaris:
                print("\n--- Usuaris registrats ---")
                for u in usuaris:
                    print(f"Nom: {u[1]} {u[2]}, DNI: {u[0]}")
            else:
                print("No hi ha usuaris a la base de dades.")

        elif opcio == "3":
            dni = input("Introdueix el DNI de l'usuari a eliminar: ").strip().upper()
            biblioteca.eliminar_usuari(dni)
            print("Usuari eliminat (si existia).")

        elif opcio == "4":
            llibre = Llibre()
            llibre.introduir_dades()
            llibre.dni_prestec = "0"
            llibre.data_prestec = None
            biblioteca.afegir_llibre(llibre)
            print("Llibre afegit.")

        elif opcio == "5":
            llibres = biblioteca.imprimir_llibres()
            if llibres:
                print("\n--- Llibres registrats ---")
                for l in llibres:
                    estat = f"Prestat a: {l[2]} des de {l[3]}" if l[2] and l[2] != "0" else "Disponible"
                    print(f"Títol: {l[0]}, Autor: {l[1]}, {estat}")
            else:
                print("No hi ha llibres a la base de dades.")

        elif opcio == "6":
            titol = input("Introdueix el títol del llibre a eliminar: ").strip()
            biblioteca.eliminar_llibre(titol)
            print("Llibre eliminat (si existia).")

        elif opcio == "7":
            titol = input("Títol del llibre a prestar: ").strip()
            dni = input("DNI de l'usuari que el rep: ").strip().upper()
            # Comprova que l'usuari existeix
            usuaris = biblioteca.imprimir_usuaris()
            if not any(u[0] == dni for u in usuaris):
                print("No existeix cap usuari amb aquest DNI.")
                continue
            # Comprova que el llibre existeix i està disponible
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
                biblioteca.tornar_llibre(titol)
                print(f"Llibre '{titol}' retornat correctament.")

        elif opcio == "9":
            # Actualitzar usuari
            dni = input("Introdueix el DNI de l'usuari a actualitzar: ").strip().upper()
            nou_nom = input("Nou nom: ").strip()
            nous_cognoms = input("Nous cognoms: ").strip()
            biblioteca.actualitzar_usuari(dni, nou_nom, nous_cognoms)
            print("Dades d'usuari actualitzades.")

        elif opcio == "10":
            # Actualitzar llibre
            titol = input("Introdueix el títol del llibre a actualitzar: ").strip()
            nou_titol = input("Nou títol: ").strip()
            nou_autor = input("Nou autor: ").strip()
            biblioteca.actualitzar_llibre(titol, nou_titol, nou_autor)
            print("Dades del llibre actualitzades.")

        elif opcio == "11":
            # Llistar llibres en préstec > 1 mes
            passat_mes = biblioteca.llibre_passat_de_temps()
            if passat_mes:
                print("\n--- Llibres en préstec més de 30 dies ---")
                for titol, dni, data, dies in passat_mes:
                    print(f"Títol: {titol}, DNI usuari: {dni}, Data préstec: {data}, Dies: {dies}")
            else:
                print("No hi ha llibres fora de termini.")

        elif opcio == "0":
            print("Sortint del programa...")
            break

        else:
            print("Opció no vàlida. Torna-ho a provar.")

