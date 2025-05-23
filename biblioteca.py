import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "..", "biblioteca.db")

class Biblioteca:
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.crear_taules()

    def crear_taules(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuaris (
                dni TEXT PRIMARY KEY, nom TEXT, cognoms TEXT,
                contrasenya TEXT, tipus_usuari TEXT
            )''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llibres (
                titol TEXT PRIMARY KEY, autor TEXT,
                dni_prestec TEXT DEFAULT '0',
                FOREIGN KEY(dni_prestec) REFERENCES usuaris(dni)
            )''')
        self.conn.commit()

    def afegir_usuari(self, usuari):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO usuaris VALUES (?, ?, ?, ?, ?)",
            (usuari.dni, usuari.nom, usuari.cognoms,
             usuari._contrasenya, usuari.tipus_usuari)
        )
        self.conn.commit()

    def afegir_llibre(self, llibre):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO llibres VALUES (?, ?, ?)",
            (llibre.titol, llibre.autor, llibre.dni_prestec)
        )
        self.conn.commit()

    def imprimir_usuaris(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuaris")
        for usuari in cursor.fetchall():
            print(usuari)

    def imprimir_llibres(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM llibres")
        for llibre in cursor.fetchall():
            print(llibre)
