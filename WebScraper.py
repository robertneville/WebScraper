# import libraries
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementNotInteractableException, InvalidArgumentException, \
    StaleElementReferenceException, TimeoutException, ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotSelectableException

list_of_links = []
global_list_of_comments = []
global_card_list = []
error_counter = 0


class WebScraper:
    """This class carries the username and pw of a facebook account. Default is user and pw"""

    def __init__(self):
        self.username = " @gmail.com"
        self.password = " "

    def set_password(self, password):
        assert isinstance(password, str)
        self.password = password

    def set_username(self, username):
        assert isinstance(username, str)
        self.username = username


def wait(by_type, value, driver):
    try:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((by_type, value))
        )
    except (NoSuchElementException, ElementNotSelectableException, ElementNotInteractableException) as e:
        print("wait" + str(e))
    except TimeoutException as ex:
        print("wait" + str(ex))
        pass


def open_webpage(driver):
    """Opens facebook"""
    # set up the web browser and goto the web page
    driver.get('https://www.facebook.com/')


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


def search(driver, term):
    """Search for a town or city"""
    print("Searching for " + term + ".")
    try:
        wait(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]" +
             "/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/input[2]", driver)
        wait(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]" +
             "/div[1]/form[1]/button[1]", driver)
        # find the elements needed to search
        search_box = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]" +
                                                  "/div[2]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/input[2]")
        search_button = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]" +
                                                     "/div[1]/div[2]/div[1]/form[1]/button[1]")
        # enter the search term and click the button and pause
        search_box.send_keys(term)
        search_button.click()
        # time.sleep(1)
        print("Found results for " + term + ".")
    except(NoSuchElementException, ElementNotSelectableException, ElementNotInteractableException) as e:
        print("search" + (str(e)))
        sys.exit(1)


def scroll_bottom(driver, name):
    """this scrolls to bottom of page to show all of the elements on a page."""
    time.sleep(5)
    print("Scrolling...")
    if name == "Pages":
        # goto container that has reults in it. Count the divs inside.
        no_of_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                        "div[1]/div[2]/div[1]/div[1]/div[1]/div"))
        # scroll down, hoping to trigger more results. Pause to give time to load those results
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(5)
        # Count divs again.
        total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                        "div[1]/div[2]/div[1]/div[1]/div[1]/div"))
        # If total_items > no_of_items then more divs were loaded. Scroll again. If not, bottom was reached.
        while total_items > no_of_items:
            no_of_items = total_items
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            print("Scrolling...")
            time.sleep(5)
            total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/" +
                                                            "div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div"))
        # we have got to bottom of page. Load all elements into a list.
        items_list = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                   "div[1]/div[2]/div[1]/div[1]/div[1]/div")
        # The last two divs are likely to have no information we want in them. Remove them from list.
        if len(items_list) > 4:
            items_list.pop()
            items_list.pop()
        print("finished scrolling")
        # get the URLs
        parse_items_pages(items_list, name)
    elif name == "Places":
        no_of_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                        "div[1]/div[2]/div[1]/div[1]/div[1]/div/div/div/ul/li"))
        # scroll down, hoping to trigger more results. Pause to give time to load those results
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        wait(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
             "div[1]/div[2]/div[1]/div[1]/div[1]/div/div/div/ul/li", driver)
        # Count li again.
        total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                        "div[1]/div[2]/div[1]/div[1]/div[1]/div/div/div/ul/li"))
        # If total_items > no_of_items then more li were loaded. Scroll again. If not, bottom was reached.
        count = 0
        while total_items > no_of_items & count < 10:
            count += 1
            no_of_items = total_items
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            print("Scrolling...")
            time.sleep(1)
            total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/" +
                                                            "div[1]/div[2]/div[1]/div[1]/div[1]/div/div/div/ul/li"))
        # we have got to bottom of page. Load all elements into a list.
        items_list = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                   "div[1]/div[2]/div[1]/div[1]/div[1]/div/div/div/ul/li")
        print("finished scrolling")
        # get the URLs
        parse_items_places(items_list, name)
    else:
        time.sleep(2)
        click_radio = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[1]/div/div/div/" +
                                                   "span/div/div/div[2]/div/a[2]")
        time.sleep(2)
        click_radio.click()
        time.sleep(2)
        no_of_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                        "div[1]/div[2]/div[1]/div[1]/div[1]/div"))
        # scroll down, hoping to trigger more results. Pause to give time to load those results
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        # time.sleep(2)
        wait(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
             "div[1]/div[2]/div[1]/div[1]/div[1]/div", driver)
        # Count divs again again.
        total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                        "div[1]/div[2]/div[1]/div[1]/div[1]/div"))
        # If total_items > no_of_items then more li were loaded. Scroll again. If not, bottom was reached.
        while total_items != no_of_items:
            no_of_items = total_items
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            print("Scrolling...")
            time.sleep(2)
            total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]" +
                                                            "/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div"))
        # we have got to bottom of page. Load all elements into a list.
        items_list = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/" +
                                                   "div[1]/div[2]/div[1]/div[1]/div[1]/div")
        # last two divs probably have useless information
        if len(items_list) > 3:
            items_list.pop()
            items_list.pop()
        print("finished scrolling. The length of items_list is " + str(len(items_list)))
        # get the URLs
        parse_items_groups(items_list, name)


