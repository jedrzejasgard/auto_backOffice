from webapiVendo import VendoApi
from datetime import datetime, timedelta, date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random


def parse_date(datestring):
    timepart = datestring.split('(')[1].split(')')[0]
    milliseconds = int(timepart[:-5])
    hours = int(timepart[-5:]) / 100
    time = milliseconds / 1000
    dt = datetime.fromtimestamp(time + hours * 3600)
    return dt.strftime("%Y-%m-%d")


def aktywny_euronip_klienta(id_klienta,data):
        #Łączenie z bazą vendo
        vendoApi = VendoApi()
        vendoApi.setApi("http://192.168.115.184:5560") # PRODUKCJA
        vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
        vendoApi.logInApi("esklep","e12345")
        vendoApi.loginUser("jpawlewski", "jp12345")

        #print(rozszerzony_klient['Wynik']['Rekordy'])
        czy_sprawdzone_dzisaj = False
        historia_klienta_euronip = vendoApi.getJson(
            '/json/reply/Plugin_Klienci_HistoriaZapytanOAktywnoscPodatnikaVAT',
            {"Token":vendoApi.USER_TOKEN, "Model":{
            "KlientID": id_klienta }
            })
        for item in historia_klienta_euronip['Wynik']:
            if str(data) == parse_date(item['DataZapytania']):
                czy_sprawdzone_dzisaj = True
        #print(id_klienta,'      ',czy_sprawdzone_dzisaj)
        return czy_sprawdzone_dzisaj

if __name__ == '__main__':
    vendoApi = VendoApi()
    vendoApi.setApi("http://192.168.115.184:5560") # PRODUKCJA
    #vendoApi.setApi("http://192.168.115.184:5575") #BOT
    vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
    vendoApi.logInApi("esklep","e12345")
    vendoApi.loginUser("jpawlewski", "jp12345")

    data = date.today()
    lista_klientow_all = []
    lista_klientow = vendoApi.getJson(
            '/json/reply/CRM_Klienci_Lista',
        {"Token":vendoApi.USER_TOKEN,"Model":{"ZwracanePola": ["DomyslnaEksportowosc"],"Cursor":True,"CursorNazwa":"String","Strona":{"Indeks":0,"LiczbaRekordow":1000}}})
    cursorresp = lista_klientow["Wynik"]["Cursor"]["Nazwa"]
    tys_rekordow = True
    ilosc_sprawdzonych = 1000

    while tys_rekordow:
        lista_klientow = vendoApi.getJson(
            '/json/reply/CRM_Klienci_Lista',
        {"Token":vendoApi.USER_TOKEN,"Model":{"ZwracanePola": ["DomyslnaEksportowosc"],"Cursor":True,"CursorNazwa":cursorresp,"Strona":{"Indeks":ilosc_sprawdzonych,"LiczbaRekordow":ilosc_sprawdzonych+1000}}})
        lista_klientow = lista_klientow['Wynik']['Rekordy']
        for item in lista_klientow:
            lista_klientow_all.append(item)
        if len(lista_klientow) != 1000:
            tys_rekordow = False
        else:
            ilosc_sprawdzonych += 1000

    print(f'Ilość sprawdzonych klientów: {len(lista_klientow_all)}')
    liczba_klientow_unijnych_sprawdzona = 0
    liczba_klientow_unijnych_true=0
    #for klient in lista_klientow_all[::-1]:
    while liczba_klientow_unijnych_sprawdzona < 2001: 
        if liczba_klientow_unijnych_true >= 100:
            print('mam 100 klientow na true')
            break
        elif liczba_klientow_unijnych_sprawdzona >= 2000:
            print('wysylam maila')
            try:
                mail_content = """
                Po sprawdzeniu 2000klientów w bazie czy dzisiaj został sprawdzony EuroNip nie udało się znaleść 100 pozytywnych przypadków
                Sprawdź ręcznie EuroNip zaraz po przeczytaniu tego maila.
                """
                #The mail addresses and password
                sender_address = 'asgard.gadzety@gmail.com'
                sender_pass = 'asgard12345gadzety'
                receiver_address = 'biuro@asgard.gifts'
                #Setup the MIME
                message = MIMEMultipart()
                message['From'] = sender_address
                message['To'] = receiver_address
                message['Subject'] = 'UWAGA Nie sprawdzony EuroNip'
                #The body and the attachments for the mail
                message.attach(MIMEText(mail_content))
                #Create SMTP session for sending the mail
                session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
                session.starttls() #enable security
                session.login(sender_address, sender_pass) #login with mail_id and password
                text = message.as_string()
                session.sendmail(sender_address, receiver_address, text)
                session.quit()
            except:
                print('nie wyslalem maila')
            break
        elif liczba_klientow_unijnych_sprawdzona < 2000:
            if liczba_klientow_unijnych_true < 100:
                klient = lista_klientow_all[random.randint(1,len(lista_klientow_all))]
                if klient['DomyslnaEksportowosc'] == 'Unijna':
                    liczba_klientow_unijnych_sprawdzona+=1
                    print(liczba_klientow_unijnych_sprawdzona)
                    print(klient['ID'])
                    if aktywny_euronip_klienta(klient['ID'],data):
                        liczba_klientow_unijnych_true+=1
        
    print(liczba_klientow_unijnych_true)
