from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import etree
from pprint import pprint
import os

class Course:

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        user = UserAgent()
        chrome_options.add_argument(f'user-agent={user.random}')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.browser = webdriver.Chrome(os.environ.get('CHROMEDRIVER_PATH'), options=chrome_options) #r'C:\Users\MAMDO\.wdm\drivers\chromedriver\win32\106.0.5249.21\chromedriver.exe'

    def log_in(self, username, password):
        self.browser.get('https://register.nu.edu.eg/PowerCampusSelfService/Registration/Courses')

        #Entere username
        WebDriverWait(self.browser, 5).until(
            EC.element_to_be_clickable(
                (By.ID, 'txtUsername'))
        )
        self.browser.find_element_by_id('txtUsername').send_keys(username)
        self.browser.find_element_by_xpath('//*[@id="btnNext"]').click()

        #Entere Password
        WebDriverWait(self.browser, 5).until(
            EC.element_to_be_clickable(
                (By.ID, 'txtPassword'))
        )
        self.browser.find_element_by_id('txtPassword').send_keys(password)
        self.browser.find_element_by_xpath('//*[@id="btnSignIn"]').click()


    def course_searching(self, course):
        WebDriverWait(self.browser, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="txtSearch"]'))
        )
        element = self.browser.find_element_by_xpath('//*[@id="txtSearch"]')
        # cleaning inputs
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)

        element.send_keys(course)
        element.send_keys(Keys.ENTER)

        WebDriverWait(self.browser, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="contentPage"]/div[2]/div/div/div[1]/div[3]'))
        )

        r = self.browser.page_source
        soup = BeautifulSoup(r, 'html.parser')
        soup_xpath = etree.HTML(str(soup))

        sessions = soup_xpath.xpath('//*[@id="contentPage"]/div[2]/div/div/div[1]/div[3]/div/div/div/div/div[1]/span[1]/text()')
        seats = soup_xpath.xpath('//*[@id="contentPage"]/div[2]/div/div/div[1]/div[3]/div/div/div/div/div[2]/div/div[3]//h4/text()')
        opened = 'Registration period has' in self.browser.page_source

        info = {
            'session': sessions,
            'seats': list(map(int, seats)),
            'opened': False if opened else True
        }

        print(info)

        return info

    def quit(self):
        self.browser.quit()