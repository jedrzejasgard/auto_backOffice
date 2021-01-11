"""
/Dokumenty_Dokumenty_ZafakturujWZ

Fakturuje dokumenty WZ.
Nie ma możliwości zamknięcia wygenerowanej FV.
"""

from . api_config import ApiConnetionConfig



class ZafakturujWZ(ApiConnetionConfig):


    def __init__(self, user_token, api_url):
        super().__init__(api_url)
        self._request_id = ""
        self._dokumenty_zrodlowe = []
    
        self._query = {"Token": user_token, "RequestID": "", "Model": {}}

        self._endpoint = '/json/reply/Dokumenty_Dokumenty_ZafakturujWZ'
        
    def _get_query_model_field(self, model_field):
        return self._query['Model'].get(model_field, None)

    def _set_query_model_field(self, model_field, value):
        self._query['Model'][model_field] = value


    @property
    def query(self):
        return self._query
        
    @property
    def request_id(self):
        return self._get_query_model_field('RequestID')
    
    @request_id.setter
    def request_id(self, value):
        # value must be string
        self._set_query_model_field('RequestID', value)

    @property
    def dokumenty_zrodlowe(self):
        return self._get_query_model_field('DokumentyZrodlowe')

    @dokumenty_zrodlowe.setter
    def dokumenty_zrodlowe(self, value):
        # value must be a list of documents IDs
        self._set_query_model_field('DokumentyZrodlowe', value)
    
    def send_request(self):
        # Returns response from api endpoint
        return self._send_request(self._endpoint, self.query)
