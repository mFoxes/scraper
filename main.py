from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import time
import os
import re
import urllib.parse
import json

loginAndPass = '0403819'

url = None

initialUrl = ""
bookId = ""

viewedUrl = []

indexList = []
indexNum = 0

finalString = []

ua = dict(DesiredCapabilities.CHROME)
options = webdriver.ChromeOptions()
# options.add_argument('headless')
# options.add_argument('window-size=1920x935')
browser = None

temp = 0

folderName = ''

# Utils
def clr():
    # os.system(['clear', 'cls'][os.name == 'nt'])
    pass

def getHtml(finUrl):
    global url
    if finUrl != None:
        browser.get(finUrl)
        # time.sleep(1)
    else:
        url = browser.current_url
    return browser.page_source

def savePage(sectionTitle, pageHtml):
    global indexNum
    if len([i for i in finalString if sectionTitle.get_text(separator=" ")in i]) == 0:
        indexList.append(sectionTitle.get_text(separator=" "))
        finalString.append(f'<div id="index-{indexNum}"><h1>{sectionTitle.get_text(separator=" ")}</h1></div>')

        indexNum += 1

    subTitle = pageHtml.find('h2')
    if subTitle != None:
        indexList.append(subTitle.get_text(separator=" "))
        subTitle['id'] = f'index-{indexNum}'
        indexNum += 1

    finalString.append(pageHtml)

def resetGlobalVariable():
    global indexList
    global finalString
    global indexNum
    global url
    global viewedUrl

    indexNum = 0
    url = None
    indexList = []
    finalString = []
    viewedUrl = []

def writeFile():
    global initialUrl
    global indexList
    global finalString
    with open(f'{bookId}.html', 'wb') as f:
        f.write("<!DOCTYPE html><html><head><meta charset=\"UTF-8\"></head><body>".encode('utf-8'))
        f.write(f'<div><a href="{initialUrl}">Ссылка на книгу</a></div>'.encode('utf-8'))
        f.write(f'<h2>Оглавление</h2>'.encode('utf-8'))
        for idx, line in enumerate(indexList):
            f.write(f'<div><a href="#index-{idx}">{line}</a></div>'.encode('utf-8'))

        for line in finalString:
            f.write(line.encode('utf-8'))
        f.write("</body></html>".encode('utf-8'))

def getNextUrl(url):
    try:
        idString = url.split('/')[-1].split('.')[0]
        newId = int(idString) + 1

        newIdString = ''
        for _ in range(len(idString) - len(str(newId))):
            newIdString += '0'
        newIdString += str(newId)

        newUrl = f'{url.split(idString)[0]}{newIdString}.{url.split("/")[-1].split(".")[1]}'

        return newUrl
    except:
        return viewedUrl[-2]
    


# Rosmedlib
def getTextRosmedlib():
    global url
    res = getHtml(url)
    soup = BeautifulSoup(res, 'lxml')

    sectionTitle = soup.find('div', class_='wrap-quantity-title').find('h1', recursive=True)
    pageHtml = soup.find('div', class_='wrap-content-read')

    if len(soup.findAll(string=re.compile('tab not found'))) > 0:
        if len(viewedUrl) > 2:
            browser.get(viewedUrl[-2])
        print("ЭТОТ САЙТ СДЕЛАЛИ ЕБАНЫЕ АУТИСТЫ, ВВЕДИТЕ ССЫЛКУ НА СЛЕДУЮЩУЮ СТРАНИЦУ")
        if len(indexList) > 1:
            print("Последний заголовок: ", indexList[-1])
        tempUrl = input('Новый url: ')

        url = f'{tempUrl.split("?")[0]}?{url.split("?")[1]}'

        res = getHtml(url)
        soup = BeautifulSoup(res, 'lxml')

        sectionTitle = soup.find('div', class_='wrap-quantity-title').find('h1')
        pageHtml = soup.find('div', class_='wrap-content-read')


    savePage(sectionTitle, pageHtml)

    if soup.find('a', class_='bmark-tab') != None:
        soup.find('a', class_='bmark-tab').decompose()

    nextBtn = soup.find('div', class_='arrow-right-tab').find('a')
    if nextBtn != None:
        url = nextBtn['href']
        viewedUrl.append(url)
    else:
        url = '-1'

def rosmedlibLogin():
    browser.find_element(By.ID, 'user_account').send_keys(loginAndPass)
    time.sleep(1)
    browser.find_element(By.ID, 'check_account').click()
    time.sleep(1)
    browser.find_element(By.ID, 'user_password').send_keys(loginAndPass)
    time.sleep(1)
    browser.find_element(By.ID, 'entry').click()
    time.sleep(1)

