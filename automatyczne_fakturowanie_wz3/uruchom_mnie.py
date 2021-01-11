"""Aplikacja fakturuje dokumenty WZ.
Zmknięte WZ są fakturowane gdy nie mają wczceśniej wystawionej FV.
Otwarte WZ są fakturowane gdy dzień w którym uruchomiona jest aplikacja jest
ostatnim dniem miesiaca oraz godzina w czasie uruchomienia aplikacji jest większa niż
wskazana w ustawieniach aplikacji.
"""


import sys
import datetime
import requests
from assets.api_vendo.config import API_CONFIG
from assets.api_vendo.api_auth import AutoryzacjaZaloguj
from assets.api_vendo.api_dokumenty_dokumenty_lista import DokumentyDokumentyLista
from assets.api_vendo.api_dokumenty_zafakturuj_wz import ZafakturujWZ
from assets.dokument_wz import DokumentWZ
from assets.helper_functions import today, mozna_fakturowac_otwarte_wz
from FV_anris_obce import mainFV,dodanie_kosztow,cena_uslugi,pobierz_liste_FV,zmiana_WD_Anris,zmiana_WD_Obce

# usuń przed uruchomieniem
#class TEST:
#    pass

# Godzina od której mają być fakturowane otwarte WZ
GODZINA = 15

# autoryzacja
try:
    API_AUTH = AutoryzacjaZaloguj(**API_CONFIG)
    API_AUTH.login_to_api()
    USER_TOKEN = API_AUTH.user_token
except requests.exceptions.ConnectionError:
    msg = 'Brak połączenia z API.'
    msg_size = 50
    print()
    print('#' * msg_size)
    print('#' + ' ' * ((msg_size - len(msg))//2) + msg + ' ' * ((msg_size - len(msg))//2 - 2) + '#')
    print('#' * msg_size)
    print()
    sys.exit()


def wystaw_fv_do_wz(wz_id, user_token, api_url):
    print('wystawiam FV do WZ')
    """
    Wystawia jedną FV do jednej WZ
    """
    dok = ZafakturujWZ(user_token, api_url)
    dok.dokumenty_zrodlowe = [wz_id]
    return dok.send_request()


def zafakturuj_dokumenty(lista_dokumentow):
    print('Zafaktorywuje dok.')
    # pozytywna odpowiedź api
    if lista_dokumentow.status_code == 200:
        # iteruje przez dokumenty WZ
        for dokument in lista_dokumentow.json()['Wynik']['Rekordy']:
            dok_wz = DokumentWZ(dokument)
            
            # pomija dokumenty z zaznaczoną FV zbiorcza na Tak
            
            if dok_wz.fv_zbiorcza:
                continue
            if not dok_wz.aktywny_euronip_klienta:
                continue
            if dok_wz.wz_uwagi_do_fakturzystek:
                print(dok_wz.dokument_id)
            response = wystaw_fv_do_wz(dok_wz.dokument_id,
                                    USER_TOKEN,
                                    API_CONFIG['api_url'])
            if response.status_code != 200:
                print(response.json()['ResponseStatus']['Message'])
    else:
        raise ConnectionAbortedError('Problem z połaczeniem.')


def main():
    if datetime.datetime.now().hour == 18 and datetime.datetime.now().minute < 40:
        dodanie_kosztow()

    if datetime.datetime.now().hour > 9 and datetime.datetime.now().hour < 19 :
        # Lista dokumentów zamkniętych
        dok_lista = DokumentyDokumentyLista(USER_TOKEN, API_CONFIG['api_url'])
        dok_lista.rodzaj_kod = 'WZ'
        dok_lista.rok = 20
        dok_lista.sortowanie = 'ID'
        dok_lista.sortowanie_rosnaco = True
        dok_lista.strona_index = 0
        dok_lista.strona_liczba_rekordow = 1000
        dok_lista.data_czas_modyfikacji = today()

        dok_lista.zamkniety = True
        zafakturuj_dokumenty(dok_lista.send_request())

        if mozna_fakturowac_otwarte_wz(datetime.date.today(), GODZINA):
            dok_lista.zamkniety = False
            zafakturuj_dokumenty(dok_lista.send_request())
        
        #Sprawdza faktury i wykonawców na ZLP odpowiednio nadając WD Anris/Obce

        mainFV()
    else:
        pass

if __name__ == '__main__':
    main()
