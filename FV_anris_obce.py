import json
from webapiVendo import VendoApi
from datetime import datetime, timedelta, date
import pandas as pd

data = date.today()
dataStart= date.today() - timedelta(days=1)

#Łączenie z bazą vendo
vendoApi = VendoApi()
# vendoApi.setApi("http://localhost:5575") BOT
vendoApi.setApi("http://192.168.115.184:5565") # testowe Vendo
vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
vendoApi.logInApi("esklep","e12345")
vendoApi.loginUser("jpawlewski", "jp12345")

# indeksy produktów które przy pojawieniu się na FV muszą zmienić WD Obce -> True:
lista_obce = ["27372","27375","27109","27779","27777","27106","27103","27701","27702","27703","27704","27705","27706","27707","27708","27709","27796"]
# indeksy produktów które przy pojawieniu się na FV muszą zmienić WD Anris -> True:
lista_anris_bez_sprawdzania = ["27043","27037","27044","27038","27371","27402","27403","27400","27401","27404"]
# indeksy produktów które przy pojawieniu się na FV oraz mają na ZLP Wykonawce Anris(id 189) muszą zmienić WD Anris -> True:
lista_anris_ZLP=['27006','27046','27007','27008','27009','27010','27047','27014','27039','27718','27040','27041','27719','27720','27721','27042','27784','27785','27786','27887','27383','27384','27385','27386','27387','27388','27389','27390','27710','27711','27712','27713','27714','27715','27716','27717','27405','27406','27407','27408','27409','27410','27411','27412','27413','27414','27415','27416','27417','27418','27419','27420','27788','27789','27790','27791','27792','27793','27794','27795','27012','27050']

# funkcje zmieniające WD 
def zmiana_WD_Anris(idFV):
    vendoApi.getJson(
        '/json/reply/DB_UstawWartoscDowolna',
        {"Token":vendoApi.USER_TOKEN,"Model":{
        "ObiektTypDanych":"Dokument","ObiektID":idFV,"Typ":"TakNie","Wartosci":True,"Nazwa":"znak_anris"}
        })


def zmiana_WD_Obce(idFV):
    vendoApi.getJson(
        '/json/reply/DB_UstawWartoscDowolna',
        {"Token":vendoApi.USER_TOKEN,"Model":{
        "ObiektTypDanych":"Dokument","ObiektID":idFV,"Typ":"TakNie","Wartosci":True,"Nazwa":"znak_obce"}
        })


def wpisanie_kosztow_anris(cena,obiekt_id):
    #print(obiekt_id)
    r = vendoApi.getJson(
        '/json/reply/DB_UstawWartoscDowolna',
        {"Token":vendoApi.USER_TOKEN,"Model":{
        "ObiektTypDanych":"PozycjaDokumentu","ObiektID":obiekt_id,"Typ":"Liczba","Wartosci":cena,"Nazwa":"FV_koszty_anris"}
        })
    #print(r)


def wpisanie_kosztow_obce(cena,obiekt_id):
    #print(obiekt_id)
    r = vendoApi.getJson(
        '/json/reply/DB_UstawWartoscDowolna',
        {"Token":vendoApi.USER_TOKEN,"Model":{
        "ObiektTypDanych":"PozycjaDokumentu","ObiektID":obiekt_id,"Typ":"Liczba","Wartosci":cena,"Nazwa":"FV_koszty_inne"}
        })
    #print(r)


# sprawdza czy są komentarze do fakturzystek na WZ
def uwagi_do_fakturzystek(WDfaktury):
    for item in WDfaktury:
        if item['NazwaWewnetrzna'] == 'Wykonawca':
            if item.get('Wartosc'):
                return False
            else:
                return True
                #print(True)


# sprawdza czy euronip był sprwawdzony i czy jest 'Pozytywny'
def sprawdzanie_EuroNIP(id_klienta):
    rozszerzony_klient = vendoApi.getJson(
    '/json/reply/CRM_Klienci_KlientRozszerzony',
    {"Token":vendoApi.USER_TOKEN,"Model":{"ZwrocPliki":False,"ZwrocLudziKlienta":False,"ZwrocKartyPremiowe":False,"ZwrocWartosciDowolne":False,"ID":9921,"Aktywnosci":["Aktywny"],
    "ZwracanePola": [
            "DomyslnaEksportowosc"
        ]}})
    #print(rozszerzony_klient['Wynik']['Rekordy'])
    eksportowosc = rozszerzony_klient['Wynik']['Rekordy'][0]['Klient']['DomyslnaEksportowosc']
    if eksportowosc == 'Unijna':
        print('Sprawdzam Euronip')
        return False
    else:
        return True


def forma_platnosci(id):
    zostaw_w_buforze = [2,12,17,16,18,53,20,11,15]
    if id in zostaw_w_buforze:
        return False
    else:
        return True


#wczytanie cen Obce/ANris z pliku exel przygotowanego przez BO
def cennik():
    with open('cennik_anris_obce.xls','rb')as plik_cennik:
        return pd.read_excel(plik_cennik, usecols='A,C,D,E,F,G,H,I')


#zwaraca ceny danej uzługi
def cena_uslugi(cennik_uslug,kod_uslugi,ilosc):
    kod_uslugi = int(kod_uslugi)
    ilosc = int(ilosc)
    for index_row,row in cennik_uslug.iterrows():
        cena = 0
        if kod_uslugi == int(row[0]):
            if ilosc <= 49:
                cena = row[1]
            elif ilosc <= 99:
                cena = row[2]
            elif ilosc <= 249:
                cena = row[3]
            elif ilosc <= 499:
                cena = row[4]
            elif ilosc <= 999:
                cena = row[5]
            elif ilosc <= 2499:
                cena = row[6]
            elif ilosc <= 4999:
                cena = row[7]
        else:
            continue
        return round(float(cena),2)
        #print(f'Cena do wpisania {cena}')


