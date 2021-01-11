"""
Funkcje autoryzacji dostępu do API
"""

from . api_config import ApiConnetionConfig


class AutoryzacjaZaloguj(ApiConnetionConfig):
    """
    Autoryzacja API vendo.
    Loguje usera do api i ustawia token do kolejnych zapytań.

    Konfiguracja jako **kwargs przy inicjalizacji klasy.
    auth_config = {
        'api_url': 'string',
        'api_user': 'string',
        'api_user_pswd': 'string',
        'v_user': 'string',
        'v_user_pswd': 'string'
    }
    """

    def __init__(self, api_url, api_user, api_user_pswd, v_user, v_user_pswd):
        super().__init__(api_url)
        self._user_token = ''
        self.api_user = api_user
        self.api_user_pswd = api_user_pswd
        self.v_user = v_user
        self.v_user_pswd = v_user_pswd

        # sprawdza czy argumenty funkcji są typu string
        # pomija pierwszy argument 'self'
        for arg in self.__init__.__code__.co_varnames[1:]:
            if not isinstance(locals()[arg], str):
                raise TypeError("Elementy konfiguracji muszą być typu string!")
            if arg == '':
                raise TypeError("Elementy nie mogą być puste!")

    @property
    def user_token(self):
        return self._user_token
            


    def _auth_zaloguj_do_api(self):
        endpoint = '/json/reply/Autoryzacja_Zaloguj'
        query = {
            "Model":{
                "Login":self.api_user,
                "Haslo":self.api_user_pswd}
        }
        response = self._send_request(endpoint, query).json() 
        
        # sprawdza czy odpowiedź API zawiera TOKEN
        try:
            return response['Wynik']['Token']
        except KeyError:
            raise AttributeError('Błąd autoryzacji')
        

    def _auth_zaloguj_uzytkownika(self, api_token):       
        endpoint = '/json/reply/Autoryzacja_ZalogujUzytkownikaVendo'
        query = {
            "Token" : api_token,
            "Model":{
                "Login":self.v_user,
                "Haslo":self.v_user_pswd}
        }
        response = self._send_request(endpoint, query).json() 
        
        # sprawdza czy odpowiedź API zawiera TOKEN
        try:
            return response['Wynik']['Token']
        except KeyError:
            raise AttributeError('Błąd autoryzacji')

    def login_to_api(self):
        """
        Wysyła żądanie autoryzacji.
        Dla pozytywnej odpowiedzi ustawia user_token 
        wymagany przy kolejnych zapytaniach.
        """
        self._user_token = self._auth_zaloguj_uzytkownika(self._auth_zaloguj_do_api())