def parse_items_pages(items_list, name):
    """Parses the list for DIVs we can use"""
    print("Parsing Items in the " + name + " list...")
    my_list = []
    time.sleep(2)
    # go through the divs and add individual divs inside to a list
    for i in range(len(items_list)):
        # The first div has different xpath
        if i == 0:
            first_list = items_list[i].find_elements_by_xpath("div")
            my_list.extend(first_list)
        elif i == 1:
            # The second xpath has another different xpath
            second_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/" +
                                                               "div/div/div[2]/div/div/div/div[2]/div/div/div")
            my_list.extend(second_list)
        else:
            # each xpath after the first two has same xpath pattern
            else_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/" +
                                                             "div/div/div[2]/div/div/div/div[" + str(i + 1) +
                                                             "]/div/div")
            my_list.extend(else_list)
    print("Parsing the " + name + " list is finished.")
    get_hrefs(my_list, name)


def parse_items_places(items_list, name):
    """Parses the list for DIVs we can use"""
    print("Parsing Items in the " + name + " list...")
    my_list = []
    time.sleep(2)
    # go through the divs and add individual divs inside to a list
    for i in range(len(items_list)):
        first_list = items_list[i].find_elements_by_xpath(".//div/div[2]/div/div[2]/div/div/table/tbody/tr/td/" +
                                                          "div/div[2]/span/a")
        # /html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/div/div/div[2]/div/div/div/div/div/div/ul/li[1]\
        # /div/div[2]/div/div[2]/div/div/table/tbody/tr[1]/td/div/div[2]/span/a
        my_list.extend(first_list)
    print("Parsing the " + name + " list is finished.")
    get_hrefs(my_list, name)


def parse_items_groups(items_list, name):
    """Parses the list for DIVs we can use"""
    print("Parsing Items in the " + name + " list...")
    my_list = []
    time.sleep(2)
    # go through the divs and add individual divs inside to a list
    for i in range(len(items_list)):
        print("my_list length = " + str(len(my_list)))
        # The first div has different xpath
        if i == 0:
            first_list = items_list[i].find_elements_by_xpath("//*[@id=BrowseResultsContainer]")
            my_list.extend(first_list)
        elif i == 1:
            # The second xpath has another different xpath
            second_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]" +
                                                               "/div[1]/div[3]/div[2]/div[1]/div[1]/" +
                                                               "div[2]/div[1]/div[1]/div[1]/div/div/div/div")
            my_list.extend(second_list)
        else:
            # each xpath after the first two has same xpath pattern
            else_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]" +
                                                             "/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]" +
                                                             "/div[" + str(i) + "]/div/div")
            my_list.extend(else_list)
    print("Parsing the " + name + " list is finished.")
    get_hrefs(my_list, name)


def get_hrefs(my_list, name):
    """This gets the URLS from the list of DIVs"""
    # in each div in the list, find the url. pause added to show progress ... When URL found, add to a global list
    for i in range(5):
        time.sleep(2)
        temp = my_list[i].find_element_by_tag_name("a").get_attribute('href')
        list_of_links.append(temp)
    print("Finished getting HREFS for " + name + ".")


