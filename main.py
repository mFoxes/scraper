from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import time
import os

loginAndPass = '0403819'

url = None

initialUrl = ""
bookId = ""

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

def getTextRosmedlib():
    global url
    clr()
    print(f'Загрузка...')
    res = getHtml(url)
    soup = BeautifulSoup(res, 'lxml')

    sectionTitle = soup.find('div', class_='wrap-quantity-title').find('h1')
    pageHtml = soup.find('div', class_='wrap-content-read')

    if not(sectionTitle in finalString):
        finalString.append(sectionTitle)
    finalString.append(pageHtml)

    if soup.find('a', class_='bmark-tab') != None:
        soup.find('a', class_='bmark-tab').decompose()

    nextBtn = soup.find('div', class_='arrow-right-tab').find('a')
    if nextBtn != None:
        url = nextBtn['href']
    else:
        url = '-1'

def rosmedlibInit():
    global browser
    global url
    try:
        browser = webdriver.Chrome(options)
        browser.get(initialUrl)

        browser.find_element(By.ID, 'guest_login_frame').find_element(By.TAG_NAME, 'a').click()
        time.sleep(1)
        browser.find_element(By.ID, 'user_account').send_keys(loginAndPass)
        time.sleep(1)
        browser.find_element(By.ID, 'check_account').click()
        time.sleep(1)
        browser.find_element(By.ID, 'user_password').send_keys(loginAndPass)
        time.sleep(1)
        browser.find_element(By.ID, 'entry').click()
        time.sleep(1)
        browser.find_element(By.ID, 'a-to_first_chapter').click()
        time.sleep(1)

        while url != '-1':
            getTextRosmedlib()

    except Exception as _ex:
        print(_ex)
    # finally:
    #     browser.close()
    #     browser.quit()

    with open(f'{bookId}.html', 'wb') as f:
        f.write("<!DOCTYPE html><html><head><meta charset=\"UTF-8\"></head><body>".encode('utf-8'))
        for line in finalString:
            f.write(line.encode('utf-8'))
        f.write("</body></html>".encode('utf-8'))


def getTextStudentlibrary():
    global browser
    global url
    clr()
    print(f'Загрузка...')
    pageHtml = getHtml(url)
    soup = BeautifulSoup(pageHtml, 'lxml')

    content = soup.find('div', class_="r_main-content")

    sectionTitle = content.find('h1')
    pageHtml = content.find('div', class_='r_main-content_content')

    if content.find('div', class_='r_main-content_content').find('a', class_='bmark-tab') != None:
        content.find('div', class_='r_main-content_content').find('a', class_='bmark-tab').decompose()

    while len(pageHtml.find_all('div', class_='hs317')) > 0:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        pageHtml = content.find('div', class_='r_main-content_content')

    if not(sectionTitle in finalString):
        finalString.append(sectionTitle)
    finalString.append(pageHtml)

    nextBtn = soup.find('div', class_='_to_next-page')
    if nextBtn != None:
        print('url: ', url)
        url = nextBtn.find('a')['href']
    else:
        url = '-1'

def studentlibraryInit():
    global browser
    global url
    try:
        browser = webdriver.Chrome(options)

        browser.get(initialUrl)

        time.sleep(1)
        browser.find_element(By.ID, 'guest_login_frame').find_element(By.TAG_NAME, 'a').click()
        time.sleep(1)

        browser.find_element(By.ID, 'new_UName').send_keys(loginAndPass)
        time.sleep(1)

        browser.find_element(By.ID, 'new_PWord').send_keys(loginAndPass)
        time.sleep(1)

        browser.find_element(By.ID, 'try_UNamePWord').click()
        time.sleep(1)

        browser.find_element(By.ID, 'a-to_first_chapter').click()
        time.sleep(1)


        while url != '-1':
            getTextStudentlibrary()

    except Exception as _ex:
        print(_ex)
    # finally:
        # browser.close()
        # browser.quit()

    with open(f'{bookId}.html', 'wb') as f:
        f.write("<!DOCTYPE html><html><head><meta charset=\"UTF-8\"></head><body>".encode('utf-8'))
        for line in finalString:
            f.write(line.encode('utf-8'))
        f.write("</body></html>".encode('utf-8'))

if __name__ == '__main__':
    inp = -1
    while inp != 0:
        clr()
        if initialUrl != '':
            print('Текущий сайт: ', initialUrl)
            print('Текущий id: ', bookId)
        else:
            print('Введие url')
        print('----------------------------')
        print('1 - Вставить новый url')
        if initialUrl != '':
            print('2 - Старт')
        print('0 - Выход')
        print('----------------------------')
        inp = int(input("Введите действие: "))

        if inp == 1:
            clr()
            print('Текущий сайт: ', initialUrl)
            initialUrl = input('Введите новый url: ')
            bookId = initialUrl.split('/')[-1].split('.')[0]
        elif inp == 2 and initialUrl != '':
            clr()
            if 'www.rosmedlib.ru' in initialUrl:
                rosmedlibInit()
            elif 'www.studentlibrary.ru' in initialUrl:
                studentlibraryInit()
            break
        elif inp == 0:
            break