#pobiera listę niezamknietych FV( z numerem 0 ) z Serią A
def mainFV():
    cennik_uslug = cennik()
    lista_FV=vendoApi.getJson(
            '/json/reply/Dokumenty_Dokumenty_Lista',
            {"Token":vendoApi.USER_TOKEN,"Model":{
            "Rodzaj": {
                "Kod": "FV",
                'Seria':'   A'},
            "DataOd": json.dumps(dataStart, indent=4, sort_keys=True,default=str),
            "Zamkniete": False,
            }
        })
    lista_FV = lista_FV['Wynik']['Rekordy']
    #print(lista_FV)
    for faktura in lista_FV:
        #print(faktura)
        numer_FV = faktura['Numer']
        seria_FV = faktura['Seria'].strip()
        if seria_FV == 'A' and numer_FV == 0:
            id_FV = faktura['ID']
            #print(id_FV)
            #Sprawdza czy do danej FV jest ZLP
            try:
                idZLP = int(faktura['ZlecenieID'])
            except:
                continue
            towarID = []
            uslugi = {}
            obiekt_ID = {}
            # Rozdziele pozycje FV na towary oraz usługi
            for item in faktura['Pozycje']:
                element_id = item['ElementID']
                #print(element_id)
                id_prod = int(item['Towar']['ID'])
                kod_prod = item['Towar']['Kod']
                ilosc_prod = item['Ilosc']
                if kod_prod not in lista_obce and kod_prod not in lista_anris_bez_sprawdzania and kod_prod not in lista_anris_ZLP:
                    towarID.append(id_prod)
                else:
                    uslugi[kod_prod]= int(ilosc_prod)
                    obiekt_ID[kod_prod] = int(element_id)
                    #dane_uslug[f'{kod_prod}'] = int(ilosc_prod)
            #print(dane_uslug)
            #ceny_uslug(cennik_uslug,dane_uslug,element_id)
            # Sprawdza czy dana usługa kwalifikuje siędo zmiany WD, jeśłi tak to ją zmienia, po zmianie WD przechodzi do następnej FV
            #print(obiekt_ID)
            for kod_uslugi,ilosc in uslugi.items():
                obiekt_id = obiekt_ID[kod_uslugi]
                cena = cena_uslugi(cennik_uslug,kod_uslugi,ilosc)
                if kod_uslugi in lista_obce:
                    zmiana_WD_Obce(id_FV)
                    wpisanie_kosztow_obce(cena,obiekt_id)
                elif kod_uslugi in lista_anris_bez_sprawdzania:
                    zmiana_WD_Anris(id_FV)
                    wpisanie_kosztow_anris(cena,obiekt_id)
                elif kod_uslugi in lista_anris_ZLP:
                    wpisanie_kosztow_anris(cena,obiekt_id)
                    for towar in towarID:
                        #print(towar)
                        # Pobiera info o ZLP z dla danej FV
                        produkty_ZLP=vendoApi.getJson(
                        '/json/reply/Produkcja_Zlecenie_PozycjeLista',
                        {"Token":vendoApi.USER_TOKEN,"Model":{"ZleceniaID":idZLP,'TowarID':towar}})
                        #print(produkty_ZLP)
                        try:
                            produkty_ZLP = produkty_ZLP['Wynik']['Rekordy'][0]
                        except:
                            continue
                        for pole in produkty_ZLP['PolaUzytkownika']:
                            # Anris 'Wykonawca' ID w Vendo 189
                            if pole['NazwaWewnetrzna'] == 'Wykonawca':
                                if pole.get('Wartosc') == '189':
                                    #print('___________ANRIS')
                                    zmiana_WD_Anris(id_FV)
                                else:
                                    pass
                                    #print('************ASGARD')
        else:
            pass
#Zamykanie FV
    print('################################ZAMYKNANIE Faktur')
    for faktura in lista_FV:
        numer_FV = faktura['Numer']
        seria_FV = faktura['Seria'].strip()
        #print(faktura['SpedytorKod'])
        if seria_FV == 'A' and numer_FV == 0:
            id_FV = faktura['ID']
            print(id_FV)
            id_klienta = faktura['Klient1ID']
            #sprawdzanie EURONIP
            if sprawdzanie_EuroNIP(id_klienta):
                pass
            else:
                print('####################################Sprawdź EuroNIP')
            #uwagi do fakturzystek
            czy_uwagi_do_faktury = uwagi_do_fakturzystek(faktura['PolaUzytkownika'])

            if faktura['SpedytorKod'] == 'Odbior własny' or faktura['SpedytorKod'] == 'Brak!!!' or czy_uwagi_do_faktury :
                print('Zostawiam w buforze')
            #ZAMYKANIE dokumentu, automatycznie nadaje sięstatus 'DO WYSŁANIA' żeby automatycznie faktura została wysłana
            elif forma_platnosci(faktura['FormaPlatnosciID']):
                vendoApi.getJson(
                    '/json/reply/Dokumenty_Dokumenty_Zamknij',
                    {"Token":vendoApi.USER_TOKEN,"Model":{
                        "DokumentyID": [
                            id_FV
                        ]}})
                print('Zamykam FV')
            else:
                pass
        else:
            pass

if __name__ == '__main__':
    mainFV()
