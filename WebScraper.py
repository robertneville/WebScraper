# import libraries
import time
import sys
import tkinter
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotSelectableException

list_of_links = []
error_counter = 0


class WebScraper:
    """This class carries the username and pw of a facebook account. Default is user and pw"""
    def __init__(self):
        self.username = "email@gmail.com"
        self.password = "password"

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
    time.sleep(3)


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
    time.sleep(1)
    print("Found results for " + term + ".")


def scroll_bottom(driver, name):
    """this scrolls to bottom of page to show all of the elements on a page."""
    print("Scrolling...")
    # goto container that has reults in it. Count the divs inside.
    no_of_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                    "div[1]/div[2]/div[1]/div[1]/div[1]/div"))
    # scroll down, hoping to trigger more results. Pause to give time to load those results
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    time.sleep(2)
    # Count divs again.
    total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                    "div[1]/div[2]/div[1]/div[1]/div[1]/div"))
    # If total_items > no_of_items then more divs were loaded. Scroll again. If not, bottom was reached.
    count = 0
    while total_items > no_of_items & count < 1:
        count += 1
        no_of_items = total_items
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        print("Scrolling...")
        time.sleep(3)
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


def parse_items(items_list, name):
    """Parses the list for DIVs we can use"""
    print("Parsing Items in the " + name + " list...")
    my_list = []
    time.sleep(2)
    # go through the divs and add individual divs inside to a list
    for i in range(len(items_list)):
        # The first div has different xpath
        if i == 0:
            time.sleep(2)
            first_list = items_list[i].find_elements_by_xpath("div")
            my_list.extend(first_list)
            print("this is item no " + str(i + 1) + ". The total size of list is " + str(len(my_list)))
        elif i == 1:
            # The second xpath has another different xpath
            second_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/" +
                                                               "div/div/div[2]/div/div/div/div[2]/div/div/div")
            my_list.extend(second_list)
            print("The second item is this one " + str(i + 1) + ". The total size of list is " + str(len(my_list)))
        else:
            # each xpath after the first two has same xpath pattern
            else_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/" +
                                                             "div/div/div[2]/div/div/div/div[" + str(i+1) + "]/div/div")
            my_list.extend(else_list)
            print("we are now on item number " + str(i + 1) + ". The total size of list is " + str(len(my_list)))
    print("Parsing the " + name + " list is finished.")
    get_hrefs(my_list, name)


def get_hrefs(my_list, name):
    """This gets the URLS from the list of DIVs"""
    print("Size of list of links list is " + str(len(list_of_links)) + ". The length of list from parse_items is " +
          str(len(my_list)) + ".")
    # in each div in the list, find the url. pause added to show progress ... When URL found, add to a global list
    for i in range(len(my_list)):
        if i > 7 and i < 11:
            time.sleep(0.05)
            temp = my_list[i].find_element_by_css_selector('a').get_attribute('href')
            list_of_links.append(temp)
    print("Finished getting HREFS for " + name + ".")


def open_links(driver, my_list):
    """Opens each link so we can start process of finding comments"""
    print(str(len(list_of_links)))
    # navigating to each URL from the open driver
    for i in range(len(my_list)):
        driver.get(my_list[i])
        try:
            driver.find_element_by_partial_link_text('Posts').click()
            # scrolls to bottom of page
            scroll_bottom_pages(driver, my_list[i])
            # starts process for getting posts
            get_posts_lists(driver, my_list[i])
        except (NoSuchElementException, ElementNotSelectableException, ElementNotInteractableException) as e:
            print("There are no posts for " + my_list[i])
            pass
    # each url requires new driver object which requires new facebook login
    """for i in range(len(my_list)):
        ffprofile = webdriver.FirefoxProfile()
        ffprofile.set_preference("dom.webnotifications.enabled", False)
        driver = webdriver.Firefox(firefox_profile=ffprofile)
        temp = my_list[i]
        relogin(driver, web_scraper, temp)"""


"""def relogin(driver, my_web_scraper, temp):
    This logs into and then goes back to URL from list and then scrolls to bottom of page
    driver.get(temp)
    driver.find_element_by_id('email').send_keys(my_web_scraper.username)
    driver.find_element_by_id('pass').send_keys(my_web_scraper.password)
    driver.find_element_by_id('loginbutton').click()
    driver.back()
    # clicks on Posts link
    try:
        driver.find_element_by_partial_link_text('Posts').click()
    except (NoSuchElementException, ElementNotSelectableException, ElementNotInteractableException) as e:
        pass
    # scrolls to bottom of page
    scroll_bottom_pages(driver, temp)
    # starts process for getting posts
    get_posts_lists(driver, temp)
    driver.close()
    # close object
    print("Closed: " + temp)"""


