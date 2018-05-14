# import libraries
from  selenium import webdriver
from time import sleep
import urllib3
import bs4
import certifi
from selenium.webdriver import FirefoxProfile

list_of_links = []


class WebScraper:
    def __init__(self):
        self.username = "robertallenneville@gmail.com"
        self.password = ""

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
    #sleep(1)


def enter_login_details (driver, webscraper):
    # find the elements needed to login
    username_box = driver.find_element_by_id('email')
    password_box = driver.find_element_by_id('pass')
    login_button = driver.find_element_by_id('loginbutton')
    #enter the username and passwords and then click the login button
    username_box.send_keys(webscraper.username)
    #pause so it doesn't look automated
    #sleep(2)
    password_box.send_keys(webscraper.password)
    login_button.click()
    sleep(3)


def search (driver, term):
    print("Searching for " + term + ".")
    #find the elements needed to search
    search_box = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/input[2]")
    search_button = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/form[1]/button[1]")
    search_box.send_keys(term)
    search_button.click()
    sleep(1)
    print("Found results for " + term + ".")

#this scrolls to bottom of page to show all of the elements on a page.
def scroll_bottom(driver, name):
    print("Scrolling...")
    #goto container that has reults in it.
    no_of_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div"))
    #scroll down, hoping to trigger more results.
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    sleep(2)
    total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div"))
    while total_items > no_of_items:
        no_of_items = total_items
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        print("Scrolling...")
        sleep(3)
        total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div"))
    items_list = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div")
    print(len(items_list))
    if(len(items_list)>4):
        items_list.pop()
        items_list.pop()
        print(len(items_list))
    print("finished scrolling")
    parse_items(items_list, name)

def parse_items(items_list , name):
    print("Parsing Items in the " + name + " list...")
    list = []
    #for item in items_list:
    #    sleep(1)
    #   single_item = item.find_element_by_xpath(".//a[1]")
    #    #6div1 1div2 3div1 1a1 1span1
    for i in range(len(items_list)):
        if(i==0):
            first_list = items_list[i].find_elements_by_xpath("div")
            list.extend(first_list)
            print("this is item no " + str(i+1) + ". The total size of list is " + str(len(list)))
        elif(i==1):
            second_list=items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div")
            list.extend(second_list)
            print("The second item is this one " + str(i+1) + ". The total size of list is " + str(len(list)))
        else:
            else_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/div/div/div[2]/div/div/div/div[" + str(i+1) + "]/div/div")
            list.extend(else_list)
            print ("we are now on item number " + str(i+1) + ". The total size of list is " + str(len(list)))
    print("Parsing the " + name + " list is finished.")
    get_hrefs(list, name)



def get_hrefs(list, name):
    print ("Size of list of links list is " + str(len(list_of_links)) + ". The length of list from parse_items is " + str(len(list)) + ".")
    for i in range (len(list)):
        sleep(0.05)
        temp = list[i].find_element_by_css_selector('a').get_attribute('href')
        list_of_links.append(temp)
        print(".", end="", flush=True)
    print(".")
    print("Finished getting HREFS for " + name + ".")




def open_links(list):
    print(str(len(list_of_links)))
    for i in range (len(list)):
        ffprofile = webdriver.FirefoxProfile();
        ffprofile.set_preference("dom.webnotifications.enabled", False);
        driver = webdriver.Firefox(firefox_profile=ffprofile)
        temp = list[i]
        relogin(driver, web_scraper, temp)


def relogin(driver, web_scraper, temp):
    driver.get(temp)
    email = driver.find_element_by_id('email').send_keys(web_scraper.username)
    pw = driver.find_element_by_id('pass').send_keys(web_scraper.password)
    enter = driver.find_element_by_id('loginbutton').click()
    driver.back()
    driver.find_element_by_partial_link_text('Posts').click()
    scroll_bottom_pages(driver, temp)
    get_posts_lists(driver, temp)
    driver.close()
    print( "Closed: " + temp)


def scroll_bottom_pages(driver, temp):
    print("Scrolling " + temp + "...")
    # goto container that has reults in it.
    #no_of_items = len(driver.find_elements_by_xpath(
    #    "//*[@id='id_5af966633d1507039767674']"))
    # scroll down, hoping to trigger more results.
    for i in range(5):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        sleep(2)


def get_posts_lists(driver, temp):
    print("Getting psots for " + temp)


#u_ps_jsonp_9_3_8 > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(1) > span:nth-child(1)
#/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/     div/div/div/div/div/div[1]/div[2]/div/div/div/a/span
def test(my_web_scraper):
    # Choose wich browser to use
    #action = input('Do you want to use [C]hrome or [F]irefox?').upper()
    #if action not in "CF" or len(action)!=1:
     #   print("You didn't pick [C]hrome or [F]irefox. Give it another go")
     #   test(my_web_scraper)
    # create driver for Chrome
    #if action == 'C':
    #    chrome_options = webdriver.ChromeOptions()
    #    prefs = {"profile.default_content_setting_values.notifications": 2}
    #    chrome_options.add_experimental_option("prefs", prefs)
    #    driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver chosen, open the webpage.
     #   open_webpage(driver)
        # enterlogin details and login
    #    enter_login_details(driver, my_web_scraper)
    #    #search for Maraenui
    #    search(driver)
    # create driver for Firefox
    #elif action == 'F':
    ffprofile = webdriver.FirefoxProfile();
    ffprofile.set_preference("dom.webnotifications.enabled", False);
    driver = webdriver.Firefox(firefox_profile=ffprofile)
    # driver chosen, open the webpage.
    open_webpage(driver)
    # enterlogin details and login
    enter_login_details(driver, my_web_scraper)
    search(driver, "Maraenui")
    driver.find_element_by_partial_link_text("Pages").click()
    scroll_bottom(driver, "Pages")
    #driver.find_element_by_partial_link_text("Places").click()             This and the next line need to do their own xpath
    #scroll_bottom(driver, "Places")                                        /html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/div/div/div[2]/div/div/div/div/div/div/ul/li. a list of li
    #driver.find_element_by_partial_link_text("Groups").click()
    #sleep(10)
    #scroll_bottom(driver, "Groups")
    open_links(list_of_links)







if __name__ == "__main__":
    web_scraper = WebScraper()
   # u_name = input('What is your Facebook username?')
    #p_word = input('What is your Facebook password?')
    # web_scraper.set_username(u_name)
    #web_scraper.set_password(p_word)
    test(web_scraper)
