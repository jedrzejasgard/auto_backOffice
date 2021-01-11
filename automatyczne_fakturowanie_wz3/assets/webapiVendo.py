#! python
#-*- coding: utf-8 -*-

import requests
import json
import sys

class VendoApi:

    def setApi(self,api_url):
        # url api - koniecznie musi być włączona usługa API w vendo
        self.API_URL = api_url

    def setHeader(self, api_header):
        self.API_HEADER = api_header

    def getJson(self,request_url, request_data):
        req_url = self.API_URL + request_url
        json_data = requests.post(req_url, json=request_data, headers=self.API_HEADER)
        return json_data.json()

    def logInApi(self, api_login, api_pswd):
        jsonData = self.getJson(
            "/json/reply/Autoryzacja_Zaloguj",
            {"Model":{"Login":api_login,"Haslo":api_pswd}})
        self.VENDO_TOKEN = jsonData["Wynik"]["Token"]

    def logOutApi(self):
        jsonData = self.getJson(
            "/json/reply/Autoryzacja_Wyloguj",
            {"Token":self.VENDO_TOKEN})
        
    def loginUser(self,user_login, user_pswd):
        jsonData = self.getJson(
            "/json/reply/Autoryzacja_ZalogujUzytkownikaVendo",
            {"Token":self.VENDO_TOKEN,"Model":{"Login":user_login,"Haslo":user_pswd}})
        self.USER_TOKEN = jsonData["Wynik"]["Token"]
    
    def logOutUser(self):
        jsonData = self.getJson(
            "/json/reply/WylogujUzytkownikaVendo",
            {"Token": self.USER_TOKEN})



if __name__ == '__main__':

    vendoApi = VendoApi()
    vendoApi.setApi("http://192.168.115.184:5560")
    vendoApi.setHeader({'Content-Type' : 'application/json', "Content-Length" : "length"})
    vendoApi.logInApi("esklep","e12345")
    vendoApi.loginUser("jpawlewski","jp12345")
    print (vendoApi.USER_TOKEN)
    
    
    vendoApi.logOutApi()
    print (vendoApi.VENDO_TOKEN)