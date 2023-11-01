from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import time
import os
import re

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

def clr():
    os.system(['clear', 'cls'][os.name == 'nt'])

def getHtml(finUrl):
    if finUrl != None:
        browser.get(finUrl)
        # time.sleep(1)

    return browser.page_source

def savePage(sectionTitle, pageHtml):
    global indexNum
    if len([i for i in finalString if sectionTitle.text in i]) == 0:
        indexList.append(sectionTitle.text)
        finalString.append(f'<div id="index-{indexNum}">{sectionTitle}</div>')

        indexNum += 1

    subTitle = pageHtml.find('h2')
    if subTitle != None:
        indexList.append(subTitle.text)
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
    idString = url.split('/')[-1].split('.')[0]
    newId = int(idString) + 1

    newIdString = ''
    for _ in range(len(idString) - len(str(newId))):
        newIdString += '0'
    newIdString += str(newId)

    newUrl = f'{url.split(idString)[0]}{newIdString}.{url.split("/")[-1].split(".")[1]}'

    return newUrl

def getTextRosmedlib():
    global url
    res = getHtml(url)
    soup = BeautifulSoup(res, 'lxml')

    sectionTitle = soup.find('div', class_='wrap-quantity-title').find('h1')
    pageHtml = soup.find('div', class_='wrap-content-read')

    if len(pageHtml.findAll(text=re.compile('tab not found'))) > 0:
        browser.get(viewedUrl[-2])
        print("ЭТОТ САЙТ СДЕЛАЛИ ЕБАНЫЕ АУТИСТЫ, ВВЕДИТЕ ССЫЛКУ НА СЛЕДУЮЩУЮ СТРАНИЦУ")
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
    finally:
        browser.close()
        browser.quit()

    writeFile()

    clr()
    print('Загрузка завершена')


def getTextStudentlibrary():
    global browser
    global url
    global indexNum

    pageHtml = getHtml(url)
    soup = BeautifulSoup(pageHtml, 'lxml')
    content = soup.find('div', class_="r_main-content")

    sectionTitle = content.find('h1')
    pageHtml = content.find('div', class_='r_main-content_content')

    if len(pageHtml.findAll(text=re.compile('tab not found'))) > 0:
        browser.get(viewedUrl[-2])
        print("ЭТОТ САЙТ СДЕЛАЛИ ЕБАНЫЕ АУТИСТЫ, ВВЕДИТЕ ССЫЛКУ НА СЛЕДУЮЩУЮ СТРАНИЦУ")
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
    finally:
        browser.close()
        browser.quit()

    writeFile()

    clr()
    print('Загрузка завершена')


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

