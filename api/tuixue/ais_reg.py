import sys
import time
import random
import requests
from threading import Lock
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from . import global_var as g
import datetime

wait_timeout = 80
refresh_interval = 30

chrome_options = Options()
chrome_options.add_argument("--headless")

cache = {}

def register(country_code, email, password, node):
    global cache
    lock =  g.value(email + "_lock", Lock())
    lock.acquire()
    # Login
    try:
        c_service = Service("./scripts/chromedriver")
        c_service.command_line_args()
        c_service.start()
#        if len(node) > 0:
#            entry = node
#        else:
#            selenium_list = [x.strip() for x in open("node.txt", "r").readlines()]
#            entry = random.choice(selenium_list)
#        driver = webdriver.Remote(
#            command_executor='http://%s:4444/wd/hub' % entry,
#            desired_capabilities=chrome_options.to_capabilities()
#        )
#        print("Choose Node:", entry)
        driver = webdriver.Chrome(
            './scripts/chromedriver',
            desired_capabilities=chrome_options.to_capabilities()
        )

        if email in cache:
            session, schedule_id, group_id = cache[email]
            new_session = change_region(country_code, session, group_id)
            driver.get("https://ais.usvisa-info.com")
            driver.add_cookie({'name' : '_yatri_session', 'value' : new_session, 'path' : '/', 'domain': 'ais.usvisa-info.com', 'secure': True})
            driver.get("https://ais.usvisa-info.com/%s/niv/groups/%s" % (country_code, group_id))
        else:
            driver.get("https://ais.usvisa-info.com/%s/niv/users/sign_in" % country_code)
            email_box = driver.find_element_by_id("user_email")
            email_box.clear()
            email_box.send_keys(email)
            password_box = driver.find_element_by_id("user_password")
            password_box.clear()
            password_box.send_keys(password)
            driver.execute_script("document.getElementById('policy_confirmed').click()")
            signin_button = driver.find_element_by_name("commit")
            signin_button.click()

        def wait_loading(xpath, option="locate", by=By.XPATH):
            try:
                if option == "locate":
                    element_present = EC.presence_of_element_located((by, xpath))
                elif option == "clickable":
                    element_present = EC.element_to_be_clickable((by, xpath))
                WebDriverWait(driver, wait_timeout).until(element_present)
            except TimeoutException:
                print("Timed out waiting for page to load")
                driver.execute_script("window.scrollTo(0, 1080)")
                driver.save_screenshot("test.png")

        print('Continue')
        # Continue
        continue_button_xpath = "//a[contains(text(), 'Continue')]"
        wait_loading(continue_button_xpath)
        current_url = driver.current_url
        group_id = current_url.split("/")[-1]
        continue_button = driver.find_element_by_xpath(continue_button_xpath)
        continue_button.click()

        print('Choose action')
        # Choose action 
        pay_button_xpath = "//a[contains(text(), 'Reschedule Appointment')]"
        wait_loading(pay_button_xpath)
#        banner = banner.find_element_by_tag_name('h5')
#        banner = driver.find_element_by_xpath(pay_button_xpath)
#        banner = banner.find_element_by_xpath('./child::*')
#        banner = driver.find_element_by_xpath("//h5[contains(text(), 'Reschedule Appointment')]")
        banner = driver.find_elements_by_tag_name('h5')[2]
        banner.click()
        wait_loading(pay_button_xpath, option="clickable")
        pay_button = driver.find_element_by_xpath(pay_button_xpath)
        pay_button.click()

        print('Display calendar')
        # Display calendar
        wait_loading('appointments_consulate_appointment_date', option='clickable', by=By.ID)
        banner = driver.find_element_by_id('appointments_consulate_appointment_date')
        banner.click()

        print('Collect result')
        # Collect result
#        title_xpath = "//h2[contains(text(), 'MRV Fee Details')]"
#        wait_loading(title_xpath)
#        time_table = driver.find_element_by_class_name('for-layout')
        wait_loading('ui-datepicker-group-last', by=By.CLASS_NAME)
        time_table = driver.find_element_by_class_name('ui-datepicker-group-last')
        result = []
        if time_table:
            trs = time_table.find_elements_by_tag_name('tr')
            for tr in trs:
                tds = tr.find_elements_by_tag_name('td')
#                if not len(tds) == 2:
#                    continue
#                place = tds[0].text
#                date_str = tds[1].text
#                s = date_str.split()
#                year, month, day = 0, 0, 0
#                if len(s) >= 3 and s[0] != "No":
#                    day_str, month_str, year_str = s[-3], s[-2].replace(",", ""), s[-1]
#                    year, month, day = int(year_str), g.MONTH[month_str], int(day_str)
                for td in tds:
                    if 'ui-datepicker-unselectable' in td.get_attribute('class').split():
                        continue
                    if len(td.find_elements_by_tag_name('span')) == 0:
                        continue
                    today = datetime.date.today()
                    year = today.year + today.month // 12
                    month = today.month % 12 + 1
                    day = int(td.find_element_by_tag_name('span').text)
                    result.append((year, month, day))
        print(result)

        current_url = driver.current_url
        schedule_id = current_url.split("/")[-2]
        session = driver.get_cookie("_yatri_session")["value"]
        driver.quit()
        c_service.stop()
        if result:
            cache[email] = [session, schedule_id, group_id]
        else:
            del cache[email]
        lock.release()
        print('returning ...')
        return result, session, schedule_id
    except Exception as e:
        if email in cache:
            del cache[email]
        print(str(e))
    lock.release()
    if driver:
        driver.quit()
    if c_service:
        c_service.stop()
    return None, None, None


def change_region(country_code, session, group_id):
    req = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
        "Referer": "https://ais.usvisa-info.com/%s/niv/groups/%s" % (country_code, group_id),
        "Cookie": "_yatri_session=" + session
    }
    r = req.get("https://ais.usvisa-info.com/%s/niv/groups/%s" % (country_code, group_id), headers=headers)
    if r.status_code != 200:
        print("Error")
    session = r.cookies["_yatri_session"]
    return session
