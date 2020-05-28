import requests
import json
from urllib.parse import urlencode  #Python内置的HTTP请求库

class CorpData:
    
    def __init__(self,area):
        self.area=area
        
    def get_wsb(self):
        params = {
            'area': self.area,
            'r':'tax/get-not-declare-tax'
        }
        url = 'http://interface.hfxscw.com/?'+ urlencode(params)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return r.json()
        except:
            return None
