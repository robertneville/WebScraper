# import libraries
from selenium import webdriver
from time import sleep

list_of_links = []


class WebScraper:
    """This class carries the username and pw of a facebook account. Default is user and pw"""
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
    """Opens facebook"""
    # set up the web browser and goto the web page
    driver.get('https://www.facebook.com/')
    print("Opened Facebook")


def enter_login_details(driver, webscraper):
    """Logs into facebook"""
    # find the elements needed to login
    username_box = driver.find_element_by_id('email')
    password_box = driver.find_element_by_id('pass')
    login_button = driver.find_element_by_id('loginbutton')
    # enter the username and passwords and then click the login button
    username_box.send_keys(webscraper.username)
    password_box.send_keys(webscraper.password)
    login_button.click()
    # pause
    sleep(3)


def search(driver, term):
    """Search for a town or city"""
    print("Searching for " + term + ".")
    # find the elements needed to search
    search_box = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]" +
                                              "/div[2]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/input[2]")
    search_button = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]" +
                                                 "/div[1]/div[2]/div[1]/form[1]/button[1]")
    # enter the search term and click the button and pause
    search_box.send_keys(term)
    search_button.click()
    sleep(1)
    print("Found results for " + term + ".")


def scroll_bottom(driver, name):
    """this scrolls to bottom of page to show all of the elements on a page."""
    print("Scrolling...")
    # goto container that has reults in it. Count the divs inside.
    no_of_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                    "div[1]/div[2]/div[1]/div[1]/div[1]/div"))
    # scroll down, hoping to trigger more results. Pause to give time to load those results
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    sleep(2)
    # Count divs again.
    total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                    "div[1]/div[2]/div[1]/div[1]/div[1]/div"))
    # If total_items > no_of_items then more divs were loaded. Scroll again. If not, bottom was reached.
    while total_items > no_of_items:
        no_of_items = total_items
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        print("Scrolling...")
        sleep(3)
        total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/" +
                                                        "div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div"))
    # we have got to bottom of page. Load all elements into a list.
    items_list = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                               "div[1]/div[2]/div[1]/div[1]/div[1]/div")
    print(len(items_list))
    # The last two divs are likely to have no information we want in them. Remove them from list.
    if len(items_list) > 4:
        items_list.pop()
        items_list.pop()
        print(len(items_list))
    print("finished scrolling")
    # get the URLs
    parse_items(items_list, name)


# noinspection PyArgumentList
def parse_items(items_list, name):
    """Parses the list for DIVs we can use"""
    print("Parsing Items in the " + name + " list...")
    my_list = []
    # for item in items_list:
    #    sleep(1)
    #   single_item = item.find_element_by_xpath(".//a[1]")
    #    #6div1 1div2 3div1 1a1 1span1

    # go through the divs and add indvidual divs inside to a list
    for i in range(len(items_list)):
        # The first div has different xpath
        if i == 0:
            first_list = items_list[i].find_elements_by_xpath("div")
            list.extend(first_list)
            print("this is item no " + str(i + 1) + ". The total size of list is " + str(len(my_list)))
        elif i == 1:
            # The second xpath has another different xpath
            second_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/" +
                                                               "div/div/div[2]/div/div/div/div[2]/div/div/div")
            list.extend(second_list)
            print("The second item is this one " + str(i + 1) + ". The total size of list is " + str(len(my_list)))
        else:
            # each xpath after the first two has same xpath pattern
            else_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/" +
                                                             "div/div/div[2]/div/div/div/div[" + str(i+1) + "]/div/div")
            list.extend(else_list)
            print("we are now on item number " + str(i + 1) + ". The total size of list is " + str(len(my_list)))
    print("Parsing the " + name + " list is finished.")
    get_hrefs(list, name)


def get_hrefs(my_list, name):
    """This gets the URLS from the list of DIVs"""
    print("Size of list of links list is " + str(len(list_of_links)) + ". The length of list from parse_items is " +
          str(len(my_list)) + ".")
    # in each div in the list, find the url. pause added to show progress ... When URL found, add to a global list
    for i in range(len(my_list)):
        sleep(0.05)
        temp = my_list[i].find_element_by_css_selector('a').get_attribute('href')
        list_of_links.append(temp)
        print(".", end="", flush=True)
    print(".")
    print("Finished getting HREFS for " + name + ".")


