from webapiVendo import VendoApi
from datetime import datetime, timedelta, date
from FV_anris_obce import parse_date
vendoApi = VendoApi()
vendoApi.setApi("http://192.168.115.184:5565") # PRODUKCJA
vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
vendoApi.logInApi("esklep","e12345")
vendoApi.loginUser("jpawlewski", "jp12345")


czy_aktywny = True
#id_klienta = self._query['Klient1ID']
id_klienta ='19966'
print(id_klienta)
data = date.today()
rozszerzony_klient = vendoApi.getJson(
'/json/reply/CRM_Klienci_KlientRozszerzony',
{"Token":vendoApi.USER_TOKEN,"Model":{"ZwrocPliki":False,"ZwrocLudziKlienta":False,"ZwrocKartyPremiowe":False,"ZwrocWartosciDowolne":False,"ID":id_klienta,"Aktywnosci":["Aktywny"],
"ZwracanePola": [
        "DomyslnaEksportowosc"
    ]}})
print(rozszerzony_klient['Wynik']['Rekordy'])
if len(rozszerzony_klient['Wynik']['Rekordy'])<1:
    czy_aktywny = False
    #return czy_aktywny
if rozszerzony_klient['Wynik']['Rekordy'][0]['Klient']['DomyslnaEksportowosc'] == 'Unijna':
    historia_klienta_euronip = vendoApi.getJson(
        '/json/reply/Plugin_Klienci_HistoriaZapytanOAktywnoscPodatnikaVAT',
        {"Token":vendoApi.USER_TOKEN, "Model":{
        "KlientID": id_klienta }
        })
    print(historia_klienta_euronip)
    for item in historia_klienta_euronip['Wynik']:
        if str(data) == parse_date(item['DataZapytania']):
            czy_aktywny = item.get('Status')
print(czy_aktywny)