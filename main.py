import requests
import csv
from bs4 import BeautifulSoup


CSV = 'cars.csv'
DOMEN = 'https://spb.drom.ru/'
URL = 'volkswagen/polo/'
PARAMS = '?minyear=2018&maxyear=2020&maxprobeg=60000'
HEADERS = {
    'Accept': ('text/html,application/xhtml+xml,'
               + 'application/xml;q=0.9,image/avif,'
               + 'image/webp,image/apng,*/*;q=0.8,'
               + 'application/signed-exchange;v=b3;q=0.9'),
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   + 'AppleWebKit/537.36 (KHTML, like Gecko) '
                   + 'Chrome/109.0.0.0 Safari/537.36')
}


def get_html(url):
    r = requests.get(url, headers=HEADERS)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find(
        'div', class_='css-1nvf6xk').find_all(
            'a', {'data-ftid': 'bulls-list_bull'}
    )
    cars = list()
    for i, item in enumerate(items):
        configurations = dict()
        configurations_names = ['engine', 'fuel',
                                'gearbox', 'drive type', 'mileage']
        configurations_items = item.find(
            'div', class_='css-1fe6w6s e162wx9x0').text.split(',')
        for j in range(len(configurations_items)):
            configurations[configurations_names[j]] = configurations_items[j]
        cars.append(
            {
                'price': item.find(
                            'span', {'data-ftid': 'bull_price'}
                        ).text.replace('\xa0', ' '),
                'link': item.get('href'),
                'title': item.find(
                            'span', {'data-ftid': 'bull_title'}).text
            }
        )
        cars[i].update(configurations)
    return cars


def save_doc(cars, path):
    mean_price = 0
    with open(path, 'w', newline='') as file:
        write = csv.writer(file, delimiter=';')
        write.writerow(
            [
                'Название', 'Цена',
                'Двигатель', 'Тип топлива',
                'Коробка', 'Привод',
                'Пробег', 'Ссылка'
            ]
        )
        for car in cars:
            write.writerow(
                [
                    car['title'], car['price'],
                    car['engine'], car['fuel'],
                    car['gearbox'], car['drive type'],
                    car['mileage'], car['link']
                ]
            )
            mean_price += int(car['price'].replace(' ', ''))
        mean_price //= len(cars)
        write.writerow(['Ср.цена:', mean_price])


def count_pages(html):
    soup = BeautifulSoup(html, 'html.parser')
    count = str(soup.find(
        'div', {'data-ftid': 'component_pagination'}
        ).find_all('div')).count('div')//2
    if count == 0:
        count = 1
    return count


def parse():
    html = get_html(DOMEN+URL+PARAMS)
    if html.status_code == 200:
        cars = list()
        count = count_pages(html.text)
        for page in range(1, count + 1):
            html = get_html(DOMEN+URL+f'page{page}/'+PARAMS)
            cars.extend(get_content(html.text))
        save_doc(cars, CSV)


if __name__ == '__main__':
    parse()
