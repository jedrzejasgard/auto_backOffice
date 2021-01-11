import unittest
import datetime
from pprint import pprint
from assets.api_vendo.api_auth import AutoryzacjaZaloguj
from assets.api_vendo.api_dokumenty_dokumenty_lista import DokumentyDokumentyLista
from assets.api_vendo.api_dokumenty_zafakturuj_wz import ZafakturujWZ
from assets.dokument_wz import DokumentWZ
from assets.helper_functions import (today,
                                     ostatni_dzien_miesiaca,
                                     hour_threshold,
                                     mozna_fakturowac_otwarte_wz)


class DokumentWZTest(unittest.TestCase):

    def setUp(self):
        self.auth_config = {
            'api_url': 'http://localhost:82',
            'api_user': 'esklep',
            'api_user_pswd': 'e12345',
            'v_user': 'stronawww',
            'v_user_pswd': 's12345'}

        api_auth = AutoryzacjaZaloguj(**self.auth_config)
        api_auth.login_to_api()
        self.user_token = api_auth.user_token

        self.dok_lista = DokumentyDokumentyLista(self.user_token,
                                                 self.auth_config['api_url'])
        self.dok_lista.rodzaj_kod = 'WZ'
        self.dok_lista.rok = 18
        self.dok_lista.sortowanie = 'ID'
        self.dok_lista.sortowanie_rosnaco = False
        self.dok_lista.strona_index = 0
        self.dok_lista.strona_liczba_rekordow = 10


    def test_czy_prawidlowa_data_today(self):
        """
        Poprawność zwracanego formatu daty.
        """
        self.assertEqual(
            datetime.date.today().strftime('%Y-%m-%d'),
            today()
        )

    def test_hour_threshold_24_hour_clock(self):
        hours = [25,-1]
        for hour in hours:
            with self.assertRaises(AttributeError):
                hour_threshold(datetime.time(12, 00), hour)


    def test_hour_threshold_arguments_types(self):
        with self.assertRaises(TypeError):
            hour_threshold('', 12)

        with self.assertRaises(TypeError):
            hour_threshold(datetime.time(12, 00), '')

                
    def test_hour_threshold_return_true_when_above_threshold(self):
        time = datetime.time(14, 30)
        self.assertTrue(hour_threshold(time, 12))


    def test_mozna_fakturowac_otwarte_wz(self):
        odm = datetime.date(2018, 6, 30)
        ht = datetime.datetime.now().hour - 1

        # Ostatni dzień miesiąca oraz hour_threshold ustawione na godzinę
        # przed aktualną godziną
        # test powienien zwrócić True
        self.assertTrue(mozna_fakturowac_otwarte_wz(odm, ht))

        # hour_threshold ustawiony na godzinę po aktualnej godzinie
        # test powinien zwrócić False
        self.assertFalse(mozna_fakturowac_otwarte_wz(odm, ht + 2))

    @unittest.skip('Wymaga przygotowania bazy vendo.')    
    def test_czy_dokument_jest_zamkniety(self):
        """
        Na bazie testowej utworzony jest dokumentu WZ
        - zamkniety
        - nie zafakturowany
        Numer WZ: 13551/A/18/WZ
        Data utworzenia: 25.06.2018

        Czy dokument jest zamknięty.
        """
        self.dok_lista.dokument_id = 847268  # WZ zamknięte w vendo (baza testowa)

        response = self.dok_lista.send_request().json()
        dok_wz = DokumentWZ(response['Wynik']['Rekordy'][0])
        self.assertTrue(dok_wz.zamkniety, response)         

    @unittest.skip('Wymaga przygotowania dokumentów w vendo')
    def test_pobieranie_tylko_zamknietych_lub_otwartych_dokumentow(self):
        """
        Test sprawdza czy jak zapytanie dotyczy wyłącznie zamknietych
        dokumentów to czy na liście pojawią się otwarte dokumenty.

        WZ otwarte:
        - 13557/A/18/WZ | 847289
        - 13558/A/18/WZ | 847290
        WZ zamkniete:
        - 13559/A/18/WZ | 847291
        - 13560/A/18/WZ | 847292
        - 13561/A/18/WZ | 847293
        - 13562/A/18/WZ | 847295
        """
        
        zamkniete = [847291, 847292, 847293, 847295]
        otwarte = [847289, 847290]
        self.dok_lista.dokumenty_lista_id = zamkniete + otwarte

        self.dok_lista.zamkniety = True
        response = self.dok_lista.send_request().json()
        for d in response['Wynik']['Rekordy']:
            dok = DokumentWZ(d)
            self.assertTrue(dok.zamkniety)
        # ilość dokumentów w zapytaniu równa ilości zamkniętych dokumentów
        self.assertEqual(len(zamkniete), len(response['Wynik']['Rekordy']))

        self.dok_lista.zamkniety = False
        response = self.dok_lista.send_request().json()
        for d in response['Wynik']['Rekordy']:
            dok = DokumentWZ(d)
            self.assertFalse(dok.zamkniety)
        # ilość dokumentów w zapytaniu równa ilości otwartych dokumentów
        self.assertEqual(len(otwarte), len(response['Wynik']['Rekordy']))

    @unittest.skip('Wymaga przygotowania dokumentó w vendo.')    
    def test_fakturowanie_zafakturowanego_dokumentu_wz(self):
        """
        Na bazie testowej utworzony jest dokument WZ
        - zamkniety
        - zafakturowany
        Numer WZ: 13555/A/18/WZ
        Data utworzenia: 25.06.2018

        Wystawienie FV do zafakturowanego dokumentu.

        Jeżeli WZ ma FV to nie można dokumentu ponownie zafakturować.
        """
        self.dok_lista.dokument_id = 847274  # WZ zamknięte i zafakturowane

        # próba ponownego fakturowania WZ
        zwz = ZafakturujWZ(self.user_token, self.auth_config['api_url'])
        zwz.dokumenty_zrodlowe = [self.dok_lista.dokument_id]
        self.assertEqual(zwz.send_request().status_code, 500)

    @unittest.skip('Wymaga przygotowania dokumentów w vendo.')
    def test_fakturowanie_zamknietego_dokuementu_wz(self):
        """
        Przed testem odepnij z dokumentu FV dokumenty magazynowe,
        następnie usuń dokument FV.

        Numer WZ: 13556/18/A/WZ
        Data utworzenia: 25.06.2018
        """
        self.dok_lista.dokument_id = 847285
        response = self.dok_lista.send_request().json()


    def test_czy_ostatni_dzien_miesiaca(self):
        """
        Jeżeli jutro miesiąc będzie inny niż dziś to funkcja zwróci True.
        """
        
        self.assertTrue(ostatni_dzien_miesiaca(
            datetime.date(2018,6,30)
        ))
        self.assertFalse(ostatni_dzien_miesiaca(
            datetime.date(2018,6,29)
        ))


    def test_ostatni_dzien_miesiaca_typ_argumentu(self):
        """
        Sprawdza typ paramentru
        """
        args = [1,'sdfsf', {'a':2}, [1,2,3]]

        for arg in args:
            with self.assertRaises(TypeError):
                ostatni_dzien_miesiaca(arg)

        
    @unittest.skip('Przed testem należy przygotować dokumenty w vendo.')
    def test_fakturowanie_otwartego_dokumentu_wz(self):
        """
        Przed testem odepnij z dokumentu FV dokumenty magazynowe,
        następnie usuń dokument FV.

        Numer WZ: 13554/18/A/WZ
        Data utworzenia: 25.06.2018
        """
        data_dzis = datetime.date.today().strftime("%Y-%m-%d")
        self.dok_lista.data_czas_modyfikacji = data_dzis
        self.dok_lista.dokument_id = 847273
        response = self.dok_lista.send_request().json()

        dok_wz = DokumentWZ(response['Wynik']['Rekordy'][0])

        zwz = ZafakturujWZ(self.user_token, self.auth_config['api_url'])
        zwz.dokumenty_zrodlowe = [dok_wz.dokument_id]
        response_fakturowanie = zwz.send_request()
        self.assertEqual(response_fakturowanie.status_code,
                         200,
                         response_fakturowanie.json())


    def test_sprawdzenie_czy_wd_fv_zbiorczna_na_dokumencie(self):
        """Sprawdza czy prawidłowo odczytywana jest wd FV zbiorcza na dokumencie.

        Wartość dowolna FV zbiorcza ustawiana jest na dokumencie automatycznie na
        podstawie wartości TAK/NIE/NULL w karcie klienta który na dokumencie jest
        nabywcą.
        """

        # WZ z nabywcą z ustawioną wd FV zbiorcza na Tak
        self.dok_lista.dokument_id = 869617
        response = self.dok_lista.send_request().json()
        self.assertTrue(DokumentWZ(response['Wynik']['Rekordy'][0]).fv_zbiorcza)

        # WZ z nabywcą z ustawioną wd FV zbiorcza na Nie
        self.dok_lista.dokument_id = 869618
        response = self.dok_lista.send_request().json()
        self.assertFalse(DokumentWZ(response['Wynik']['Rekordy'][0]).fv_zbiorcza)

        
        # WZ z nabywcą z ustawioną wd FV zbiorcza na null
        self.dok_lista.dokument_id = 869614
        response = self.dok_lista.send_request().json()
        self.assertFalse(DokumentWZ(response['Wynik']['Rekordy'][0]).fv_zbiorcza)


    # @unittest.skip('Zależne od ilości dokumentów w danym dniu')    
    def test_pobieranie_dokumentow_bez_fv_zbiorcza(self):
        self.dok_lista.wartosci_dowolne = {'Typ':'Tekst',
                                           'Wartosci':['Tak'],
                                           'Nazwa':'fv_zbiorcza'}

        data_dzis = datetime.date.today().strftime("%Y-%m-%d")
        self.dok_lista.data_czas_modyfikacji = data_dzis
        
        response = self.dok_lista.send_request().json()
        dok_zbiorcza_tak, dok_zbiorcza_nie = 0, 0
        for dok in response['Wynik']['Rekordy']:
            wz = DokumentWZ(dok)
            if wz.fv_zbiorcza:
                dok_zbiorcza_tak += 1
            else:
                dok_zbiorcza_nie += 1

        # zależne od daty wywołania testu
        self.assertEqual(dok_zbiorcza_tak, 2)
        self.assertEqual(dok_zbiorcza_nie, 4)
        
if __name__ == '__main__':
    unittest.main()
