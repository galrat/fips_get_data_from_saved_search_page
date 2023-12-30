# 1. get patent numbers from saved htmls in folder
# 2. get data from fips site using list of patent numbers
# 3. save results


import os
import requests
from bs4 import BeautifulSoup
import time
from defs import get_patent_numbers_from_search_pages, get_data_from_soup
import pandas as pd

folder_dir = 'cyclo' # folder with html page
file_address = 'saved_data/cycloid_reductor.txt' # save data here

# 1. get patent numbers from saved htmls in folder

patent_numbers = (get_patent_numbers_from_search_pages(folder_dir))
print('total patents number', len(patent_numbers))
print('patent_numbers', sorted(patent_numbers))
print()
#patent_numbers = ['2610214'] # здесь можно ввести список номеров патентов

#2. get data from fips site using list of patent numbers

header_line = ['app number', 'app url', 'INV/UM', 'filing date', 'patent number', 'patent url', 'title', 'PCT app',
    'PCT publication', 'applicant', 'authors', 'ipc', 'claims', 'status', 'correspondense_address', 'lisence',
    'otch', 'zalog', 'abstract']

# create file if it does not exist or get numbers of already parsed patents
try:
    saved_numbers = []
    saved_data = pd.read_csv(file_address, sep='\t')
    saved_data.columns = header_line
    saved_num = (saved_data['patent number'].loc[1:]).astype(int).values

    # all patent numbers to list
    for num in saved_num:
        saved_numbers.append(str(num).replace(' ', ''))

    # all application numbers to list
    saved_num = (saved_data['app number'].loc[1:]).astype(int).values
    for num in saved_num:
        saved_numbers.append(str(num).replace(' ', ''))
    print('saved_numbers', saved_numbers)
    print('saved_numbers lenght', int(len(saved_numbers)/2))

except:
    print('creating a file for data')
    saved_numbers = []
    with open(file_address, 'a', encoding='utf8') as f:
        f.writelines('\t'.join(header_line) + '\n')

numbers_for_parsing = set(patent_numbers) - set(saved_numbers)
print('\nостаток', numbers_for_parsing)
print('длина остатка', len(numbers_for_parsing))
print()
time.sleep(0)

# get data from fips page
counter = 1
for patent_number in numbers_for_parsing:
    #try:
    print('\n\npatent_number', patent_number)
    time.sleep(3)  # обход защиты на частые запросы
    print('counter', counter, '/', len(numbers_for_parsing))

    if len(patent_number) <= 6 :
        patent_url = 'https://www1.fips.ru//registers-doc-view/fips_servlet?DB=RUPM&DocNumber=' + patent_number
    elif len(patent_number) == 7:
        patent_url = 'https://www1.fips.ru/registers-doc-view/fips_servlet?DB=RUPAT&DocNumber=' + patent_number
    elif len(patent_number) > 7:
        patent_url = 'https://www1.fips.ru/registers-doc-view/fips_servlet?DB=RUPAT&DocNumber=' + patent_number

    print(patent_url)
    try:
        html = requests.get(patent_url)
        soup = BeautifulSoup(html.text, 'lxml')
    except:
        print('smth wrong with url or getting data from url')
    #print(soup.text[:200])
    if 'DDoS-Guard' in soup.text[:200]:
        print('DDoS-Guard!')
        break
    if 'Документ с данным номером отсутствует' in soup.text[:200]:
        print('Документ с данным номером отсутствует\n')
        with open(file_address, 'a', encoding='utf8') as f:
            f.writelines(patent_number + '\tДокумент с данным номером отсутствует\t\t\t' + patent_number +'\n')
        counter += 1
        continue
    if 'Слишком быстрый просмотр' in soup.text[:200]:
        print('Слишком быстрый просмотр')
        time.sleep(4)
        counter += 1
        continue
    data_line = get_data_from_soup(soup, patent_url)

    print(data_line)

    with open(file_address, 'a', encoding='utf8') as f:
        f.writelines('\t'.join(data_line) + '\n')

    #print()
    #except:
        #print('smth wong with', patent_number)
        #wrong = 1
    counter += 1
print('finish!\n=======================================')