def open_links(driver, my_list, page_type):
    """Opens each link so we can start process of finding comments"""
    # navigating to each URL from the open driver
    for i in range(len(my_list)):
        # go to url
        driver.get(my_list[i])
        try:
            # click on the posts link to get to posts
            if page_type == "Groups":
                driver.find_element_by_partial_link_text("Discussion").click()
            else:
                driver.find_element_by_partial_link_text('Posts').click()
            # scrolls to bottom of page
            scroll_bottom_pages(driver, my_list[i])
            # starts process for getting posts
            time.sleep(3)
            get_posts_lists(driver, my_list[i], page_type)
        except (NoSuchElementException, ElementNotSelectableException, ElementNotInteractableException) as e:
            print("open_links There are no posts for " + my_list[i] + " " + str(e))
            pass
        except InvalidArgumentException as ex:
            print("open_links" + str(ex))
            pass


def scroll_bottom_pages(driver, url):
    """Scrolls to bottom of 'PAGES' pages"""
    print("Scrolling " + url + "...")
    # only scrolling down 10 times at maximum on each page.
    for i in range(10):
        try:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            # give page chance to load next set of divs
            time.sleep(3)
        except Exception as ex:
            print("scroll_bottom_pages" + str(ex))
            pass
        except (Exception, NoSuchElementException, ElementNotInteractableException, ElementNotSelectableException) as e:
            print("scroll_bottom_pages" + str(e))
            pass


def get_posts_lists(driver, url, type2):
    """This starts the process of separating posts from a URL"""
    print("Getting posts for " + url)
    if type2 == "Groups":
        get_posts_lists_groups(driver, url)
    # check to see if element is there
    time.sleep(2)
    # a list of each card on the page
    xpath = "/html/body/div[1]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div"
    global_card_list.clear()
    parse_cards(driver, xpath)
    # list_of_posts = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[2]" +
    #                                              "/div[2]/div/div/div[2]/div/div")
    # get rid of empty cards
    list_of_posts = global_card_list[1:]
    # send list of cards to get each cards comments and URLs
    parse_posts(list_of_posts, url)


def get_posts_lists_groups(driver, url):
    """This starts the process of separating posts from a URL"""
     # print("Getting posts for " + url)
    time.sleep(5)
    return_list = []
    # check to see if element is there
    wait(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div[2]" +
         "/div[9]/div[4]/div/div", driver)
    # a list of each card on the page
    list_of_posts = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[2]/div/" +
                                                  "div[2]/div[2]/div[9]/div[4]/div/div/div")
    time.sleep(3)
    # recent activity and older divs to be removed
    try:
        if len(list_of_posts) > 0:
            # break up first element that contains recent and older posts
            temp_list = list_of_posts[0].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]" +
                                                                "/div[2]/div/div[2]/div[2]/div[9]/div[4]/div/div/" +
                                                                "div[1]/div")
            for i in range(len(temp_list)):
                wait(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div[2]/div[9]" +
                     "/div[4]/div/div", driver)
                if temp_list[i].text != "RECENT ACTIVITY":
                    if temp_list[i].text != "OLDER":
                        return_list.append(temp_list[i])
            # remove first item from list of posts as that has been spli and added to return list previously.
            # Then add that list to the return_list
            list_of_posts.pop(0)
        return_list.extend(list_of_posts)
        parse_posts_groups(return_list, url)
    except StaleElementReferenceException as e:
        print("get_posts_lists_groups " + str(e))
        time.sleep(5)
        pass


def parse_cards(driver, xpath):
    """This cycles through the divs. After scrolling the page, the extra divs are hidden in the last div
       Open last div, and if there are more, they will be hidden in the last div.
       Continue until we reach the div with the id."""
    list_of_cards = driver.find_elements_by_xpath(xpath)
    length = len(list_of_cards)
    last_9 = length - 9
    for i in range(last_9, length):
        try:
            card_class = list_of_cards[i].get_attribute("class")
            if card_class != "_1xnd":
                card_id = list_of_cards[i].get_attribute("id")
                if card_id != "www_pages_reaction_see_more_unitwww_pages_posts":
                    global_card_list.append(list_of_cards[i])
                else:
                    pass
            else:
                new_xpath = xpath + "/div"
                parse_cards(driver, new_xpath)
        except IndexError:
            pass


def parse_posts(list_of_posts, url):
    """This parses the posts of a page"""
    print("Parsing posts of " + url)
    for i in range(len(list_of_posts) - 1):
        wait(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/div[2]" +
             "/div/div[4]/div/div/div/div[3]/div[2]", list_of_posts[i])
        click_links(list_of_posts[i])
        comment_divs = get_web_comment(list_of_posts[i])
        comments_list = get_list_of_comments(comment_divs)
        global_list_of_comments.extend(comments_list)
    # list_of_comments.extend(my_list)
    print("Parsing the " + url + " list is finished.")
    # get_hrefs(my_list, name)


