import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm

KEYWORDS = {'дизайн', 'фото', 'web', 'python'}
my_url = 'https://habr.com/ru/all/'


def stupid_time_processing(datastr):
    """делает время в соответствии с часовым поясам, не нашёл, как сделать проще"""
    time_1 = time.strptime(datastr, "%Y-%m-%dT%H:%MZ")
    res = time.ctime(time.mktime(tuple(time_1)) - time.timezone)
    return res


class article:
    all_articles = list()

    def __init__(self, art):
        self.title = art.find(class_="post__title_link").text.strip()
        self.href = art.find(class_="post__title_link").attrs.get('href')
        self.hubs = {h.text.strip().lower() for h in art.find_all('a', class_="hub-link")}
        self.abstract = art.find('div', class_="post__text").text.strip()
        text_and_date = self.get_full_text_and_post_time()
        self.full_text = text_and_date['text']
        self.data = stupid_time_processing(text_and_date['date'])
        self.all_articles.append(self)
        self.search_res = {'in title': set(), 'in hubs': set(), 'in abstract': set(), 'in full text': set()}

    def __str__(self):
        return f"{self.data} : {self.title} >> {self.href}"

    def get_full_text_and_post_time(self):
        res = {}
        full_ = BeautifulSoup(requests.get(self.href).text, 'html.parser')
        res['text'] = full_.find('div', class_="post__text").text
        res['date'] = full_.find('span', class_="post__time").attrs.get('data-time_published')
        return res

    def search_(self, search_set):
        """сначала поиск по источнику с добавлением результата в атрибут, потом поиск по атрибуту"""
        if isinstance(search_set, str):
            search_set = {search_set}  # если на входе строка

        [self.search_res['in title'].add(s) for s in search_set if s in self.title.lower()]
        [self.search_res['in hubs'].add(s) for s in search_set if s in self.hubs]
        [self.search_res['in abstract'].add(s) for s in search_set if s in self.abstract.lower()]
        [self.search_res['in full text'].add(s) for s in search_set if s in self.full_text.lower()]

        res = set()
        for s in search_set:
            for val in self.search_res.values():
                if s in val:
                    res.add(s)
        return res


def get_articles(url):
    ret = requests.get(url)
    soup = BeautifulSoup(ret.text, 'html.parser')
    articles = soup.find_all('article', class_="post_preview")
    st_bar = tqdm(articles)
    st_bar.desc = 'Scraping'
    a = [article(art) for art in st_bar]
    return a


if __name__ == '__main__':
    arts = get_articles(my_url)
    print(f'Со словами {KEYWORDS} найдены статьи:')
    [print(a) for a in arts if a.search_(KEYWORDS)]
