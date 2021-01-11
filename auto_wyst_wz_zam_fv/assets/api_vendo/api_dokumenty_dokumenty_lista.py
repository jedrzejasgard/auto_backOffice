"""
 /Dokumenty_Dokumenty_Lista
"""

from . api_config import ApiConnetionConfig



class DokumentyDokumentyLista(ApiConnetionConfig):
    """
    Zwraca listę dokumentów
    """

    def __init__(self, user_token, api_url):
        super().__init__(api_url)
        self._query = {'Token': user_token, 'Model': {'Strona': {}}}
        self._endpoint = '/json/reply/Dokumenty_Dokumenty_Lista'
        
    def _get_query_model_field(self, model_field):
        return self._query['Model'].get(model_field, None)

    def _set_query_model_field(self, model_field, value):
        self._query['Model'][model_field] = value

    @property
    def query(self):
        return self._query

    @property
    def dokumenty_lista_id(self):
        return self._get_query_model_field('DokumentyID')

    @dokumenty_lista_id.setter
    def dokumenty_lista_id(self, value):
        self._set_query_model_field('DokumentyID', value)

    @property
    def dokument_id(self):
        return self._get_query_model_field('ID')

    @dokument_id.setter
    def dokument_id(self, dokument_id):
        self._set_query_model_field('ID', dokument_id)

    @property
    def rok(self):
        return self._get_query_model_field('Rok')

    @rok.setter
    def rok(self, rok):
        self._set_query_model_field('Rok', rok)

    @property
    def zamkniety(self):
        return self._get_query_model_field('Zamkniete')

    @zamkniety.setter
    def zamkniety(self, zamkniety):
        self._set_query_model_field('Zamkniete', zamkniety)

    @property
    def rodzaj_kod(self):
        return self.query['Model'].get('Rodzaj', None).get('Kod', None)

    @rodzaj_kod.setter
    def rodzaj_kod(self, kod):
        if self._get_query_model_field('Rodaj'):
            self.query['Model']['Rodzaj']['Kod'] = kod
        else:
            self.query['Model'].update({'Rodzaj': dict()})
            self.query['Model']['Rodzaj']['Kod'] = kod

    @property
    def data_czas_modyfikacji(self):
        return self._get_query_model_field('DataCzasModyfikacji')

    @data_czas_modyfikacji.setter
    def data_czas_modyfikacji(self, data):
        self._set_query_model_field('DataCzasModyfikacji', data)

    @property
    def strona_index(self):
        return self.query['Model']['Strona'].get('Indeks', None)

    @strona_index.setter
    def strona_index(self, indeks):
        self.query['Model']['Strona']['Indeks'] = indeks

    @property
    def strona_liczba_rekordow(self):
        return self.query['Model']['Strona'].get('LiczbaRekordow', None)

    @strona_liczba_rekordow.setter
    def strona_liczba_rekordow(self, liczba_rekordow):
        self.query['Model']['Strona']['LiczbaRekordow'] = liczba_rekordow

    @property
    def aktywny(self):
        return self._get_query_model_field('Aktywne')

    @aktywny.setter
    def aktywny(self, value):
        self._set_query_model_field('Aktywne', value)

    @property
    def sortowanie(self):
        return self._get_query_model_field('Sortowanie')

    @sortowanie.setter
    def sortowanie(self, value):
        self._set_query_model_field('Sortowanie', value)

    @property
    def sortowanie_rosnaco(self):
        return self._get_query_model_field('SortowanieRosnaco')

    @sortowanie_rosnaco.setter
    def sortowanie_rosnaco(self, value):
        self._set_query_model_field('SortowanieRosnaco', value)

    def send_request(self):
        # Returns response from api endpoint
        return self._send_request(self._endpoint, self.query)
