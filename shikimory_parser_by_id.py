import time
import requests
from bs4 import BeautifulSoup as BS

# Возвращает JSON вида {'chronology': [{'shikimori_id': 1, 'title': 'БЛА БЛА'}, {'shikimori_id': 2, 'title': 'бла бла'}]}
# Если хронология состоит из 1 тайтла, то возвращает "False"
def get_chronology_by_id(anime_id):
    url = "https://shikimori.one/animes/" + str(anime_id) + "/chronology"
    header = {
        "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        "accept-encoding": 'utf-8',
        "accept-language": 'ru,en;q=0.9',
        "cache-control": 'no-cache',
        "dnt": '1',
        "cookie": '_ga=GA1.2.404010728.1639150201; _ym_d=1639150201; _ym_uid=1639150201346825244; '
                  '_gid=GA1.2.722278053.1642100981; _ym_isad=1; related_view=list; '
                  'i1=1642100982x1642156025x1642156038x1642156560x1642156577x1642156789x1642156803x1642156827x1642156988x1642156999x1642157012x1642157030x1642157046x1642157089x1642157169x1642157183x1642159872x1642159889x1642159902x1642159919x1642159958x1642159979x1642159996x1642161072x1642161339; _gat=1; _kawai_session=kgn64SrndycaixFNDzfLFw5mYYQiyn7xCdFHWfHkjquiR30yn4kBt0XiQ6uJxwm5CWupGksOd%2FWwG6i5ptR9umaobg4hepPnEXKMAdvJ%2BtjgCDRMDejyDqkgOREMraRB%2FbMbimW9lWv0fqhs2LahpbRESKffqRyPtHUcuNKx7L%2Fb0frb4yRgJU%2FvEwFclBYxZT9FpBfGuMAhvlk1zyHTOdlZj7GrVRe6fC9BMPHjwbeJed4tfEFpmMF%2F2Afa2HfMD1jEo%2BXWvC1HMI6Cmk9LAnFCebqp%2FPnBANPCQxhGrBmTly8Jfz9GOQKpC0agm2kHd68oIvjiZsWsNrHpJg%3D%3D--cgS%2Bcb8rzN5i%2FmCv--0vvuoEUozacfPpqivyVZlQ%3D%3D',
        "pragma": 'no-cache',
        "sec-ch-ua": '"Chromium";v="94", "Yandex";v="21", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": 'document',
        "sec-fetch-mode": 'navigate',
        "sec-fetch-site": 'same-origin',
        "sec-fetch-user": '?1',
        "upgrade-insecure-requests": '1',
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/94.0.4606.85 YaBrowser/21.11.4.727 Yowser/2.5 Safari/537.36',
    }
    session = requests.Session()
    session.headers = header
    r = session.get(url)
    html = BS(r.text, 'html.parser')
    errors = html.select(".dialog > p")

    # Если страница переехала
    if errors:
        for el in html.select(".dialog > p > a"):
            url = el.attrs.get('href')
            r = session.get(url)
            html = BS(r.text, 'html.parser')
    while str(html).__contains__("Retry later"):
        print(f"Reconnect on {anime_id}...")
        time.sleep(5)
        r = session.get(url)
        html = BS(r.text, 'html.parser')

    anime_data = {"chronology": []}
    # Для каждого элемента хрронологии
    for el in html.select(".block > .b-db_entry-variant-list_item"):
        url = el.select('.info > .name > a')
        anime_type = "[" + el.select('.info > .line > .value > .b-tag')[0].text + "]"
        try:
            year = el.select('.info > .line > .value > .b-tag')[1].text
        except IndexError:
            year = "??? год"
        try:
            # Если тег с классом .name
            title = el.select(".name-ru")[0].text.replace("OVA", "").replace("  ", " ")
        except IndexError:
            title = url[0].text
        id_str = url[0].attrs.get('href').split('/')[4].split('-')[0]
        # на случай, если id как z8841
        try:
            anime_id = int(id_str)
        except ValueError:
            anime_id = int(id_str[1:])
        anime_data['chronology'].append({"shikimori_id": anime_id, "title": f'{title} {anime_type} {year}'})

    # переворачиваем, т.к. на сайте хронология идёт от новых к старым
    if anime_data != {"chronology": []}:
        anime_data['chronology'].reverse()
        return anime_data
    else:
        if str(html).__contains__("Retry later"):
            print(html)
        return False

# Тестовые shikimori_id
# print(get_chronology_by_id(1589))
# print(get_chronology_by_id(8841))
# print(get_chronology_by_id(35847))
