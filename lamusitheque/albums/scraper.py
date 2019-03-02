import datetime

import requests
from bs4 import BeautifulSoup

PROTOCOL = "https://"
MUSICBRAINZ_URL = "musicbrainz.org/"
COVER_URL = 'coverartarchive.org/'
ARTIST = "artist/"
ALBUM = "release-group/"
SEARCH = "search"

LASTFM_API_KEY = "f92f74bff80870fe482db287a02685c3"
LASTFM_API_URL = "ws.audioscrobbler.com/2.0/"


def valid_year(year):
    if year and year.isdigit():
        if int(year) >= 1000 and int(year) <= 3000:
            return year  # return an integer
    return ""


def get_page_list(nb_pages, current_page):
    page_list = []
    if nb_pages <= 0:
        return page_list
    page_list.append(1)
    page_list.append(nb_pages)
    for i in range(current_page - 1, current_page + 2):
        if 1 < i < nb_pages:
            page_list.append(i)
    page_sorted = sorted(list(set(page_list)))
    page_sorted_with_dots = []
    for i in range(len(page_sorted) - 1):
        page_sorted_with_dots.append(page_sorted[i])
        if page_sorted[i] + 1 < page_sorted[i + 1]:
            page_sorted_with_dots.append('...')
    page_sorted_with_dots.append(page_sorted[-1])
    return page_sorted_with_dots


class ParseSearch:
    def __init__(self, query, search_type, page, protocol=PROTOCOL, search=SEARCH, url=MUSICBRAINZ_URL):
        self.url = protocol + url + search + "?query=" + query + "&type=" + search_type + "&method=indexed" + "&page=" + str(
            page)

    def load(self):
        req = requests.get(self.url)
        if req.status_code == 200:
            page = req.content
            self.soup = BeautifulSoup(page, "html.parser")
        return (req.status_code == 200)

    def get_nb_pages(self):
        try:
            navbar = self.soup.find('ul', {'class': 'pagination'})
            if navbar == None:
                nb_pages = 1
            else:
                links = navbar.find_all('a')
                nb_pages = 0
                for link in links:
                    if link.text.isdigit():
                        nb_pages = max(nb_pages, int(link.text))
            return nb_pages
        except AttributeError:
            return 0


class ParseSearchAlbums(ParseSearch):

    def __init__(self, query, page=1):
        super(ParseSearchAlbums, self).__init__(query, page=page, search_type='release_group')

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
                if titles[i].text == 'Type':
                    album_type_index = i
            for row in rows:
                try:
                    cols = row.find_all('td')
                    title = cols[album_index].text
                    album_mbid = cols[album_index].a['href'].split('/')[-1]
                    artist = cols[artist_index].text
                    artist_mbid = cols[artist_index].a['href'].split('/')[-1]
                    release_type = cols[album_type_index].getText()
                    result = {
                        'title': title,
                        'album_mbid': album_mbid,
                        'artist': artist,
                        'artist_mbid': artist_mbid,
                        'type': release_type,
                    }
                    result_list.append(result)
                except:
                    pass
            return result_list
        except AttributeError:
            return []


class ParseSearchArtists(ParseSearch):

    def __init__(self, query, page=1):
        super(ParseSearchArtists, self).__init__(query, page=page, search_type='artist')

    def get_results(self):
        try:
            table = self.soup.find('table', {'class', 'tbl'})
            result_list = []
            rows = table.tbody.find_all('tr')
            titles = table.thead.find_all('th')
            artist_index = 0
            for i in range(len(titles)):
                if titles[i].text == 'Name':
                    artist_index = i
            for row in rows:
                try:
                    cols = row.find_all('td')
                    name = cols[artist_index].text.strip('\n')
                    mbid = cols[artist_index].a['href'].split('/')[-1]
                    result = {
                        'name': name,
                        'mbid': mbid,
                    }
                    result_list.append(result)
                except:
                    pass
            return result_list
        except AttributeError:
            return []


class ParseArtistPhoto:
    def __init__(self, artist_id, protocol=PROTOCOL, url=LASTFM_API_URL):
        self.artist_id = artist_id
        self.url = protocol + url + "?method=artist.getinfo" + "&api_key=" + LASTFM_API_KEY + "&format=json" + "&mbid=" + self.artist_id

    def load(self):
        req = requests.get(self.url)
        if req.status_code == 200:
            self.json = req.json()
        return (req.status_code == 200)

    def get_thumb(self):
        try:
            images = self.json['artist']['image']
            if images:
                return images[-1]["#text"]
            return ""
        except:
            return ""


