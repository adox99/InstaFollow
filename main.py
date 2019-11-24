
# made by ado

# simple script, basucally just automates following with instagram
# using the selenium library for instagram (to bypass bot control)
#
# this code is a little outdated but hopefully
# can assist someone, using API endpoints on mobile android devices
# is the easier way to do this same sort of logic..

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from time import sleep
from random import randint
import re
# for threading
import queue
import threading
import time

TARGET_LINKS = [
    'https://www.instagram.com/cristiano/',
    'https://www.instagram.com/selenagomez/',
    'https://www.instagram.com/arianagrande/',
    'https://www.instagram.com/therock/',
    'https://www.instagram.com/kimkardashian/',
    'https://www.instagram.com/beyonce/',
    'https://www.instagram.com/kyliejenner/',
    'https://www.instagram.com/taylorswift/',
]
LOGIN_LINK = 'https://www.instagram.com/accounts/login/?hl=en'

LOW_TIME  = 20
HIGH_TIME = 25

# made for multiple accounts (just add them to the array)
MY_DATABASE = [
    ['username', 'password']
]

# pause function
def p():
    sleep(99999)

# random waiting function
def w(x, y, z=1000):
    sleep((randint(x*z, y*z)/z))

def Login(driver, username=None, password=None, findDelay=5):
    loggedIn = False

    beforeURL = driver.current_url
    u=None
    p=None
    logIn=None

    try:
        u = WebDriverWait(driver, findDelay).until(EC.presence_of_element_located((By.NAME, 'username')))
        p = WebDriverWait(driver, findDelay).until(EC.presence_of_element_located((By.NAME, 'password')))
        logIn = WebDriverWait(driver, findDelay).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Log In')]")))
    except:
        print('Could not log in!')
    else:
        print('Found all log in elements!')
    
    w(1, 2)
    ActionChains(driver).click(u)
    w(0.05, 0.09)
    for x in username:
        ActionChains(driver).send_keys_to_element(u, x).perform()
        w(0.05, 0.09)
    w(1, 2)
    ActionChains(driver).click(p)
    w(0.05, 0.09)
    for x in password:
        ActionChains(driver).send_keys_to_element(p, x).perform()
        w(0.05, 0.09)
    w(1, 2)
    ActionChains(driver).click(logIn).perform()
    w(2, 3)

    cnt = 1
    while cnt < 500:
        if driver.current_url != beforeURL:
            loggedIn = True
            break
        else:
            sleep(0.01)
    
    if loggedIn:
        try:
            notNow = WebDriverWait(driver, findDelay).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Not Now')]")))
            ActionChains(driver).click(notNow).perform()
        except:
            pass
        else:
            pass

    return loggedIn


def createDriver(link=None, isHeadless=False, isFullScreen=True):
    cOptions = Options()
    if isHeadless:
        cOptions.add_argument("--headless")
    if isFullScreen:
        cOptions.add_argument("--start-maximized")
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe", options=cOptions)
    if link == None:
        driver.get(LOGIN_LINK)
    print('Driver was created!')
    
    return driver

# start following accounts
def Start():

    num_worker_threads = 10

    def StartNewThread(acc):
        userName = acc[0]
        passWord = acc[1]
        print('Launching ' + userName + ':' + ('*'*len(passWord)))

        # create and login driver
        driver = createDriver(isHeadless=False)
        if driver == None:
            print(userName + ' failed to boot!')
            return -1
        if Login(driver, username=userName, password=passWord) != True:
            print(userName + ' failed to login!')
            return -1

        print(userName + ' is ready to start!')
        # navigate to new link
        driver.get( TARGET_LINKS[randint(0, len(TARGET_LINKS)-1)] )
        w(1, 2)
        btn = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a')))
        ActionChains(driver).move_to_element(btn).click().perform()
        w(1, 2)

        btn = None
        x = 1
        # always stay one ahead of where we are clicking to ensure that the item has loaded
        ActionChains(driver).send_keys(Keys.TAB).perform()
        for yy in range(1, 5):
                ActionChains(driver).send_keys(Keys.TAB).perform()
                w(0.05, 0.09)
        while True:
            # indent to ensure that the area has loaded
            for zz in range(1, 5):
                ActionChains(driver).send_keys(Keys.TAB).perform()
                w(0.05, 0.09)
            try:
                btn = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[2]/ul/div/li[' + str(x) + ']/div/div[2]/button')))
            except:
                #print('[' + userName + '] item is missing')
                w(7, 8)
            else:
                #print(btn.get_attribute('innerHTML'))
                if btn.get_attribute('innerHTML') == 'Follow':
                    ActionChains(driver).move_to_element(btn).click().perform()
                    w(LOW_TIME, HIGH_TIME)
                else:
                    w(1, 2)
            x += 1
            

        #/html/body/div[3]/div/div[2]/ul/div/li[1]/div/div[2]/button
        #/html/body/div[3]/div/div[2]/ul/div/li[2]/div/div[2]/button

    def worker():
        while True:
            acc = q.get()
            if acc is None:
                break
            StartNewThread(acc)
            q.task_done()

    q = queue.Queue()
    threads = []
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for acc in MY_DATABASE:
        tt = [acc[0], acc[1]]
        q.put(tt)

    # block until all tasks are done
    q.join()

    # stop workers
    for i in range(num_worker_threads):
        q.put(None)
    for t in threads:
        t.join()



def Main():
    print('0) start all ' + str(len(MY_DATABASE)) + ' accounts')
    for x in range(len(MY_DATABASE)):
        print(str(x+1) + ') start ' + MY_DATABASE[x][0])

    uinput = input('$> ' )
    if uinput == '0':
        Start()

if __name__ == "__main__":
    Main()