def rosmedlibInit():
    global browser
    global url
    global finalString
    global indexNum
    global initialUrl
    global viewedUrl
    try:
        clr()
        print('Текущий сайт: ', initialUrl)
        print('Текущий id: ', bookId)
        print(f'Загрузка...')

        resetGlobalVariable()

        browser = webdriver.Chrome(options)
        browser.get(initialUrl)

        browser.find_element(By.ID, 'guest_login_frame').find_element(By.TAG_NAME, 'a').click()
        time.sleep(1)
        rosmedlibLogin()
        browser.find_element(By.ID, 'a-to_first_chapter').click()
        time.sleep(1)

        while url != '-1':
            getTextRosmedlib()

        clr()
        print('Запись')

    except Exception as _ex:
        print('Ошибка: ', url)
        print(_ex)
    # finally:
        # browser.close()
        # browser.quit()

    writeFile()

    clr()
    print('Загрузка завершена')


# Studentlibrary
def getTextStudentlibrary():
    global browser
    global url
    global indexNum

    pageHtml = getHtml(url)
    # lxml
    soup = BeautifulSoup(pageHtml, 'html.parser')
    content = soup.find('div', class_="r_main-content")

    if content != None:
        sectionTitle = content.find('h1', recursive=True)
        pageHtml = content.find('div', class_='r_main-content_content')

    if len(soup.findAll(string=re.compile('tab not found'))) > 0 or len(soup.findAll('div', id='main_content_404')) > 0:
        if len(viewedUrl) > 2:
            browser.get(viewedUrl[-2])
        print("ЭТОТ САЙТ СДЕЛАЛИ ЕБАНЫЕ АУТИСТЫ, ВВЕДИТЕ ССЫЛКУ НА СЛЕДУЮЩУЮ СТРАНИЦУ")
        if len(indexList) > 1:
            print("Последний заголовок: ", indexList[-1])
        tempUrl = input('Новый url: ')

        url = f'{tempUrl.split("?")[0]}?{url.split("?")[1]}'

        pageHtml = getHtml(url)
        soup = BeautifulSoup(pageHtml, 'lxml')
        content = soup.find('div', class_="r_main-content")

        sectionTitle = content.find('h1')
        pageHtml = content.find('div', class_='r_main-content_content')


    if content.find('div', class_='r_main-content_content').find('a', class_='bmark-tab') != None:
        content.find('div', class_='r_main-content_content').find('a', class_='bmark-tab').decompose()

    savePage(sectionTitle, pageHtml)

    nextBtn = soup.find('div', class_='_to_next-page')
    if nextBtn != None and nextBtn.find('a') != None:
        if nextBtn.find('a')['href'] in viewedUrl:
            url = getNextUrl(url)
        else:
            url = nextBtn.find('a')['href']

        viewedUrl.append(url)
    else:
        url = '-1'

def studentlibraryLogin():
    browser.find_element(By.ID, 'new_UName').send_keys(loginAndPass)
    time.sleep(1)

    browser.find_element(By.ID, 'new_PWord').send_keys(loginAndPass)
    time.sleep(1)

    browser.find_element(By.ID, 'try_UNamePWord').click()
    time.sleep(1)

def studentlibraryInit():
    global browser
    global url
    global initialUrl
    try:
        clr()
        print('Текущий сайт: ', initialUrl)
        print('Текущий id: ', bookId)
        print(f'Загрузка...')

        resetGlobalVariable()

        browser = webdriver.Chrome(options)

        browser.get(initialUrl)

        time.sleep(1)
        browser.find_element(By.ID, 'guest_login_frame').find_element(By.TAG_NAME, 'a').click()
        time.sleep(1)

        studentlibraryLogin()

        browser.find_element(By.ID, 'a-to_first_chapter').click()
        time.sleep(1)

        while url != '-1':
            getTextStudentlibrary()

        clr()
        print('Запись')

    except Exception as _ex:
        print('Ошибка: ', url)
        print(_ex)
    # finally:
        # browser.close()
        # browser.quit()

    writeFile()

    clr()
    print('Загрузка завершена')


