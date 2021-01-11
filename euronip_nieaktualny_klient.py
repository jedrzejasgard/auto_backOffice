from webapiVendo import VendoApi
from datetime import datetime, timedelta, date

def aktywny_euronip_klienta(id_klienta):
        #Łączenie z bazą vendo
        vendoApi = VendoApi()
        vendoApi.setApi("http://192.168.115.184:5560") # PRODUKCJA
        vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
        vendoApi.logInApi("esklep","e12345")
        vendoApi.loginUser("jpawlewski", "jp12345")


        czy_aktywny = True
        
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
            czy_aktywny = False
            historia_klienta_euronip = vendoApi.getJson(
                '/json/reply/Plugin_Klienci_HistoriaZapytanOAktywnoscPodatnikaVAT',
                {"Token":vendoApi.USER_TOKEN, "Model":{
                "KlientID": id_klienta }
                })
            print(f'Klient ID : ,{historia_klienta_euronip["Wynik"]}')
            for item in historia_klienta_euronip['Wynik']:
                data_zapytania = parse_date(item['DataZapytania'])
                if str(data) == parse_date(item['DataZapytania']):
                    print(f'{data_zapytania}-->{item}')
                    czy_aktywny = item.get('Status')
        print(czy_aktywny)
        return czy_aktywny

def parse_date(datestring):
    '''
    Zmienia date w starym formacie Vendo w czytelną
    '''
    timepart = datestring.split('(')[1].split(')')[0]
    milliseconds = int(timepart[:-5])
    hours = int(timepart[-5:]) / 100
    time = milliseconds / 1000
    dt = datetime.fromtimestamp(time + hours * 3600)
    return dt.strftime("%Y-%m-%d")

if __name__ == "__main__":
    aktywny_euronip_klienta(17666)
    pass