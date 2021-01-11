"""
Generowanie FV z WZ
"""
from webapiVendo import VendoApi
from datetime import datetime, timedelta, date
from FV_anris_obce import parse_date

class DokumentWZ:
    """
    Parsuje odpowiedź zapytania o dokument WZ

    Dokument(response)
    * dokument_id -> int
    * numer -> str
    * numer_pelny -> str
    * zamkniety -> 
    """

    def __init__(self, response):
        self._query = response

    @property
    def dokument_id(self):
        return self._query['ID']

    @property
    def numer(self):
        return self._query['Numer']
    
    @property
    def numer_pelny(self):
        return self._query['NumerPelny']

    @property
    def zamkniety(self):
        return self._query['Zamkniety']

    @property
    def fv_zbiorcza(self):
        czy_zbiorcza = False
        for wd in self._query['PolaUzytkownika']:            
            if wd['NazwaWewnetrzna'] == 'fv_zbiorcza' and wd['Wartosc'] == 'Tak':
                czy_zbiorcza = True
            else:
                pass
        return czy_zbiorcza
    
    @property
    def wz_uwagi_do_fakturzystek(self):
        for wd in self._query['PolaUzytkownika']:
            if wd['NazwaWewnetrzna'] == 'uwagi_dla_fakturzystek_wz': #and wd['Wartosc'] == 'Tak':
                if wd['Wartosc']:
                    return False
                else:
                    return True

    @property
    def aktywny_euronip_klienta(self):
        #Łączenie z bazą vendo
        vendoApi = VendoApi()
        vendoApi.setApi("http://192.168.115.184:5560") # PRODUKCJA
        vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
        vendoApi.logInApi("esklep","e12345")
        vendoApi.loginUser("jpawlewski", "jp12345")


        czy_aktywny = True
        id_klienta = self._query['Klient1ID']
        print(id_klienta)
        data = date.today()
        rozszerzony_klient = vendoApi.getJson(
        '/json/reply/CRM_Klienci_KlientRozszerzony',
        {"Token":vendoApi.USER_TOKEN,"Model":{"ZwrocPliki":False,"ZwrocLudziKlienta":False,"ZwrocKartyPremiowe":False,"ZwrocWartosciDowolne":False,"ID":id_klienta,"Aktywnosci":["Aktywny"],
        "ZwracanePola": [
                "DomyslnaEksportowosc"
            ]}})
        #print(rozszerzony_klient['Wynik']['Rekordy'])
        if len(rozszerzony_klient['Wynik']['Rekordy'])<1:
            czy_aktywny = False
            return czy_aktywny
        if rozszerzony_klient['Wynik']['Rekordy'][0]['Klient']['DomyslnaEksportowosc'] == 'Unijna':
            historia_klienta_euronip = vendoApi.getJson(
                '/json/reply/Plugin_Klienci_HistoriaZapytanOAktywnoscPodatnikaVAT',
                {"Token":vendoApi.USER_TOKEN, "Model":{
                "KlientID": id_klienta }
                })
            for item in historia_klienta_euronip['Wynik']:
                print(item)
                if str(data) == parse_date(item['DataZapytania']):
                    czy_aktywny = item.get('Status')
        print(czy_aktywny)
        return czy_aktywny
