import os
import requests
from bs4 import BeautifulSoup
import time


def fips_patent_data(soup):
    data_line = []

    # title
    title = soup.find('p', id='B542').text.split('(54) ')[1].strip()
    #print(title)

    # patent_number
    patent_number = 'RU' + soup.find_all('td')[1].find('div', id='top4').text.replace(' ', '').strip()
    print(patent_number)
    data_line.append(patent_number)

    # applicant, authors
    applicants = 'no_data'
    authors = 'no_data'
    app_data = soup.find('td', id='bibl').find_all('p')
    for app in app_data:
        if '73' in app.text:
            applicants = app.text.split(':')[1].strip().replace('\t', ' ').replace('\n', ' ')
        if '72' in app.text:
            authors = app.text.split(':')[1].strip().replace('\t', ' ').replace('\n', ' ')
    #print('applicants', applicants)
    #print('authors', authors)

    # filing_date
    filind_data = soup.find('table', id='bib').find_all('tr')[-1].find('td').find('b')
    #print(filind_data.text, '\n!!!!!!!!!!!!\n')
    filind_date = filind_data.text.split(', ')[1]
    #print('filind_date', filind_date)

    # application number
    application_number = soup.find('table', id='bib').text.split('Заявка:')[1].split(',')[0].split('/')[0]
    print('application_number', application_number)

    # publication_date
    publication_date = ''
    pub_data = soup.find('table', id='bib').find_all('p')
    for date in pub_data:
        if '(45)' in date.text:
            #print(date.text.replace('\n', '').replace('\t', ''))
            publication_date = date.text.replace('\n', '').replace('\t', '').split('Опубликовано:')[1].split('Бюл')[0]
    #print('publication_date', publication_date)

    claims_data = soup.find_all('p')
    marker = 0
    for claim in claims_data:
        if marker == 2:
            claims = claim.text.replace('\t', '').replace('\n', '')
            break
        marker = 2 * marker
        if 'Формула изобретения' in claim.text or 'Формула полезной модели' in claim.text:
            marker = 1

    claims_data = soup.find('div', id='main').text
    try:
        claim_1 = claims_data.split('Формула изобретения\n')[1].split('\n2.')[0].replace('\t', '').replace('\n', '').split('2. ')[0]
        #print(claim_1)
    except:
        claim_1 = claims_data.split('Формула полезной модели\n')[1].split('\n2.')[0].replace('\t', '').replace('\n', '').split('2. ')[0]
        #print(claim_1)


    #print('claims', claims)


    # type
    type_data = soup.find('div', id='NameDoc').text
    if 'ИЗОБРЕТ' in type_data:
        type = 'ИЗ'
        #print('IZ')
    else:
        type = 'ПМ'
        #print('UM')

    # ipc
    ipc_data = soup.find('table', class_='tp').text.split('МПК')[1].replace('\n', '')
    #print(ipc_data)

    # status
    status = soup.find('td', id='StatusR').text.replace('\t', '').replace('\n', '')
    #print(status)

    # abstract
    try:
        abstract = soup.find('div', id='Abs').text.replace('\t', '').replace('\n', '')
    except:
        abstract = 'no_data'

    head = ['app number', 'title', 'INV/UM', 'filing date', 'patent number',  'applicant', 'autors',
                        'publiction date', 'ipc', 'claims', 'abstract']

    data_line.append(application_number)
    data_line.append(title)
    data_line.append(type)
    data_line.append(filind_date)
    data_line.append(applicants)
    data_line.append(authors)
    data_line.append(publication_date)
    data_line.append(ipc_data)
    data_line.append(claim_1)
    data_line.append(status)
    data_line.append(abstract)

    return data_line


def get_patent_numbers_from_search_pages(folder_dir):
    '''
    :param folder_dir: directory of html-pages saved from FIPS search results
    :return: unique numbers of patents
    '''

    patent_numbers = []
    for filename in os.listdir(folder_dir):
        #print('filename:', filename)
        try:
            with open(folder_dir + '/' + filename,  'r', encoding='utf8') as f:
                content = f.read()
                #print('content', content)
            soup = BeautifulSoup(content, 'lxml')
            #print(soup.text[:200].strip())
            try:
                lines = (soup.find('div', class_='table').find_all('a', class_='tr'))
                for line in lines:
                    # print(line.text)
                    patent_number = (line.text.split('(')[0].strip().replace('\n', ' ').split('.')[1].strip())
                    # print(patent_number)
                    patent_numbers.append(patent_number.split()[0])
            except:
                print('smth wrong! with getting data from html-file')
            #print('=========================================================')
        except:
            folder = 1
            #print('not_file')

    return list(set(patent_numbers))