def open_links(my_list):
    """Opens each link so we can start process of finding comments"""
    print(str(len(list_of_links)))
    # each url requires new driver object which requires new facebook login
    for i in range(len(my_list)):
        ffprofile = webdriver.FirefoxProfile()
        ffprofile.set_preference("dom.webnotifications.enabled", False)
        driver = webdriver.Firefox(firefox_profile=ffprofile)
        temp = my_list[i]
        relogin(driver, web_scraper, temp)


def relogin(driver, my_web_scraper, temp):
    """This logs into and then goes back to URL from list and then scrolls to bottom of page"""
    driver.get(temp)
    driver.find_element_by_id('email').send_keys(my_web_scraper.username)
    driver.find_element_by_id('pass').send_keys(my_web_scraper.password)
    driver.find_element_by_id('loginbutton').click()
    driver.back()
    # clicks on Posts link
    driver.find_element_by_partial_link_text('Posts').click()
    # scrolls to bottom of page
    scroll_bottom_pages(driver, temp)
    # starts process for getting posts
    get_posts_lists(driver, temp)
    driver.close()
    # close object
    print("Closed: " + temp)


def scroll_bottom_pages(driver, temp):
    """Scrolls to bottom of 'PAGES' pages"""
    print("Scrolling " + temp + "...")
    # only scrolling down 5 times at maximum.
    for i in range(5):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        sleep(2)


def get_posts_lists(driver, temp):
    """This starts the process of separating posts from a URL"""
    print("Getting psots for " + temp + driver)


def test(my_web_scraper):
    """Chooses what browser to use and creates a driver for that browser"""
    # Choose wich browser to use
    # action = input('Do you want to use [C]hrome or [F]irefox?').upper()
    # if action not in "CF" or len(action)!=1:
    #   print("You didn't pick [C]hrome or [F]irefox. Give it another go")
    #   test(my_web_scraper)
    # create driver for Chrome
    # if action == 'C':
    #    chrome_options = webdriver.ChromeOptions()
    #    prefs = {"profile.default_content_setting_values.notifications": 2}
    #    chrome_options.add_experimental_option("prefs", prefs)
    #    driver = webdriver.Chrome(chrome_options=chrome_options)
    #    # driver chosen, open the webpage.
    #   open_webpage(driver)
    #    # enterlogin details and login
    #    enter_login_details(driver, my_web_scraper)
    #    # search for Maraenui
    #    search(driver)
    # create driver for Firefox
    # elif action == 'F':
    ffprofile = webdriver.FirefoxProfile()
    ffprofile.set_preference("dom.webnotifications.enabled", False)
    driver = webdriver.Firefox(firefox_profile=ffprofile)
    # driver chosen, open the webpage.
    open_webpage(driver)
    # enterlogin details and login
    enter_login_details(driver, my_web_scraper)
    search(driver, "Maraenui")
    driver.find_element_by_partial_link_text("Pages").click()
    scroll_bottom(driver, "Pages")
    # driver.find_element_by_partial_link_text("Places").click()       This and the next line need to do their own xpath
    # scroll_bottom(driver, "Places")
    # /html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/div/div/div[2]/div/div/div/div/div/div/ul/li. a list of li
    # driver.find_element_by_partial_link_text("Groups").click()
    # sleep(10)
    # scroll_bottom(driver, "Groups")
    open_links(list_of_links)


if __name__ == "__main__":
    """This is a webscraper for Facebook. The goal is to scrape comments and the gender of people making those comments
       about a location that we type in. Default place is Maraenui"""
    web_scraper = WebScraper()
    # u_name = input('What is your Facebook username?')
    # p_word = input('What is your Facebook password?')
    # web_scraper.set_username(u_name)
    # web_scraper.set_password(p_word)
    test(web_scraper)