def parse_posts_groups(list_of_posts, url):
    """This parses the posts of a page"""
    print("Parsing posts of " + url)
    my_list = []
    for i in range(len(list_of_posts)):
        time.sleep(3)   # wait(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div[2]/div[9]/" +
     #          "div[4]/div/div[1]", list_of_posts[i])
        click_links(list_of_posts[i])
        # wait for just clicked links to register
        time.sleep(3)
        comment_divs = get_web_comment_groups(list_of_posts[i])
        comments_list = get_list_of_comments(comment_divs)
        global_list_of_comments.extend(comments_list)
        print(str(len(global_list_of_comments)))
    print("Parsing the " + url + " list is finished.")
    # get_hrefs(my_list, name)


def click_links(driver):
    """This clicks on links such as view replies and more comments to make more comments available"""
    try:
        time.sleep(5)
        click_the_links = driver.find_elements_by_partial_link_text(" more comment")
        for h in range(len(click_the_links)):
            click_the_links[h].click()
            time.sleep(3)
        click_replies = driver.find_elements_by_partial_link_text(" Replies")
        for i in range(len(click_replies)):
            click_replies[i].click()
            time.sleep(3)
        click_one_more_reply = driver.find_elements_by_partial_link_text("1 Reply")
        for j in range(len(click_one_more_reply)):
            click_one_more_reply[j].click()
            time.sleep(3)
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print("click_links " + str(e))
        pass


def get_web_comment(driver):
    # comment_div = driver.find_element_by_xpath(".//div/div/div/div[3]/div[2]/form/div[2]")
    try:
        no_of_divs = (len(driver.find_elements_by_xpath(".//div/div/div/div[3]/div[2]/form/div[2]/div/div")))
        time.sleep(3)
        if no_of_divs == 3:
            comment_divs = driver.find_elements_by_xpath(".//div/div/div/div[3]/div[2]/form/div[2]/div/div[2]" +
                                                         "/div/div")
            # check to see if comment_divs is empty
            if len(comment_divs) < 2:
                return comment_divs
            # check to see if we have a comment or add comment input
            comment_array = comment_divs[1].text.split("\n")
            if comment_array[0] == "Write a comment...":
                comment_divs = driver.find_elements_by_xpath(".//div/div/div/div[3]/div[2]/form/div[2]/div/div[3]" +
                                                             "/div/div")
                return comment_divs
            return comment_divs
        elif no_of_divs == 4:
            comment_divs = driver.find_elements_by_xpath(".//div/div/div/div[3]/div[2]/form/div[2]/div/" +
                                                         "div[3]/div/div")
            # check to see if comment_divs is empty
            if len(comment_divs) < 2:
                return comment_divs
            # check to see if we have a comment or add comment input
            comment_array = comment_divs[1].text.split("\n")
            if comment_array[0] == "Write a comment...":
                comment_divs = driver.find_elements_by_xpath(".//div/div/div/div[3]/div[2]/form/div[2]/div/div[4]" +
                                                             "/div/div")
                return comment_divs
            return comment_divs
        elif no_of_divs == 5:
            comment_divs = driver.find_elements_by_xpath(".//div/div/div/div[3]/div[2]/form/div[2]/div/" +
                                                         "div[4]/div/div")
            # check to see if comment_divs is empty
            if len(comment_divs) < 2:
                return comment_divs
            # check to see if we have a comment or add comment input
            comment_array = comment_divs[1].text.split("\n")
            if comment_array[0] == "Write a comment...":
                comment_divs = driver.find_elements_by_xpath(".//div/div/div/div[3]/div[2]/form/div[2]/div/div[5]" +
                                                             "/div/div")
                return comment_divs
            return comment_divs
        elif no_of_divs == 0:
            comment_divs_retry = driver.find_elements_by_xpath(".//div/div/div/div[3]/div[2]/form/div[2]/div" +
                                                               "/div/div[4]/div")
            print(str(len(comment_divs_retry)) + " divs found. get_web_comment.")
            return comment_divs_retry
        else:
            print("Number of divs exceeded 5. There are " + str(no_of_divs))
            comment_divs = []
            return comment_divs
    except NoSuchElementException as e:
        print("get_web_comment" + str(e))
        return []


