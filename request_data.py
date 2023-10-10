class PostRequest:
    def __init__(self):
        self.headers = {
            'Host': 'ttpu.edupage.org',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://ttpu.edupage.org/',
            'Content-type': 'application/json; charset=utf-8',
            'Origin': 'https://ttpu.edupage.org',
            'Connection': 'keep-alive',
            'Cookie': 'PHPSESSID=9ec281c2b7b4e7bad1c06e23cf32615d',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'DNT': '1',
            'Sec-GPC': '1',
            'TE': 'trailers',
        }
        self.payload = {
            "__args": [None, "170"],
            "__gsh": "00000000"
        }