class ParseSimilarArtists:
    def __init__(self, artist_id, protocol=PROTOCOL, url=LASTFM_API_URL, limit=6):
        self.artist_id = artist_id
        self.url = protocol + url + "?method=artist.getsimilar" + "&api_key=" + LASTFM_API_KEY + "&format=json" + "&mbid=" + self.artist_id
        self.limit = limit

    def load(self):
        req = requests.get(self.url)
        if req.status_code == 200:
            self.json = req.json()
        return req.status_code == 200

    def get_artists(self):
        artists = self.json['similarartists']['artist']
        res = []
        i = 0
        while (len(res) < min(self.limit, len(artists))) and (i < len(artists)):
            try:
                artist = artists[i]
                name = artist['name']
                mbid = artist['mbid']
                image = artist['image'][-1]["#text"]
                if image != "" and mbid != "" and artist != "":
                    res.append({
                        'name': name,
                        'mbid': mbid,
                        'image': image,
                    })
            except KeyError:
                pass
            i += 1
        return res


class ParseAlbum:
    def __init__(self, album_id, protocol=PROTOCOL, url=MUSICBRAINZ_URL, album_folder=ALBUM):
        self.album_id = album_id
        self.root_url = protocol + url
        self.url = protocol + url + album_folder
        self.track_list = None

    def load(self):
        req = requests.get(self.url + self.album_id)
        if req.status_code == 200:
            page = req.content
            self.soup = BeautifulSoup(page, "html.parser")
        return (req.status_code == 200)

    def get_title(self):
        div = self.soup.find('div', {'class': 'rgheader'})
        return div.a.text

    def get_artists(self):
        links = self.soup.find('p', {'class': 'subheader'}).find_all('a')
        artists = []
        for link in links:
            artist = {
                'name': link.text,
                'mbid': link['href'].split('/')[-1]
            }
            artists.append(artist)
        return artists

    def get_release_date(self):
        table = self.soup.find('table', {'class': 'tbl'})
        dates = []

        for row in table.tbody.find_all('tr')[1:]:
            rows = row.find_all('td')
            try:
                col = row.find_all('td')[3].find_all('li')
                for li in col:
                    r_date = li.text
                    if len(r_date) == 4:
                        r_date = r_date + '-12-31'
                    try:
                        date = datetime.datetime.strptime(r_date, '%Y-%m-%d').date()
                        dates.append(date)
                    except ValueError:
                        pass
            except IndexError:
                pass
        if dates:
            return min(dates)
        else:
            return None

    def get_track_list(self):
        if self.track_list:
            return self.track_list
        else:
            table = self.soup.find('table', {'class': 'tbl'})
            release_1 = table.tbody.find_all('tr')[1:2]
            if release_1:
                release_link = release_1[0].find_all('td')[0].a['href']
                req = requests.get(self.root_url + release_link)
                if req.status_code == 200:
                    page = req.content
                    tracks_soup = BeautifulSoup(page, "html.parser")
                    return self.parse_track_list(tracks_soup)

    def parse_track_list(self, soup):
        tables = soup.find_all('table', {'class': 'tbl'})
        lists = []
        for table in tables:
            try:
                subh = table.tbody.find('tr', {'class': 'subh'}).find_all('th')
                title_index = 0
                duration_index = 0
                for i in range(len(subh)):
                    if subh[i].text == 'Title':
                        title_index = i
                    if subh[i].text == 'Length':
                        duration_index = i

                tracks = table.tbody.find_all('tr')[1:]
                cd = []
                for track in tracks:
                    try:
                        cols = track.find_all('td')
                        title = cols[title_index].a.text
                        cd.append({
                            'title': title,
                            'duration': cols[duration_index].text,
                        })
                    except IndexError:
                        pass
                name = table.find_all('span', {'class': 'medium-name'})
                if name:
                    title = name[0].text
                else:
                    title = ""
                lists.append({
                    'medium_title': title,
                    'tracks': cd,
                })
            except Exception:
                pass
        return {'track_list': lists}

    def get_type(self):
        album_type = self.soup.find('dl', {'class': 'properties'}).find('dd', {'class': 'type'})
        if album_type:
            album_type = album_type.text
            return {
                'Single': 'SI',
                'Album': 'LP',
                'EP': 'EP',
                'Album + Live': 'LI',
                'Album + Compilation': 'CP',
                'Album + Remix': 'RE',
                'Single + Live': 'LI',
                'Album + Compilation + Live': 'LI',
            }.get(album_type, 'UK')
        return "UK"

    def get_tags(self):
        tag_list = self.soup.find('div', {'id': 'sidebar-tags'})
        if tag_list:
            tags = tag_list.find_all('a')
            tag_names = []
            for tag in tags:
                tag_names.append(tag.text)
            return tag_names
        else:
            return []


def merge_identical(discog):
    n = len(discog)
    merged = []
    i = 0
    while (i < n):
        elt = discog[i]
        while (i + 1 < n and discog[i][0] == discog[i + 1][0]):
            elt[1].extend(discog[i + 1][1])
            i = i + 1
        i = i + 1
        merged.append(elt)
    return merged


