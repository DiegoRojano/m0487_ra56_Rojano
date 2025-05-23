from usuari import UsuariRegistrat
from llibres import Llibre
from biblioteca import Biblioteca

if __name__ == "__main__":
    biblio = Biblioteca()

    usuari = UsuariRegistrat()
    usuari.introduir_dades()
    biblio.afegir_usuari(usuari)

    llibre = Llibre()
    llibre.introduir_dades()
    biblio.afegir_llibre(llibre)

    print("\nUsuaris:")
    biblio.imprimir_usuaris()

    print("\nLlibres:")
    biblio.imprimir_llibres()
