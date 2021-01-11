#-*- coding: utf-8 -*-
import pandas as pd

indexy = {'27712':'50','27717':'1'}
def cennik():
    with open('cennik_anris_obce.xls','rb')as plik_cennik:
        return pd.read_excel(plik_cennik, usecols='A,C,D,E,F,G,H,I')
    #df_cennik = df_cennik.dropna()
    #print(df_cennik)
cennik = cennik()
for row_index,row in cennik.iterrows():
    cena = 0
    for produkt,ilosc in indexy.items():
        
        if int(produkt) == int(row[0]):
            if int(ilosc) <= 49:
                cena = row[1]
            elif int(ilosc) <= 99:
                cena = row[2]
            elif int(ilosc) <= 249:
                cena = row[3]
            elif int(ilosc) <= 499:
                cena = row[4]
            elif int(ilosc) <= 999:
                cena = row[5]
            elif int(ilosc) <= 2499:
                cena = row[6]
            elif int(ilosc) <= 4999:
                cena = row[7]
        else:
            pass
        cena = round(float(cena),2)
