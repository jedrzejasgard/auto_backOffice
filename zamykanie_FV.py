import json
from webapiVendo import VendoApi

#Łączenie z bazą vendo
vendoApi = VendoApi()
# vendoApi.setApi("http://localhost:5575") BOT
vendoApi.setApi("http://192.168.115.184:5565") # testowe Vendo
vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
vendoApi.logInApi("esklep","e12345")
vendoApi.loginUser("jpawlewski", "jp12345")

# rozszerzony_klient = vendoApi.getJson(
#     '/json/reply/CRM_Klienci_KlientRozszerzony',
#     {"Token":vendoApi.USER_TOKEN,"Model":{"ZwrocPliki":False,"ZwrocLudziKlienta":False,"ZwrocKartyPremiowe":False,"ZwrocWartosciDowolne":False,"ID":9921,"Aktywnosci":["Aktywny"],
#     "ZwracanePola": [
#             "DomyslnaEksportowosc"
#         ]}})
# #print(rozszerzony_klient['Wynik']['Rekordy'])
# print(rozszerzony_klient['Wynik']['Rekordy'][0]['Klient']['DomyslnaEksportowosc'])

# #DomyslnaEksportowosc == 'Unijna' 
# #EuroNIP sprawdzony danego dnia oraz "Poprawny" , 
# # WD DomyslnaEksportowosc == Kraj nie ma żadnego dodatkowego warunku, a przy WD DomyslnaEksportowosc == 'Unijna'  musi być WD Weryfikacja : Pozytywny, jeśli jest Niepoprawny DFV musi zostać w buforze

# #numer ZO pełny 10151/A/20/ZO

dok_ZO = vendoApi.getJson(
    '/json/reply/Dokumenty_Dokumenty_Lista',{"Token":vendoApi.USER_TOKEN,"Model":{'NumerPelny':'13909/A/20/FV',"Rodzaj":{"Kod": "FV"}}})
dok_ZO = dok_ZO['Wynik']['Rekordy'][0]
print(dok_ZO['FormaPlatnosciID'])

# zamykanie_dok = vendoApi.getJson(
#     '/json/reply/Dokumenty_Dokumenty_Zamknij',
#     {"Token":vendoApi.USER_TOKEN,"Model":{
#         "DokumentyID": [
#             1274353
#         ]}})
# #print(rozszerzony_klient['Wynik']['Rekordy'])
# print(zamykanie_dok)
