import json
from webapiVendo import VendoApi
from datetime import datetime, timedelta, date
import pandas as pd
from shutil import copyfile

data = date.today()
dataStart= date.today() - timedelta(days=19)

#Łączenie z bazą vendo
vendoApi = VendoApi()
# vendoApi.setApi("http://localhost:5575") BOT
vendoApi.setApi("http://192.168.115.184:5560") 
vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
vendoApi.logInApi("esklep","e12345")
vendoApi.loginUser("jpawlewski", "jp12345")


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


def czy_Asgard(pozycja_FV):
    '''
    Zwraca False jeśli wykonawcą pozycji nie jest Asgard
    '''
    for item in pozycja_FV['PolaUzytkownika']:
        if item['NazwaWewnetrzna']=='Wykonawca':
            if item.get('Wartosc') == '167':
                return True
            else:
                return False

def czy_Anris(pozycja_FV):
    '''
    Zwraca True jeśli wykonawcą pozycji jest Anris
    '''
    for item in pozycja_FV['PolaUzytkownika']:
        if item['NazwaWewnetrzna']=='Wykonawca':
            if item.get('Wartosc') == '189':
                return True
            else:
                return False


def cennik():
    '''
    wczytanie cen Obce/Anris z pliku exel przygotowanego przez BO
    '''
    with open('cennik_anris_obce.xls','rb')as plik_cennik:
        return pd.read_excel(plik_cennik, usecols='A,D,E,F,G,H,I,J,K,L,M,N')


def pobierz_liste_FV_koszty():
    lista_FV_all=[]
    lista_FV=vendoApi.getJson(
            '/json/reply/Dokumenty_Dokumenty_Lista',
            {"Token":vendoApi.USER_TOKEN,"Model":{
            "Rodzaj": {
                "Kod": "FV",},
            "DataOd": str(dataStart),
            "Cursor":True,"CursorNazwa":"String","Strona":{"Indeks":0,"LiczbaRekordow":1}
            }
        })
    cursorresp = lista_FV["Wynik"]["Cursor"]["Nazwa"]
    tys_rekordow = True
    ilosc_sprawdzonych = 0
    while tys_rekordow:
        lista_FV=vendoApi.getJson(
            '/json/reply/Dokumenty_Dokumenty_Lista',
            {"Token":vendoApi.USER_TOKEN,"Model":{
            "Rodzaj": {
                "Kod": "FV",},
            "DataOd": str(dataStart),
            "Cursor":True,"CursorNazwa":cursorresp,"Strona":{"Indeks":ilosc_sprawdzonych,"LiczbaRekordow":1000}
            }
        })
        lista_FV = lista_FV['Wynik']['Rekordy']
        for item in lista_FV:
            lista_FV_all.append(item)
        if len(lista_FV) != 1000:
            tys_rekordow = False
        else:
            ilosc_sprawdzonych += 1000
    #print(lista_FV_all)
    return(lista_FV_all)


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


def dodanie_kosztow():
    '''
    Raz dziennie wieczorem skrypt do wszystkich zamkniętych faktur z danego dnia dopisuje koszty Anris oraz zaznacza wartość gdzie dodatkowe 
    koszty powstały('Anris'-wpisuje automatycznie/'Obce'-faktórzystka musi wpisać ręcznie)
    '''
    src = r'V:\\10 SPRZEDAŻ (Arek Urbaniak)\\01 BACK OFFICE (Magda Wojciechowska)\\09. Projekt automatyzacja faktur\\cennik_anris_obce.xls'
    dst = r'C:\\Users\\asgard_59\\Documents\\Skrypty\\AutomatyzacjaBO\\auto_wyst_wz_zam_fv\\cennik_anris_obce.xls'
    copyfile(src, dst)
    
    cennik_uslug = cennik()
    # indeksy produktów które przy pojawieniu się na FV muszą zmienić WD Obce -> True:
    lista_obce = list(indeksy_wykonawcow()[0])
    # indeksy produktów które przy pojawieniu się na FV muszą zmienić WD Anris -> True:
    lista_anris = list(indeksy_wykonawcow()[1])

    lista_FV = pobierz_liste_FV_koszty()
    for faktura in lista_FV:
        numer_FV = faktura['Numer']
        seria_FV = faktura['Seria'].strip()
        data_wystawienia = parse_date(faktura['Data2'])
        if seria_FV == 'A' or seria_FV == 'PROMO':
            id_FV = faktura['ID']
            for item in faktura['Pozycje']:
                element_id = item['ElementID']
                kod_prod = item['Towar']['Kod']
                ilosc_prod = item['Ilosc']
                #print(kod_prod)
                if czy_Asgard(item):
                    #print('Asgard')
                    continue
                elif czy_Anris(item):
                    if kod_prod in lista_anris:
                        print(numer_FV, 'Anris')
                        zmiana_WD_Anris(id_FV)
                        #cena = cena_uslugi(cennik_uslug,kod_prod,ilosc_prod)
                        #wpisanie_kosztow_anris(cena,element_id)
                elif kod_prod in lista_obce :
                    zmiana_WD_Obce(id_FV)
                else:
                    pass
                        #continue


def indeksy_wykonawcow():
    '''
    Tworzy tuple z dwoma listami zawierającymi indeksy usług przypisane do Anrisu oraz do Obcych
    '''
    with open('cennik_anris_obce.xls','rb')as plik_cennik:
        indeksy_wykonawcy = pd.read_excel(plik_cennik, usecols='A,B')
        lista_anris = []
        lista_obcy = []
        for index_row,row in indeksy_wykonawcy.iterrows():
            if row[1]=='anris':
                lista_anris.append(str(row[0]))
            else:
                lista_obcy.append(str(row[0]))
    return(lista_obcy,lista_anris)

if __name__ == "__main__":
    dodanie_kosztow()