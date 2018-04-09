# import libraries
from  selenium import webdriver
from time import sleep
import urllib3
import bs4
import certifi


class WebScraper:
    def __init__(self):
        self.username = "robertallenneville@gmail.com"
        self.password = "password"

    def set_password(self, password):
        assert isinstance(password, str)
        self.password = password

    def set_username(self, username):
        assert isinstance(username, str)
        self.username = username


def open_webpage(driver):
    # set up the web browser and goto the web page
    driver.get('https://www.facebook.com/')
    print("Opened Facebook")
    # pausing for a second so it doesn't look automated
    sleep(1)


def enter_login_details (driver, webscraper):
    # find the elements needed to login
    username_box = driver.find_element_by_id('email')
    password_box = driver.find_element_by_id('pass')
    login_button = driver.find_element_by_id('loginbutton')
    #enter the username and passwords and then click the login button
    username_box.send_keys(webscraper.username)
    #pause so it doesn't look automated
    sleep(2)
    password_box.send_keys(webscraper.password)
    login_button.click()
    # sleep(60)
    # driver.quit()

def test(my_web_scraper):
    # Choose wich browser to use
    action = input('Do you want to use [C]hrome or [F]irefox?').upper()
    if action not in "CF" or len(action)!=1:
        print("You didn't pick [C]hrome or [F]irefox. Give it another go")
        test(my_web_scraper)
    # create driver for Chrome
    if action == 'C':
        driver = webdriver.Chrome()
        # driver chosen, open the webpage.
        open_webpage(driver)
        # enterlogin details and login
        enter_login_details(driver, my_web_scraper)
    # create driver for Firefox
    elif action == 'F':
        driver = webdriver.Firefox()
        # driver chosen, open the webpage.
        open_webpage(driver)
        # enterlogin details and login
        enter_login_details(driver, my_web_scraper)






if __name__ == "__main__":
    web_scraper = WebScraper()
   # u_name = input('What is your Facebook username?')
    p_word = input('What is your Facebook password?')
    # web_scraper.set_username(u_name)
    web_scraper.set_password(p_word)
    test(web_scraper)
