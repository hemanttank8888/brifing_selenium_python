import csv
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime ,timedelta


current_time = (datetime.now()).strftime("%d_%m_%Y_%H_%M_%S")
today_date = (datetime.now()).strftime("%d-%m-%Y")

PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
symbol_list = pd.read_csv(f"{PROJECT_ROOT_PATH}/input_symbol/symbol.csv")
output_folder_create = os.makedirs(f'{PROJECT_ROOT_PATH}/output_folder/{today_date}', exist_ok=True)
geckodriver_path = os.path.join(PROJECT_ROOT_PATH, "geckodriver.exe")
firefox_binary_path = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
firefox_options = webdriver.FirefoxOptions()
# firefox_options.headless = True
firefox_options.binary_location = firefox_binary_path
firefox_service = webdriver.firefox.service.Service(geckodriver_path)
browser = webdriver.Firefox(service=firefox_service, options=firefox_options)

browser.get('https://www.briefing.com/InPlayEq/Search/ticker.htm?ticker=tsla&page=TICKER&range=60')

username_input = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.NAME, 'username'))
)
username_input.send_keys('manojsaraogi13@gmail.com')

password_input = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.NAME, 'password'))
)
password_input.send_keys('Anurag123')
time.sleep(20)

login_button = WebDriverWait(browser, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
)
login_button.click()
time.sleep(5)
for i in symbol_list["symbol"].values:
    browser.get(f'https://www.briefing.com/InPlayEq/Search/ticker.htm?ticker={i}&page=TICKER&range=60')
    try:
        search = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'SearchTextBox'))
        )
        search.send_keys('tsla')
        login_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@class='vspace2px searchFormPost']"))
        )
        login_button.click()
    except:
        pass
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@id="SearchDate5"]'))).click()
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="dateRangeInput"]/following-sibling::button'))).click()
    time.sleep(5)
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@class="all-comments"]'))).click()
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="Earnings"]/parent::li/input'))).click()
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="News"]/parent::li/input'))).click()
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[@class="buttonPadding"]/button'))).click()
    time.sleep(7)
    datas = []
    twodays_data = []

    def fetch_data():
        while True:
            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            table = soup.find('table', {'id': 'dt1'})

            if table:
                for tr in table.find_all('tr'):
                    row_data = {}
                    
                    try:
                        row_data['symbol_time'] = tr.find('td', class_='timeColumn').find('span', id='ArticleTime').get_text(strip=True)
                    except:
                        continue
                    try:
                        row_data['symbol'] = tr.find('td', class_='tickerColumn').get_text(strip=True)
                    except:
                        continue
                    try:
                        row_data['cell_text'] = tr.find('td', class_='articleColumn').get_text(separator="\n")
                    except:
                        continue

                    if i == row_data['symbol'].lower():
                        datas.append(row_data)
                        given_date = datetime.strptime(row_data['symbol_time'].split(" ")[0], "%d-%b-%y")
                        today_dates = datetime.now()
                        previous_date = today_dates - timedelta(days=1)
                        if given_date.date() == today_dates.date() or given_date.date() == previous_date.date():
                            twodays_data.append(row_data)


            try:
                next_page= WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@id="searchNext"][@class="searchNext pagingBtn searchNextOn"]')))
                print(next_page,":::::::::::")
                if next_page:
                    WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@id="searchNext"][@class="searchNext pagingBtn searchNextOn"]'))).click()
                    time.sleep(8)
                    return fetch_data()
            except:
                break

    def write_output(datas):
        with open(f'{PROJECT_ROOT_PATH}/output_folder/{today_date}/{i}_{current_time}.csv', mode='w', encoding="utf-8", newline="") as output_file:
            writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            # Header
            writer.writerow(['symbol_time', 'symbol', 'cell_text', ])

            # Body
            for row in datas:
                writer.writerow(row.values())

    def two_day_write_output(twodays_data):
        with open(f'{PROJECT_ROOT_PATH}/output_folder/{today_date}/two_days_{i}_{current_time}.csv', mode='w', encoding="utf-8", newline="") as output_file:
            writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            # Header
            writer.writerow(['symbol_time', 'symbol', 'cell_text', ])

            # Body
            for row in twodays_data:
                writer.writerow(row.values())

    fetch_data()
    write_output(datas)
    two_day_write_output(twodays_data)
browser.quit()