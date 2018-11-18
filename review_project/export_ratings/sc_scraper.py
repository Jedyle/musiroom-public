import requests
from bs4 import BeautifulSoup

PROTOCOL = "https://"
SENSCRITIQUE_URL = "www.senscritique.com/"

class ParseSCUser:
    def __init__(self, user, protocol = PROTOCOL, url = SENSCRITIQUE_URL):
        self.url = protocol + url + user

    def load(self):
        req = requests.get(self.url)
        if req.status_code == 200:
            page = req.content
            self.soup = BeautifulSoup(page, "html.parser")
        return (req.status_code == 200)

    def get_user_data(self):
        avatar = self.soup.find('img', {'class' : 'uco-cover-avatar'})['src']
        username = self.soup.find('div', {'class' : 'uco-cover-username-container'}).text
        url = self.url
        return {
            'avatar' : avatar,
            'username' : username,
            'url' : url
            }


          