def get_data_from_soup(data, url):
    '''
    get all data regarding patent from fips site
    :param data: soup-data from html-page
    :return: line of data: ['app number', 'app url', 'INV/UM', 'filing date', 'patent number', 'patent url', 'title', 'PCT app',
    'PCT publication', 'applicant', 'authors', 'ipc', 'claims', 'status', 'correspondense_address', 'lisence',
    'otch', 'zalog', 'abstract']
    '''

    application_data = []

    # getting app number and app url
    app_url = url
    try:
        app_num = data.find('table', id='bib').text.split('Заявка:')[1].split(',')[0].split('/')[0]
    except:
        app_num = 'no_data'

    # getting type: INV or UM
    type_of_object = data.find('div', id='NameDoc').text
    if 'МОДЕЛ' in type_of_object:
        patent_type = 'ПМ'
        patent_url_first_part = 'https://www1.fips.ru//registers-doc-view/fips_servlet?DB=RUPM&DocNumber='
    else:
        patent_type = 'ИЗ'
        patent_url_first_part = 'https://www1.fips.ru/registers-doc-view/fips_servlet?DB=RUPAT&DocNumber='

    # getting filing date, patent number, patent url, PCT app, PCT publication, applicant, authors
    filing_date = 'no_data'
    patent_number= 'no_data'
    patent_url = 'no_data'
    PCT_num = 'no_data'
    PCT_pub = 'no_data'
    applicant = 'no_data'
    author = 'no_data'

    try:
        patent_number = data.find('div', id='top4').text.strip().replace(' ', '')
    except:
        patent_number = 'no_data'

    try:
        all_data = data.find('table', id='bib').find_all('p')
        for all_dat in all_data:
            if '(21)' in all_dat.text:
                try:
                    filing_date = all_dat.text.strip().split(',')[1]
                    # print('filing_date', filing_date)
                except:
                    filing_date = 'no_data'
                    #print('filing_date error')
            # print(all_dat.text.strip(), '\n\n')
            if 'Заявка PCT:' in all_dat.text:
                PCT_num = all_dat.text.strip().split('PCT:')[1].replace('\t', '').replace('\n', '')
                # print('PCT_num', PCT_num)
            if 'Выдан патент №' in all_dat.text:
                patent_number= all_dat.text.strip().split('№ ')[1].replace(' ', '')
                # print('patent_num', patent_num)
                patent_url = 'https://www1.fips.ru/' + all_dat.find('a')['href']
                # print('patent_url', patent_url)
            if 'Публикация заявки PCT:' in all_dat.text:
                # print(all_dat.text.strip(' \n\t'))
                PCT_pub = all_dat.text.strip(' \n\t').split(':')[1].strip(' \n\t').replace('\t', '').replace('\n', '')
                #print('PCT_pub', PCT_pub)
            if '(71)' in all_dat.text:
                applicant = all_dat.find('b').text.replace('),', '); ').replace(',', '').strip()
                # print('applicant', applicant)
            if '(72)' in all_dat.text:
                author = all_dat.find('b').text.replace('),', '); ').replace(',', '').strip()
                # print('author', author)
    except:
        dates = ''


    # applicant
    try:
        try:
            applicant = data.find('table', id='bib').text.split('Патентообладатель(и):')[1].replace('\n', '').strip()
        except:
            applicant = data.find('table', id='bib').text.split('Заявитель(и):')[1].split('(72) Автор(ы)')[0].strip()
    except:
        applicant = 'no_data'

    # getting IPC data
    ipc = 'no_data'
    try:
        ipcs = data.find('table', class_='tp')  # .find_all('tr')[1]
        ipc = ipcs.text.strip().split('МПК')[1].strip().replace('\t', '').replace('\n', '')
        ipc = ipc.split('(52)')[0].strip()
        ipc = ipc.replace('(2000.01)', '')
        ipc = ipc.replace('(2006.01)', '')
    except:
        ipc = 'no_data'


    # getting claim 1 text
    claim_1 = ''
    try:
        claim_1 = data.find('p', class_='TitCla').find_next_sibling().text.replace('\n', ' ').replace('\t', '')

        #print(claim_1)
        if claim_1 == '':
            claim_1 = 'no_data'
    except:
        claim_1 = 'no_data'
    #print('lenght', len(claim_1))
    if len(claim_1) < 10:
        #print('empty')
        claim_text = ''
        try:
            for i in data.find('p', class_='TitCla').find_next_siblings()[:2]:
                claim_text = claim_text + i.text
            #print(claim_text.strip().replace('\n', ''))
            claim_1 = claim_text.replace('\n', '').strip()
        except:
            claim_1 = 'no_data'
    #print('claim_1', claim_1, '!')


    #print(data.find('p', class_='TitCla').find_next_siblings()[1].text)

    # status
    status = 'no_data'
    try:
        status = data.find('table', class_='Status').find_all('td')[1].text
    except:
        status = 'no_data'


    # address
    try:
        correspondense_address = ''
        adress_data = data.find('table', id='bib').find_all('p')
        for adress in adress_data:
            if 'Адрес для переписки:' in adress.text:
                correspondense_address = adress.text.split('Адрес для переписки:')[1]
        if correspondense_address == '':
            correspondense_address = 'no_data'
    except:
        correspondense_address = ''

    # izveschenie
    izvesch = ''
    otchugd = 0
    licens = 0
    zalog = 0
    try:
        izv_data = data.find('p', class_='StartIzv').find_next_siblings()
        for izv in izv_data:
            # print(izv.text)
            if 'отчужден' in izv.text:
                otchugd += 1
            if 'лиценз' in izv.text:
                licens += 1
            if ' залог' in izv.text:
                zalog += 1
    except:
        otchugd = 0
        licens = 0
        zalog = 0


    # abstract
    abs_par = ''
    try:
        abstract_data = data.find('div', id='Abs').find_all('p')
        for abs in abstract_data:
            abs_par += abs.text
        abstract = abs_par.replace('\n', '').replace('\t', '')
    except:
        abstract = 'no_data'

    try:
        title = data.find('p', id='B542').text.split('(54) ')[1].strip()
    except:
        title = 'no_data'

    application_data.append(app_num)
    application_data.append(app_url)
    application_data.append(patent_type)
    application_data.append(filing_date)
    application_data.append(patent_number)
    application_data.append(patent_url_first_part + patent_number)
    application_data.append(title)
    application_data.append(PCT_num)
    application_data.append(PCT_pub)
    application_data.append(applicant)
    application_data.append(author)
    application_data.append(ipc)
    application_data.append(claim_1)
    application_data.append(status)
    application_data.append(correspondense_address.replace('\n', '').replace('\t', '').strip())
    application_data.append(str(otchugd))
    application_data.append(str(licens))
    application_data.append(str(zalog))
    application_data.append(abstract)

    return application_data
