from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import warnings
import os
import requests
from bs4 import BeautifulSoup
import datetime
import json
from difflib import SequenceMatcher
from datetime import datetime


PROTOCOL = "https://"
SENSCRITIQUE_URL = "www.senscritique.com/"
COLLECTION_URL = "collection/rating/albums/all/all/all/{}/all/all/list/"
MUSICBRAINZ_URL = "musicbrainz.org/"
SEARCH = "search"
LP_ID = "16"
EP_ID = "17"
SINGLE_ID = "18"
LIVE_ID = "19"
COMPILATION_ID = "21"
OST_ID = "585"


CONFIG = {
    'LP': LP_ID,
    'EP' : EP_ID,
    'Single' : SINGLE_ID,
    'Live' : LIVE_ID,
    'Compilation' : COMPILATION_ID,
    'OST' : OST_ID  
    }


TYPES = {
    LP_ID : "Album",
    EP_ID : "EP",
    SINGLE_ID : "Single",
    LIVE_ID : "Album + Live",
    COMPILATION_ID : "Album + Compilation",
    OST_ID : "Album + Soundtrack"
    }


PATTERNS_TO_REMOVE = [
    '(Live)',
    '(EP)',
    '(Single)',
    '(OST)'
    ]

def remove_type(string):
    res = string
    for pattern in PATTERNS_TO_REMOVE:
        res = res.replace(pattern, '')
    return res.rstrip()

def valid_string(string):
    return string.replace('?', '')


def collection_url(type_id):
    return COLLECTION_URL.format(type_id)

class ParseSCPage:
    def __init__(self, user, type_id, driver):
        self.url = PROTOCOL + SENSCRITIQUE_URL + user + '/' + collection_url(type_id)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.driver = driver


    def load_page(self, page):
        self.driver.get(self.url + "page-{}".format(page))

    def get_page_data(self):
        collection = self.driver.find_elements_by_class_name('elco-collection-item')
        return collection #work on that


class ParseSearch:
    def __init__(self, query, protocol = PROTOCOL, search = SEARCH, url = MUSICBRAINZ_URL):
        self.url = protocol + url + search + "?type=release_group&method=advanced&limit=10" + "&query=" + query

    def load(self):
        req = requests.get(self.url)
        if req.status_code == 200:
            page = req.content
            self.soup = BeautifulSoup(page, "html.parser")
        return (req.status_code == 200)

    def get_results(self):
        try:
            table = self.soup.find('table', {'class', 'tbl'})
            result_list = []
            rows = table.tbody.find_all('tr')
            titles = table.thead.find_all('th')
            album_type_index = 0
            album_index = 0
            artist_index = 0
            for i in range(len(titles)):
                if titles[i].text == 'Release Group':
                    album_index = i
                if titles[i].text == 'Artist':
                    artist_index = i
                if titles[i].text == 'Type' :
                    album_type_index = i
            for row in rows:
                try:
                    cols = row.find_all('td')
                    title = cols[album_index].a.text
                    album_mbid = cols[album_index].a['href'].split('/')[-1]
                    artist = cols[artist_index].text
                    artist_mbid = cols[artist_index].a['href'].split('/')[-1]
                    release_type = cols[album_type_index].getText()
                    result = {
                        'title' : title,
                        'album_mbid' : album_mbid ,
                        'artist' : artist,
                        'artist_mbid' : artist_mbid,
                        'type' : release_type,
                        }
                    result_list.append(result)
                except:
                    pass
            return result_list
        except AttributeError:
            return []


def parse_album_data(element):
    rating = element.find_element_by_css_selector('.elco-collection-rating.user').get_attribute('innerText')
    product_detail = element.find_element_by_class_name('elco-product-detail') 
    album = product_detail.find_element_by_class_name('elco-anchor').get_attribute('innerText')
    try:
        release_year = product_detail.find_element_by_class_name('elco-date').get_attribute('innerText').replace('(', '').replace(')', '')
    except NoSuchElementException:
        release_year = ''
    artists = [ el.get_attribute('innerText') for el in product_detail.find_elements_by_class_name('elco-baseline-a') ]
    return {
        "album" : remove_type(album),
        "artists" : artists,
        "release_year" : release_year,
        "rating" : rating,
        }    


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def search_best_result(album_data, release_type):
    query = valid_string(album_data['album'])
    for artist in album_data['artists']:
        query += ' AND artist:{}'.format(artist)
    search = ParseSearch(query.replace(' ', '+'))
    if search.load():
        results = search.get_results()
        for el in results:
            valid_title = valid_string(el['title'])
            valid_query = valid_string(album_data['album'])
            ratio = similar(valid_title, valid_query)
            if el['type'] == release_type and similar(valid_title, valid_query) > 0.9:
                return el
    return None


def parse_data_for_type(user, type_id, filename, errorfile, driver):
    parser = ParseSCPage(user, type_id, driver)
    parser.load_page(1)
    elements = parser.get_page_data()
    collection = []
    page = 1
    while elements :
        for element in elements:
            album_data = parse_album_data(element)
            best_result = search_best_result(album_data, TYPES[type_id])
            if best_result:
                with open(filename, 'a') as infile:
                    infile.write("{} {}\n".format(best_result['album_mbid'], album_data['rating']))
            else :
                with open(errorfile, 'a') as error:
                    error.write("{}///{}///{}\n".format(album_data['album'], ", ".join(album_data['artists']), album_data['rating'] ))                          
        page+=1
        parser.load_page(page)
        elements = parser.get_page_data()
    return collection


def parse_all_data(user, filename, errorfile, driver, types = [LP_ID, EP_ID, LIVE_ID, COMPILATION_ID, SINGLE_ID, OST_ID]):    
    res = {}
    for type_el in types:
        res[TYPES[type_el]] = parse_data_for_type(user, type_el, filename, errorfile, driver)
    return res, driver


def compute_file(username, config, temp_dir = ""):
    types = []
    for key in config:
        if config[key]:
            try:
                el = CONFIG[key]
                types.append(el)
            except KeyError:
                pass

    filename = temp_dir + username + "success" + str(datetime.now()).replace(' ', '-')
    errorfile = temp_dir + username + "fails" + str(datetime.now()).replace(' ', '-')

    with open(filename, 'w'):
        pass
    with open(errorfile, 'w'):
        pass

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        driver = webdriver.PhantomJS()
    
    export, driver = parse_all_data(username, filename, errorfile, driver = driver, types = types)

    driver.close()
    driver.quit()

    return filename, errorfile
            

# def read_file(file):
#     with open(file, 'r') as infile:
#         for line in infile:
#             print(line.split(' ')[0], int(line.split(' ')[1]))

        
