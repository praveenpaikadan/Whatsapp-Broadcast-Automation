"""
    Project Name : WhatsApp Selenium Automation
    Author : Praveen Paikadan
    Contact : praveenpaikadan2@gmail.com
    Date of creation : 20-05-2021

    Description : The script automates sending of WhatsApp messages to a or a list of whatsapp registered phone numbers.
    Capabilities:
        1. Checks if the user is logged into WhatsApp Web and prompts to login if not.
        2. Notify timeouts and poor internet.
        3. Send Messages to a list of phone numbers passed as phone_number:Message key:value pairs.
        4. Make sure a message is send within the prescribed time limit.
        5. Returns a summary of the messages send.

    Input : A dictionary of phone_number_string : message_string pairs
    Return value : A dictionary of summary of sending messages OR an Error_string

    For the HP Project :
    This module should be place in the a folder named 'Script_Files' which should be placed in the same ...
    ... directory as that of main.py

    Dependency : requires selenium and its associated requirements (chromedriver.exe)
    imports : selenium, os, datetime, time, logging, urllib

"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from urllib.parse import quote
from datetime import datetime
import time
import getpass

import logging
from selenium.webdriver.remote.remote_connection import LOGGER


LOGGER.setLevel(logging.WARNING)

def log(info, visible=True):            # Prints (and logs)
    info = str(datetime.now())[:-7] + " : " + str(info)
    print(info)


def set_path_variables():               # set paths of different requirements
    user = getpass.getuser()
    user_data_path = "C:\\Users\\" + user + "\\.ChromeDriverUserData"
    if not os.path.exists(user_data_path):
        os.makedirs(user_data_path)

    current_path = os.path.dirname(__file__)
    chrome_driver_path = current_path + "\\chromedriver.exe"
    user_data = user_data_path
    return current_path, chrome_driver_path, user_data


def check_logged_in_what():             # Checks if the use is logged in
    current_path, chrome_driver_path, user_data_path = set_path_variables()

    options = Options()
    options.add_argument("user-data-dir=" + user_data_path)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    options.add_argument('--headless')          # checks without opening browser on screen
    options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--user-agent={}'.format(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'))

    driver = webdriver.Chrome(chrome_driver_path, options=options)
    driver.get("http://web.whatsapp.com")

    start = time.time()

    while True:                     # loop until any conditions are met
        time.sleep(0.3)

        try:
            warn = driver.find_element_by_class_name('_1ENRV')  # check if the retryong ... modal is appearing on page
            driver.find_element_by_class_name('_3xWLK').click() # click retry

        except:
            pass

        try:
            landing_wrapper = driver.find_element_by_class_name('landing-wrapper') # check if qr page is coming
            driver.close()          # confirms not logged in and clos the browser
            return False            # A False return indicates user no logged in
        except:
            pass

        try:
            element_in_logged_in_page = driver.find_element_by_class_name('g5RCg')  # checks for an element in the page
                                                                                    # if user is logged in
            driver.close()
            return True             # A True return indicates user is logged in
        except:
            pass

        try:
            if driver.find_element_by_class_name('_1ENRV').text == "Trying to reach phone":
                driver.find_element_by_class_name('_3xWLK').click()
        except:
            pass

        if time.time() - start > 120:   # TIME OUT Check condition
            driver.close()
            return -1


def login_what():           # Opens Login page
    current_path, chrome_driver_path, user_data_path = set_path_variables()

    options = Options()
    options.add_argument("user-data-dir=" + user_data_path)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    # options.add_argument('--headless')
    options.add_argument("--log-level=3")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--user-agent={}'.format(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'))

    driver = webdriver.Chrome(chrome_driver_path, options=options)
    driver.get("http://web.whatsapp.com")

    start = time.time()
    while True:
        time.sleep(0.3)
        try:
            driver.find_element_by_class_name('g5RCg')  # Check for an element in the logged in page
            break
        except:
            pass
        try:
            if driver.find_element_by_class_name('_1ENRV').text == "Trying to reach phone":
                driver.find_element_by_class_name('_3xWLK').click()
        except:
            pass

        if time.time() - start > 120:
            driver.close()
            return "TIMEOUT"

    driver.close()
    return True


def send_message(phone_number, message, driver):  # Core function to send a single message
    TIME_OUT = 120

    def convert_to_secs(time_string):   # converts the passed time string to match with format in the whatsapp message
        # 2:48 PM
        time_string = time_string.strip()

        def convert_to_24(time_string):
            n = int(time_string[:time_string.find(':')])
            hour = n + 12 if (time_string[-2] == 'P' and time_string.find('12:') == -1) else n
            min = int(time_string[time_string.find(':') + 1:time_string.find(' ')])
            return (hour, min)

        hour, min = convert_to_24(time_string)
        now = datetime.now()
        secs = datetime(now.year, now.month, now.day, hour, min).timestamp()

        return secs

    def check_validity_no():    # Check if a number is registered in whatsapp or not
        TIME_OUT = 120
        start = time.time()
        while True:
            time.sleep(0.3)
            try:  # try finding warning box
                box = driver.find_element_by_class_name('_3NCh_')
                try:
                    if driver.find_element_by_class_name('_1ENRV').text == "Trying to reach phone":
                        driver.find_element_by_class_name('_3xWLK').click()  # click retry
                except:
                    pass
                try:
                    if driver.find_element_by_class_name('_3SRfO').text == "Phone number shared via url is invalid.":
                        return False
                except:
                    pass
            except:
                pass

            try:
                element = driver.find_element_by_class_name('_1-qgF')
                return True
            except:
                pass

            if time.time() - start > TIME_OUT:      # Timeout check
                return "TIMEOUT"

    parsedMessage = quote(message)
    driver.switch_to.window(driver.window_handles[-1])
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get('https://web.whatsapp.com/send?phone=' + phone_number + '&text=' + parsedMessage)

    no_validity = check_validity_no()

    if no_validity == False:
        log("Failed : No WhatsApp available in this number")
        driver.close()
        return False

    elif no_validity == "TIMEOUT":
        log("Failed : Failed to check validity. Whatsapp took too long to respond")
        driver.close()
        return "VALIDITY_CHECK_TIMEOUT"

    else:
        send_xpath = '//*[@id="main"]/footer/div[1]/div[3]/button'

        time.sleep(0.1)
        now = datetime.now()
        now_ = datetime(now.year, now.month, now.day, now.hour, now.minute, 0).timestamp()
        element = WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.XPATH, send_xpath)))
        driver.find_element_by_xpath(send_xpath).click()

        start = time.time()
        while True:
            time.sleep(0.3)
            try:
                last_out_message = driver.find_elements_by_class_name('message-out')[-1]
                send_time = last_out_message.find_elements_by_class_name('_17Osw')[-1].text
                pending_sign = last_out_message.find_elements_by_class_name('_2nWgr')[-1].find_element_by_tag_name('span').get_attribute('aria-label')
            except Exception as err:
                log(err)
                continue

            if convert_to_secs(send_time) >= now_:
                if pending_sign.strip() != "Pending":
                    break

            if time.time() - start > TIME_OUT:
                return "SEND_TIMEOUT"

        time.sleep(0.05)
        driver.close()

        return True


def multi_message(message_dict): # Checks if user is loggen in, loops though send_message funtions to send multiple messages
    # start
    current_path, chrome_driver_path, user_data_path = set_path_variables()

    # Check Logged In
    login_status = check_logged_in_what()

    # Log in if not logged in
    if login_status == "TIMEOUT":
        log("\nError : Not able to verify login status.")
        return "LOGIN_CHECK_TIMEOUT"

    if login_status == False:

        log("\n\nNOTE : Not Logged Into Whatsapp. Login Now ..... ")

        a = True  # on or off switch
        while a:
            login_status = login_what()

            if login_status == True:
                log("Logged in Successfully. ")
                a = True
                while a == True:
                    inp = input("Press 1 to continue Sending Message or 2 to abort: ").strip()
                    if inp == '1':
                        a = False
                        continue
                    elif inp == '2':
                        log("Aborted.")
                        a = False
                        return "ABORTED"
                    else:
                        log("Wrong input.")

            elif login_status == "TIMEOUT":
                log("Login Timeout. Whatsapp takes too much time to respond.")
                b = True
                while b:
                    inp = input("Press 1 to try log in again or 2 to abort : ").strip()
                    if inp == '1':
                        a = True
                        b = False
                        pass
                    elif inp == '2':
                        log("Aborted.")
                        a = False
                        b = False
                    else:
                        log("Wrong input.")

    if login_status == True:
        log("\n\nLogin Status : Logged In")
        options = Options()
        options.add_argument("user-data-dir=" + user_data_path)
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument('--headless')
        options.add_argument("--log-level=3")
        options.add_argument('--disable-gpu')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--user-agent={}'.format(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'))

        driver = webdriver.Chrome(chrome_driver_path, options=options)
        driver.get("http://www.google.com")

        # Making Send status dictionary
        send_status = {}
        for mob_no in message_dict:
            send_status[mob_no] = "NOT_ATTEMPTED"

        for phone_no in message_dict:
            message = message_dict[phone_no]
            truck = message[message.find('Truck Number') + 15: message.find(' (')]
            log('Attempting to send message to ' + phone_no + " (" + truck + ")")

            status = send_message(phone_no, message_dict[phone_no], driver)
            if status == True:
                log("Message send to " + phone_no)
                send_status[phone_no] = "SEND"
            elif status == False:
                log("Message NOT send to " + phone_no + ". Number not registered")
                send_status[phone_no] = "NUMBER_NOT_REGISTERED"
            else:
                log("Message NOT send to " + phone_no + ". " + str(status))
                send_status[phone_no] = status

        time.sleep(3)
        driver.quit()

        return send_status  # send_status, ABORTED, LOGIN_CHECK_TIMEOUT

