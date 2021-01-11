import json
from webapiVendo import VendoApi
from datetime import datetime, timedelta, date
import pandas as pd
from shutil import copyfile

data = date.today()
dataStart= date.today() - timedelta(days=1)

#Łączenie z bazą vendo
vendoApi = VendoApi()
# vendoApi.setApi("http://localhost:5575") BOT
vendoApi.setApi("http://192.168.115.184:5560") 
vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
vendoApi.logInApi("esklep","e12345")
vendoApi.loginUser("jpawlewski", "jp12345")

# indeksy produktów które przy pojawieniu się na FV muszą zmienić WD Obce -> True:
lista_obce = ["27372","27375","27109","27779","27777","27106","27103","27701","27702","27703","27704","27705","27706","27707","27708","27709","27796"]
# indeksy produktów które przy pojawieniu się na FV muszą zmienić WD Anris -> True:
lista_anris = ["27185","27186","27187","27180","27181","27182","27183","27184",'27043','27037','27044','27038','27371','27402','27403','27400','27401','27404','27006','27046','27007','27008','27009','27010','27047','27014','27039','27718','27040','27041','27719','27720','27721','27042','27784','27785','27786','27887','27383','27384','27385','27386','27387','27388','27389','27390','27710','27711','27712','27713','27714','27715','27716','27717','27405','27406','27407','27408','27409','27410','27411','27412','27413','27414','27415','27416','27417','27418','27419','27420','27788','27789','27790','27791','27792','27793','27794','27795','27012','27050']
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

# 
def uwagi_do_fakturzystek(WDfaktury):
    '''
    Sprawdza czy są komentarze do fakturzystek na WZ
    '''
    for item in WDfaktury:
        if item['NazwaWewnetrzna'] == 'uwagi_do_fakturzystek_FV':
            if item.get('Wartosc'):
                return True
            else:
                return False

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


def forma_platnosci(id):
    mozna_zamknac = [2,13,6,10]
    if id in mozna_zamknac:
        return True
    else:
        return False


def cennik():
    '''
    wczytanie cen Obce/Anris z pliku exel przygotowanego przez BO
    '''
    with open('cennik_anris_obce.xls','rb')as plik_cennik:
        return pd.read_excel(plik_cennik, usecols='A,D,E,F,G,H,I,J,K,L,M,N')


def cena_uslugi(cennik_uslug,kod_uslugi,ilosc):
    '''
    zwaraca ceny danej usługi sprawdzone na podstawie pliku Excel cennik_anris_obce.xls
    '''
    sublimacja_uslugi = [27402,27403,27400,27401,27404]
    flex_uslugi = [27043,27037,27044,27038,27371]
    kod_uslugi = int(kod_uslugi)
    ilosc = int(ilosc)
    for index_row,row in cennik_uslug.iterrows():
        cena = 0
        if kod_uslugi in sublimacja_uslugi:
            if ilosc <= 9:
                cena = row[1]
            elif ilosc >= 10 and ilosc <= 19:
                cena = row [10]
            elif ilosc >= 20 and ilosc <= 49:
                cena = row [11]
            elif ilosc >= 50 and ilosc <= 99:
                cena = row[2]
            elif ilosc >= 100 and ilosc <= 249:
                cena = row[3]
            elif ilosc >= 250 and ilosc <= 499:
                cena = row[4]
            elif ilosc >= 500 and ilosc <= 999:
                cena = row[5]
            elif ilosc >= 1000 and ilosc <= 9999:
                cena = row[6]
        if kod_uslugi in flex_uslugi:
            if ilosc <= 49:
                cena = row[1]
            elif ilosc >= 50 and ilosc <= 99:
                cena = row[2]
            elif ilosc >= 100 and ilosc <= 299:
                cena = row[3]
            elif ilosc >= 300 and ilosc <= 499:
                cena = row[4]
            elif ilosc >= 500 and ilosc <= 999:
                cena = row[5]
            elif ilosc >= 1000 and ilosc <= 2999:
                cena = row[6]
            elif ilosc >= 3000 and ilosc <= 4999:
                cena = row[7]
            elif ilosc > 5000:
                cena = row[8]
        if kod_uslugi == int(row[0]):
            if ilosc <= 49:
                cena = row[1]
            elif ilosc >= 50 and ilosc <= 99:
                cena = row[2]
            elif ilosc >= 100 and ilosc <= 249:
                cena = row[3]
            elif ilosc >= 250 and ilosc <= 499:
                cena = row[4]
            elif ilosc >= 500 and ilosc <= 999:
                cena = row[5]
            elif ilosc >= 1000 and ilosc <= 2499:
                cena = row[6]
            elif ilosc >= 2500 and ilosc <= 4999:
                cena = row[7]
            elif ilosc >= 5000:
                cena = row[9]
        else:
            continue
        return round(float(cena),2)


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


