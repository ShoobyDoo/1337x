# --------------------------------
# File      : i1337x.py (renamed from py1337x.py)
# Author    : Hemanta Pokharel, Doomlad
# Date      : 07/11/2022
# Info      : Parse a search query via torrent site 1337x.to and its different proxies and
#             prints an array with relevant torrent information to be processed by EZTorrentio.
# --------------------------------
#
# MIT License

# Copyright (c) 2021 Hemanta Pokharel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
from bs4 import BeautifulSoup


class py1337x:
    # Remove requests_cache to fix bug in Pyinstaller executable build
    def __init__(self, proxy=None, cookie=None):
        self.baseUrl = f'https://www.{proxy}' if proxy else 'https://www.1337x.to'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.5',
            'upgrade-insecure-requests': '1',
            'te': 'trailers'
        }

        if cookie:
            self.headers['cookie'] = f'cf_clearance={cookie}'

        self.requests = requests

    #: Searching torrents
    def search(self, query, page=1, category=None, sortBy=None, order='desc'):
        query = '+'.join(query.split())
        category = category.upper() if category and category.lower() in ['xxx', 'tv'] else category.capitalize() if category else None
        url = f"{self.baseUrl}/{'sort-' if sortBy else ''}{'category-' if category else ''}search/{query}/{category+'/' if category else ''}{sortBy.lower()+'/' if sortBy else ''}{order.lower()+'/' if sortBy else ''}{page}/"

        response = self.requests.get(url, headers=self.headers)
        return self.torrentParser(response, baseUrl=self.baseUrl, page=page)

    #: Trending torrents
    def trending(self, category=None, week=False):
        url = f"{self.baseUrl}/trending{'-week' if week and not category else ''}{'/w/'+category.lower()+'/' if week and category else '/d/'+category.lower()+'/' if not week and category else ''}"

        response = self.requests.get(url, headers=self.headers)
        return self.torrentParser(response, baseUrl=self.baseUrl)

    #: Top 100 torrents
    def top(self, category=None):
        category = 'applications' if category and category.lower() == 'apps' else 'television' if category and category.lower() == 'tv' else category.lower() if category else None
        url = f"{self.baseUrl}/top-100{'-'+category if category else ''}"

        response = self.requests.get(url, headers=self.headers)
        return self.torrentParser(response, baseUrl=self.baseUrl)

    #: Popular torrents
    def popular(self, category, week=False):
        url = f"{self.baseUrl}/popular-{category.lower()}{'-week' if week else ''}"

        response = self.requests.get(url, headers=self.headers)
        return self.torrentParser(response, baseUrl=self.baseUrl)

    #: Browse torrents by category type
    def browse(self, category, page=1):
        category = category.upper() if category.lower() in ['xxx', 'tv'] else category.capitalize()
        url = f'{self.baseUrl}/cat/{category}/{page}/'

        response = self.requests.get(url, headers=self.headers)
        return self.torrentParser(response, baseUrl=self.baseUrl, page=page)

    #: Info of torrent
    def info(self, link=None, torrentId=None):
        if not link and not torrentId:
            raise TypeError('Missing 1 required positional argument: link or torrentId')
        elif link and torrentId:
            raise TypeError('Got an unexpected argument: Pass either link or torrentId')

        link = f'{self.baseUrl}/torrent/{torrentId}/h9/' if torrentId else link
        response = self.requests.get(link, headers=self.headers)

        return self.infoParser(response, baseUrl=self.baseUrl)


    # Moved parser(s) to static methods in 1337x class
    @staticmethod
    def torrentParser(response, baseUrl, page=1):
        soup = BeautifulSoup(response.content, 'html.parser')
        
        torrentList = soup.select('a[href*="/torrent/"]')
        seedersList = soup.select('td.coll-2')
        leechersList = soup.select('td.coll-3')
        sizeList = soup.select('td.coll-4')
        timeList = soup.select('td.coll-date')
        uploaderList = soup.select('td.coll-5')

        lastPage = soup.find('div', {'class': 'pagination'})

        if not lastPage:
            pageCount = page
        else:
            try:
                pageCount = int(lastPage.findAll('a')[-1]['href'].split('/')[-2])

            except Exception:
                pageCount = page

        results = {
            'items': [],
            'currentPage': page or 1,
            'itemCount': len(torrentList),
            'pageCount': pageCount
        }

        if torrentList:
            for count, torrent in enumerate(torrentList):
                name = torrent.getText().strip().encode('ascii',errors='ignore').decode('ascii')
                torrentId = torrent['href'].split('/')[2].encode('ascii',errors='ignore').decode('ascii')
                link = baseUrl+torrent['href'].encode('ascii',errors='ignore').decode('ascii')
                seeders = seedersList[count].getText().encode('ascii',errors='ignore').decode('ascii')
                leechers = leechersList[count].getText().encode('ascii',errors='ignore').decode('ascii')
                size = sizeList[count].contents[0].encode('ascii',errors='ignore').decode('ascii')
                time = timeList[count].getText().encode('ascii',errors='ignore').decode('ascii')
                uploader = uploaderList[count].getText().strip().encode('ascii',errors='ignore').decode('ascii')
                uploaderLink = baseUrl+'/'+uploader+'/'.encode('ascii',errors='ignore').decode('ascii')

                results['items'].append({
                    'name': name,
                    'torrentId': torrentId,
                    'link': link,
                    'seeders': seeders,
                    'leechers': leechers,
                    'size': size,
                    'time': time,
                    'uploader': uploader,
                    'uploaderLink': uploaderLink
                })

        return results

    @staticmethod
    def infoParser(response, baseUrl):
        soup = BeautifulSoup(response.content, 'html.parser')

        name = soup.find('div', {'class': 'box-info-heading clearfix'})
        name = name.text.strip().encode('ascii',errors='ignore').decode('ascii') if name else 'N/A'

        shortName = soup.find('div', {'class': 'torrent-detail-info'})
        shortName = shortName.find('h3').getText().strip().encode('ascii',errors='ignore').decode('ascii') if shortName else 'N/A'

        description = soup.find('div', {'class': 'torrent-detail-info'})
        description = description.find('p').getText().strip().encode('ascii',errors='ignore').decode('ascii') if description else 'N/A'

        genre = soup.find('div', {'class': 'torrent-category clearfix'})
        genre = [i.text.strip() for i in genre.find_all('span')] if genre else 'N/A'

        thumbnail = soup.find('div', {'class': 'torrent-image'})
        thumbnail = thumbnail.find('img')['src'] if thumbnail else ''

        if thumbnail and not thumbnail.startswith('http'):
            thumbnail = f'{baseUrl}'+thumbnail

        magnetLink = soup.select('a[href^="magnet"]')
        magnetLink = magnetLink[0]['href'] if magnetLink else 'N/A'

        infoHash = soup.find('div', {'class': 'infohash-box'})
        infoHash = infoHash.find('span').getText() if infoHash else 'N/A'

        images = soup.find('div', {'class': 'tab-pane active'})
        images = [i['src'] for i in images.find_all('img')] if images else 'N/A'

        descriptionList = soup.find_all('ul', {'class': 'list'})

        if len(descriptionList) > 2:
            firstList = descriptionList[1].find_all('li')
            secondList = descriptionList[2].find_all('li')

            category = firstList[0].find('span').getText()
            species = firstList[1].find('span').getText()
            language = firstList[2].find('span').getText()
            size = firstList[3].find('span').getText()
            uploader = firstList[4].find('span').getText()
            uploaderLink = baseUrl+'/'+uploader+'/'

            downloads = secondList[0].find('span').getText()
            lastChecked = secondList[1].find('span').getText()
            uploadDate = secondList[2].find('span').getText()
            seeders = secondList[3].find('span').getText()
            leechers = secondList[4].find('span').getText()

        else:
            category = species = language = size = uploader = uploaderLink = downloads = lastChecked = uploadDate = seeders = leechers = None

        return {
            'name': name,
            'shortName': shortName,
            'description': description,
            'category': category,
            'type': species,
            'genre': genre,
            'language': language,
            'size': size,
            'thumbnail': thumbnail,
            'images': images if images else 'N/A',
            'uploader': uploader.strip(),
            'uploaderLink': uploaderLink,
            'downloads': downloads,
            'lastChecked': lastChecked,
            'uploadDate': uploadDate,
            'seeders': seeders,
            'leechers': leechers,
            'magnetLink': magnetLink,
            'infoHash': infoHash.strip() if infoHash else 'N/A'
        }