# speclit.profy-lib.ru
def getMaxPageNumber():
    global folderName
    body = json.load(open('body.json'))
    cookies = json.load(open('cookies.json'))
    headers = json.load(open('headers.json'))
    params = json.load(open('query.json'))
    cookiesString = ""
    for i in cookies:
        cookiesString += f'{i}={cookies[i]}; '
    headers['Cookie'] = cookiesString
    headers['Referer'] = initialUrl
    
    body['A9912:j_idt11:j_idt23'] = str(int(body['A9912:j_idt11:j_idt23']) + 1)
    body['javax.faces.encodedURL'] = initialUrl
    urlParamsString = ""
    for i in params:
        urlParamsString += f'&{i}={urllib.parse.quote(params[i], safe="")}'

    url = 'https://speclit.profy-lib.ru/book?' + urlParamsString[1::]
    body['javax.faces.encodedURL'] = urllib.parse.quote(url, safe='()&?=')
    bodyRow = ''
    for i in body:
        bodyRow += f'&{urllib.parse.quote(i, safe="()&?=")}={urllib.parse.quote(body[i], safe="()&?=")}'
    resp = requests.post(url, headers=headers, data=bodyRow[1::])

    reg = re.search(r"id=\"A9912:j_idt146\" src=\".*documentId=(.*)&amp;layout=(.*)\" width", resp.text)
    folderName = reg.group(1)
    os.mkdir(folderName)  

    return int(re.search(r"из (.*)<\/label>", resp.text).group(1))

def downloadSpeclitProfylibImg():
    global initialUrl
    global folderName
    bookNumber = 0

    nextGuid = ''

    body = json.load(open('body.json'))

    pageCount = getMaxPageNumber() - 2
    for i in range(pageCount):
        clr()
        print(f'Загрузка...')
        print(i, " из ", pageCount)
        cookies = json.load(open('cookies.json'))
        headers = json.load(open('headers.json'))
        params = json.load(open('query.json'))
        cookiesString = ""
        for i in cookies:
            cookiesString += f'{i}={cookies[i]}; '
        headers['Cookie'] = cookiesString
        headers['Referer'] = initialUrl
        
        body['A9912:j_idt11:j_idt23'] = str(int(body['A9912:j_idt11:j_idt23']) + 1)
        body['javax.faces.encodedURL'] = initialUrl
        urlParamsString = ""
        for i in params:
            urlParamsString += f'&{i}={urllib.parse.quote(params[i], safe="")}'

        url = 'https://speclit.profy-lib.ru/book?' + urlParamsString[1::]
        body['javax.faces.encodedURL'] = urllib.parse.quote(url, safe='()&?=')
        bodyRow = ''
        for i in body:
            bodyRow += f'&{urllib.parse.quote(i, safe="()&?=")}={urllib.parse.quote(body[i], safe="()&?=")}'
        resp = requests.post(url, headers=headers, data=bodyRow[1::])

        reg = re.search(r"id=\"A9912:j_idt146\" src=\".*documentId=(.*)&amp;layout=(.*)\" width", resp.text)
        nextName = reg.group(1)
        nexLayout = reg.group(2)
        imgUrl = "https://speclit.profy-lib.ru/pdf-viewer-portlet/pdfRenderer/?documentId=" + urllib.parse.quote(nextName, safe='()') + "&layout=" + urllib.parse.quote(nexLayout, safe='()')

        cookies['csfcfc'] = nextGuid
        cookiesString = ""
        for i in cookies:
            cookiesString += f'{i}={cookies[i]}; '
        headers['Cookie'] = cookiesString

        headers['Accept'] = "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        del headers['Content-type']
        headers['Sec-Fetch-Dest'] = 'image'
        headers['Sec-Fetch-Mode'] = 'no-cors'

        res = requests.get(imgUrl, headers=headers, stream=True)
        nextGuid = re.search(f"csfcfc=(.*);", resp.headers['Set-Cookie']).group(1)
        if res.status_code == 200:
            with open(f'{folderName}/{bookNumber}.jpg', 'wb') as f:
                f.write(res.content)
                bookNumber += 1


def speclitProfylibInit():
    global initialUrl
    try:

        downloadSpeclitProfylibImg()

    except Exception as _ex:
        print('Ошибка: ', url)
        print(_ex)

    initialUrl = ""

    clr()
    print('Загрузка завершена')
    pass


if __name__ == '__main__':
    while True:
        if initialUrl != '':
            print('Текущий сайт: ', initialUrl)
            print('Текущий id: ', bookId)
        else:
            print('Введите url')

        initialUrl = input('Введите новый url: ')
        if '?SSr' in initialUrl:
            initialUrl = initialUrl.split('?')[0]
        bookId = initialUrl.split('/')[-1].split('.')[0]
        if initialUrl != '':
            clr()
            if 'www.rosmedlib.ru' in initialUrl:
                rosmedlibInit()
            elif 'www.studentlibrary.ru' in initialUrl:
                studentlibraryInit()
            elif 'speclit.profy-lib.ru' in initialUrl:
                speclitProfylibInit()