def scroll_bottom_pages(driver, temp):
    """Scrolls to bottom of 'PAGES' pages"""
    print("Scrolling " + temp + "...")
    # check to see if window is scrollable
    check = driver.find_elements_by_xpath("// *[ @ id = 'pagelet_timeline_main_column']/div")
    # check = driver.find_elements_by_xpath("")
    # if len(check) > 3:
    # only scrolling down 5 times at maximum.
    for i in range(5):
        try:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
#            sleep(2)
        except Exception:
            pass
        except (Exception, NoSuchElementException, ElementNotInteractableException, ElementNotSelectableException) as e:
            print("THIS IS THE ERROR: " + e)
            pass
        finally:
            pass


def get_posts_lists(driver, url):
    """This starts the process of separating posts from a URL"""
    print("Getting posts for " + url)
    time.sleep(5)
    list_of_posts = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[2]"
                                                 + "/div[2]/div/div/div[2]/div/div")

    print(len(list_of_posts))
    list_of_posts = list_of_posts[3:]
    print(len(list_of_posts))
    parse_posts(driver, list_of_posts, url)
    # parseitems
    # gethrefs
    # openlinks
    # get gender
    # back copy text


def parse_posts(driver, list_of_posts, url):
    """This parses the posts of a page"""
    print("Parsing posts of " + url)
    my_list = []
    for i in range (len(list_of_posts)):
        time.sleep(3)
        comment_divs = list_of_posts[i].find_elements_by_xpath("//div/div/div/div[3]/div[2]/form/div[2]/div/div[2]/div/div")
        get_posts(comment_divs, url)
        """for j in range(len(comment_divs)):
            print("What the whole comment says: /n" + comment_divs[j].text)
            time.sleep(3)
        #    the_whole_comment = comment_divs[j].find_element_by_xpath("//div/div/div/div[2]/div/div/div/div/div/span")
            the_whole_comment = comment_divs[j].find_element_by_xpath("//div")
            print("What the whole comment says: /n" + comment_divs[j].text)
            print("The whole comment text : + " + the_whole_comment.text)
            time.sleep(3)
            test_urls = the_whole_comment.find_elements_by_tag_name('a')
            string = the_whole_comment.text
            commenters_url = the_whole_comment.find_element_by_tag_name('a')
            test_comment_url = commenters_url.get_attribute('href')
            time.sleep(3)
            commenters_text = the_whole_comment.text
            print("URL of commenter = " + commenters_url.get_attribute('href'))
            print("The actual comment is: " + commenters_text)
            print("test string: " + string)"""

    # go through the divs and add individual divs inside to a list
    # for i in range(len(list_of_posts)):
    # The first div has different xpath
    print("Parsing the " + url + " list is finished.")
    # get_hrefs(my_list, name)


def get_posts(comment_divs, url):
    length = len(comment_divs)
    for i in range(length):
        comment = comment_divs[i].find_element_by_xpath("//div/div/div/div[3]/div[2]/form/div[2]/div/div[2]/div/div")
        comment_text = comment.text
        comment_url = comment.find_element_by_xpath("//span[2]/a")
        print("String of comment: " + comment_text + "\n URL of comment: " + comment_url)


def test(my_web_scraper, error_counter):
    """Chooses what browser to use and creates a driver for that browser"""
    start_time=time.clock()
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
    try:
        driver.find_element_by_partial_link_text("Pages").click()
    except (Exception, NoSuchElementException, ElementNotInteractableException, ElementNotSelectableException) as e:
        print("THIS IS THE ERROR: " + e)
        driver.close()
        error_counter += 1
        if(error_counter < 5):
            web_scraper = WebScraper()
            test(web_scraper, error_counter)
            pass
        else:
            print("There was an unresolved issue and there were too many errors. Program will close")
            sys.exit(1)
    except Exception:
        print("unknown error. Program will quit.")
        sys.exit(1)

    scroll_bottom(driver, "Pages")
    # driver.find_element_by_partial_link_text("Places").click()       This and the next line need to do their own xpath
    # scroll_bottom(driver, "Places")
    # /html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/div/div/div[2]/div/div/div/div/div/div/ul/li. a list of li
    # driver.find_element_by_partial_link_text("Groups").click()
    # sleep(10)
    # scroll_bottom(driver, "Groups")
    open_links(driver, list_of_links)
    print("My program took", time.clock() - start_time, " to run.")


if __name__ == "__main__":
    """This is a webscraper for Facebook. The goal is to scrape comments and the gender of people making those comments
       about a location that we type in. Default place is Maraenui"""
    web_scraper = WebScraper()
    # u_name = input('What is your Facebook username?')
    # p_word = input('What is your Facebook password?')
    # web_scraper.set_username(u_name)
    # web_scraper.set_password(p_word)
    test(web_scraper, error_counter)