def pobierz_liste_FV():
    lista_FV=vendoApi.getJson(
            '/json/reply/Dokumenty_Dokumenty_Lista',
            {"Token":vendoApi.USER_TOKEN,"Model":{
            "Rodzaj": {
                "Kod": "FV",
                'Seria':'   A'},
            "Zamkniete": False,
            }
        })
    lista_FV = lista_FV['Wynik']['Rekordy']
    return(lista_FV)
    
    
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
    return(lista_FV_all)
    
    
def dodanie_kosztow():
    '''
    Raz dziennie wieczorem skrypt do wszystkich zamkniętych faktur z danego dnia dopisuje koszty Anris oraz zaznacza wartość gdzie dodatkowe 
    koszty powstały('Anris'-wpisuje automatycznie/'Obce'-faktórzystka musi wpisać ręcznie)
    '''
    src = r'V:\\10 SPRZEDAŻ (Arek Urbaniak)\\01 BACK OFFICE (Magda Wojciechowska)\\09. Projekt automatyzacja faktur\\cennik_anris_obce.xls'
    dst = r'C:\\auto_wyst_wz_zam_fvcennik_anris_obce.xls'
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
                if czy_Asgard(item):
                    continue
                elif czy_Anris(item):
                    if kod_prod in lista_anris:
                        zmiana_WD_Anris(id_FV)
                        cena = cena_uslugi(cennik_uslug,kod_prod,ilosc_prod)
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
    
    
def mainFV():
    lista_FV = pobierz_liste_FV()
    
    for faktura in lista_FV:
        '''
        Skrypt sprawdza FV z numerem 0 wystawiona z WZek i zamyka te które spełniają poniższe zależności:
        -nie ma uwag do faktórzystek
        -FV ma wyznaczonego spedytora oraz NIE jest do odbioru własnego
        -forma płatności pozwala na zamknięcie
        '''
        numer_FV = faktura['Numer']
        seria_FV = faktura['Seria'].strip()
        data_wystawienia = parse_date(faktura['Data2'])
        if seria_FV == 'A' or seria_FV == 'PROMO' and numer_FV == 0 :
            id_FV = faktura['ID']
            czy_uwagi_do_faktury = uwagi_do_fakturzystek(faktura['PolaUzytkownika'])
            if faktura['SpedytorKod'] == 'Odbior własny' or faktura['SpedytorKod'] == 'Brak!!!' or czy_uwagi_do_faktury :
                continue
            #ZAMYKANIE dokumentu, automatycznie nadaje sięstatus 'DO WYSŁANIA' po którym notify wysyła FV
            elif forma_platnosci(faktura['FormaPlatnosciID']):
                vendoApi.getJson(
                    '/json/reply/Dokumenty_Dokumenty_Zamknij',
                    {"Token":vendoApi.USER_TOKEN,"Model":{
                        "DokumentyID": [
                            id_FV
                        ]}})
            else:
                pass
        else:
            pass

if __name__ == '__main__':
    mainFV()