class ParseCover:
    def __init__(self, album_id, protocol=PROTOCOL, album_folder=ALBUM, url=COVER_URL):
        self.album_id = album_id
        self.url = protocol + url + album_folder

    def load(self):
        req = requests.get(self.url + self.album_id)
        if req.status_code == 200:
            self.cover = req.json()
        return (req.status_code == 200)

    def get_cover_small(self):
        try:
            images = self.cover['images']
            for image in images:
                if image["front"] == True:
                    url = image['thumbnails']['small'].split('/')
                    return url[-2] + '/' + url[-1]
            return ""
        except:
            return ""

    def get_cover_large(self):
        try:
            images = self.cover['images']
            for image in images:
                if image["front"] == True:
                    url = image['thumbnails']['large'].split('/')
                    return url[-2] + '/' + url[-1]
            return ""
        except:
            return ""


class ParseArtist:
    def __init__(self, artist_id, page=1, name="", url=PROTOCOL + MUSICBRAINZ_URL + ARTIST):
        self.artist_id = artist_id
        self.url = url
        self.page = page
        self.name = name

    def load(self):
        req = requests.get(
            self.url + self.artist_id + "?" + "filter.name=" + str(self.name) + "&" + "page=" + str(self.page))
        if req.status_code == 200:
            page = req.content
            self.soup = BeautifulSoup(page, "html.parser")
        return req.status_code == 200

    def get_name(self):
        div = self.soup.find('div', {'class': 'artistheader'})
        return div.h1.a.text

    def get_photo(self):
        photo = self.soup.find("div", {"class": "picture"})
        if photo:
            if photo.img:
                return photo.img['src']
        return ""

    def get_nb_pages(self):
        navbar = self.soup.find('ul', {'class': 'pagination'})
        if navbar == None:
            nb_pages = 1
        else:
            links = navbar.find_all('a')
            nb_pages = 0
            for link in links:
                if link.text.isdigit():
                    nb_pages = max(nb_pages, int(link.text))
        return nb_pages

    def get_discography(self):
        discog = []
        form = self.soup.find('h2', {'class': 'discography'}).find_next_sibling('form')

        if form:
            tables = form.find_all('table')
            for table in tables:
                release_type = table.find_previous_sibling('h3').text
                album_list = []
                rows = table.tbody.find_all('tr')
                for row in rows:
                    try:
                        cols = row.find_all('td')
                        year = valid_year(cols[0].text)
                        title = cols[1].a.text
                        mbid = cols[1].a['href'].split('/')[-1]
                        artists = cols[2].find_all('a')
                        featurings = []
                        for artist in artists:
                            a_mbid = artist['href'].split('/')[-1]
                            if a_mbid != self.artist_id:
                                collab = {
                                    'name': artist.text,
                                    'mbid': a_mbid,
                                }
                                featurings.append(collab)
                        release = {
                            'year': year,
                            'title': title,
                            'mbid': mbid,
                            'feat': featurings
                        }
                        album_list.append(release)
                    except:
                        pass
                discog.append((release_type, album_list))
        return discog


def test_album(album_id):
    album = ParseAlbum(album_id)
    status = album.load()
    if status:
        print(album.get_title())
        print(album.get_artists())
        print(album.get_type())
        print(album.get_release_date())
        print(album.get_track_list())
        print(album.get_tags())
    print('\n\n')


def test_artist(artist_id):
    artist = ParseArtist(artist_id)
    status = artist.load()
    if status:
        print(artist.get_name())
        print(artist.get_photo())
        discog = artist.get_discography()
        for elt in discog:
            print(elt)


def test_cover(album_id):
    cover = ParseCover(album_id)
    if cover.load():
        print(cover.get_cover_small())


def test_search_album(album):
    search = ParseSearchAlbums(album)
    if search.load():
        print('ok')
        print(search.get_results())


def test_search_artist(artist):
    search = ParseSearchArtists(artist)
    if search.load():
        print(search.get_results())


def test_page_list(nb_pages, current_page):
    print('nb_pages : ', nb_pages, 'current_page : ', current_page, 'list : ', get_page_list(nb_pages, current_page))

# test_album('1122eaed-f403-4feb-af98-63a63d3e083a')
# test_album('9c150c9b-769e-4a63-92b3-faf0db3033b0')
# test_album('1bd0767d-756b-3023-bf84-ca475fea487a')
# test_album('3a73b210-aa6e-459d-a9f7-9be3')
# test_album('62db99f0-2629-305c-8c2d-b860b5b99744')
# test_album('aebc4e2f-f900-3ccd-886f-626c2b02eca8')

# test_artist('06fb1c8b-566e-4cb2-985b-b467c90781d4')
# test_artist('d347406f-839d-4423-9a28-188939282afa')

# test_search_album('Mariner')
# test_search_artist('Opeth')

# test_page_list(1,1)
# test_page_list(50, 100)
# test_page_list(100, 50)
# test_page_list(10, 1)
# test_page_list(10,10)
# test_page_list(10,11)
# test_page_list(5,1)