def get_web_comment_groups(driver):
    try:
        comment_div = driver.find_element_by_xpath(".//div/div[3]/div[2]/form/div[2]")
        temp = comment_div.find_element_by_xpath(".//div").text
        if temp == '' or temp == "":
            return []
        else:
            no_of_divs = (len(driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div")))

            if no_of_divs == 3:
                comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[2]/div/div")
                # check to see if comment_divs is empty
                if len(comment_divs) < 2:
                    comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[3]/div/div")
                    return comment_divs
                # check to see if we have a comment or add comment input
                comment_array = comment_divs[1].text.split("\n")
                if comment_array[0] == "Write a comment...":
                    comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[3]/div/div")
                    return comment_divs
                return comment_divs
            elif no_of_divs == 4:
                # time.sleep(2)
                comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[3]/div/div")
                # check to see if comment_divs is empty
                if len(comment_divs) < 2:
                    comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[4]/div/div")
                    return comment_divs
                # check to see if we have a comment or add comment input
                comment_array = comment_divs[1].text.split("\n")
                if comment_array[0] == "Write a comment...":
                    comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[4]/div/div")
                    return comment_divs
                return comment_divs
            elif no_of_divs == 5:
                comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[4]/div/div")# check to see if comment_divs is empty
                if len(comment_divs) < 2:
                    comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[5]/div/div")
                    return comment_divs
                # check to see if we have a comment or add comment input
                comment_array = comment_divs[1].text.split("\n")
                if comment_array[0] == "Write a comment...":
                    comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[5]/div/div")
                    return comment_divs
                return comment_divs
            elif no_of_divs == 2:
                comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[2]/div/div")
                return comment_divs
            elif no_of_divs == 1:
                comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div/div/div")
                return comment_divs
            else:
                print("Number of divs exceeded 5. There are " + str(no_of_divs))
                comment_divs = []
                return comment_divs
    except NoSuchElementException as e:
        print("get_web_comment_groups" + str(e))
        return []


def get_list_of_comments(comment_list):
    """This returns a list of individual comments."""
    time.sleep(3)
    length = len(comment_list)
    returns_list = []
    for i in range(length):
        try:
            comment_array = comment_list[i].text.split("\n")
            if comment_array[0] == '':
                pass
            elif comment_array[0] == "Write a comment...":
                pass
            else:
                comment_text = comment_array[0]
                returns_list.append(comment_text)
                print('.', end='', flush=True)
        except StaleElementReferenceException as e:
            print("get_list_of_comments " + str(e))
            pass
    return returns_list


def test(my_web_scraper, error_counter2):
    """Chooses what browser to use and creates a driver for that browser"""
    start_time = time.clock()
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
    search(driver, "Addington")
    try:
        time.sleep(3)
        driver.find_element_by_partial_link_text("Pages").click()
        # driver.find_element_by_partial_link_text("Places").click()
        # driver.find_element_by_partial_link_text("Groups").click()
    except (Exception, NoSuchElementException, ElementNotInteractableException, ElementNotSelectableException) as e:
        print("test " + e)
        driver.close()
        error_counter2 += 1
        if error_counter2 < 5:
            web_scraper2 = WebScraper()
            test(web_scraper2, error_counter2)
            pass
        else:
            print("There was an unresolved issue and there were too many errors. Program will close")
            sys.exit(1)
    except Exception as ex:
        print("unknown error" + str(ex))
        sys.exit(1)
    scroll_bottom(driver, "Pages")
    # scroll_bottom(driver, "Places")
    # scroll_bottom(driver, "Groups")
    open_links(driver, list_of_links, "Pages")
    # open_links(driver, list_of_links, "Places")
    # open_links(driver, list_of_links, "Groups")
    for i in range(len(global_list_of_comments)):
        print(global_list_of_comments[i])
    print("My program took", time.clock() - start_time, " to run.")
    print(str(len(global_list_of_comments)))


if __name__ == "__main__":
    """This is a webscraper for Facebook. The goal is to scrape comments and the gender of people making those comments
       about a location that we type in. Default place is Maraenui"""
    web_scraper = WebScraper()
    # u_name = input('What is your Facebook username?')
    # p_word = input('What is your Facebook password?')
    # web_scraper.set_username(u_name)
    # web_scraper.set_password(p_word)
    test(web_scraper, error_counter)
