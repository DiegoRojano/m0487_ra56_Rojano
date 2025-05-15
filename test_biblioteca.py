import unittest
import os
import sqlite3
import datetime

from biblioteca import Usuari, Llibre, Biblioteca

class TestUsuari(unittest.TestCase):
    def test_dni_valid(self):
        # DNI correcte
        self.assertTrue(Usuari.dni_valid("12345678Z"))
        self.assertTrue(Usuari.dni_valid("00000000T"))
        # DNI incorrecte
        self.assertFalse(Usuari.dni_valid("1234567A"))
        self.assertFalse(Usuari.dni_valid("ABCDEFGH"))
        self.assertFalse(Usuari.dni_valid("12345678"))

class TestLlibre(unittest.TestCase):
    def test_inicialitzacio(self):
        l = Llibre("El llibre", "Autor", "0", None)
        self.assertEqual(l.titol, "El llibre")
        self.assertEqual(l.dni_prestec, "0")
        self.assertIsNone(l.data_prestec)
    def test_actualitzar_dades(self):
        l = Llibre("TitolAntic", "AutorAntic")
        l.actualitzar_dades("TitolNou", "AutorNou")
        self.assertEqual(l.titol, "TitolNou")
        self.assertEqual(l.autor, "AutorNou")

class TestBiblioteca(unittest.TestCase):
    def setUp(self):
        self.temp_db = "temp_biblio_test.db"
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)
        self.biblio = Biblioteca()
        self.biblio.conn = sqlite3.connect(self.temp_db)
        self.biblio.crear_taules()

    def tearDown(self):
        self.biblio.conn.close()
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

    def test_afegir_i_eliminar_usuari(self):
        u = Usuari("Pau", "Garcia", "12345678A")
        self.biblio.afegir_usuari(u)
        usuaris = self.biblio.imprimir_usuaris()
        self.assertEqual(len(usuaris), 1)
        self.biblio.eliminar_usuari(u.dni)
        self.assertEqual(len(self.biblio.imprimir_usuaris()), 0)

    def test_afegir_i_eliminar_llibre(self):
        l = Llibre("Prova", "Autor", "0", None)
        self.biblio.afegir_llibre(l)
        llibres = self.biblio.imprimir_llibres()
        self.assertEqual(len(llibres), 1)
        self.biblio.eliminar_llibre(l.titol)
        self.assertEqual(len(self.biblio.imprimir_llibres()), 0)

    def test_maxim_3_prestecs(self):
        u = Usuari("Marc", "Ribas", "11111111A")
        self.biblio.afegir_usuari(u)
        # Afegim 4 llibres
        for i in range(4):
            l = Llibre(f"Titol{i}", "Autor", "0", None)
            self.biblio.afegir_llibre(l)
        # Presta 3 llibres
        for i in range(3):
            self.biblio.prestar_llibre(f"Titol{i}", u.dni)
        # El quart ha de donar error i seguir disponible
        self.biblio.prestar_llibre("Titol3", u.dni)
        llibres_prestats = self.biblio.llibres_en_prestec(u.dni)
        self.assertEqual(llibres_prestats, 3)
        cursor = self.biblio.conn.cursor()
        cursor.execute("SELECT dni_prestec FROM llibres WHERE titol = 'Titol3'")
        self.assertEqual(cursor.fetchone()[0], "0")  # segueix disponible

    def test_prestec_mes_de_30_dies(self):
        u = Usuari("Joan", "Casals", "22222222B")
        l = Llibre("LlibreAntic", "Autor", "22222222B", "2022-01-01")
        self.biblio.afegir_usuari(u)
        self.biblio.afegir_llibre(l)
        result = self.biblio.llibre_passat_de_temps()
        self.assertTrue(any(t[0] == "LlibreAntic" for t in result))

    def test_actualitzar_usuari_i_llibre(self):
        u = Usuari("Marta", "Vila", "33333333C")
        l = Llibre("TitolX", "AutorY", "0", None)
        self.biblio.afegir_usuari(u)
        self.biblio.afegir_llibre(l)
        self.biblio.actualitzar_usuari("33333333C", "Martina", "Vilaseca")
        self.biblio.actualitzar_llibre("TitolX", "TitolNou", "AutorNou")
        usuaris = self.biblio.imprimir_usuaris()
        llibres = self.biblio.imprimir_llibres()
        self.assertTrue(any(x[1] == "Martina" for x in usuaris))
        self.assertTrue(any(y[0] == "TitolNou" for y in llibres))

if __name__ == '__main__':
    unittest.main()
