# import libraries
import datetime
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
        self.username = ""
        self.password = ""
        self.search = ""

    def set_password(self, password):
        assert isinstance(password, str)
        self.password = password

    def set_username(self, username):
        assert isinstance(username, str)
        self.username = username

    def set_search(self, searchterm):
        assert isinstance(searchterm, str)
        self.search = searchterm


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


def enter_login_details(driver, webscraper):
    """Logs into facebook"""
    u_name = input('What is your Facebook username?\n')
    p_word = input('What is your Facebook password?\n')
    web_scraper.set_username(u_name)
    web_scraper.set_password(p_word)
    # find the elements needed to login
    username_box = driver.find_element_by_id('email')
    password_box = driver.find_element_by_id('pass')
    login_button = driver.find_element_by_id('loginbutton')
    # enter the username and passwords and then click the login button
    username_box.send_keys(webscraper.username)
    password_box.send_keys(webscraper.password)
    login_button.click()


def scroll_bottom_results(driver, page_type):
    """this scrolls to bottom of results to show all of the hidden elements on a page."""
    time.sleep(5)
    print('-+', end='', flush=True)
    if page_type == "Pages":
        # go to container that has reults in it. Count the divs inside.
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
            print('-+', end='', flush=True)
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
        parse_items_pages(items_list, page_type)
    else:
        time.sleep(2)
        # clicking on open groups radio button.
        click_radio = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[1]/div/div/div/" +
                                                   "span/div/div/div[2]/div/a[2]")
        time.sleep(2)
        click_radio.click()
        time.sleep(2)
        # only open groups in search results
        scroll_items = len(driver.find_elements_by_xpath("// *[ @ id = \"u_ps_jsonp_5_3_0\"]/div"))
        # scroll down, hoping to trigger more results. Pause to give time to load those results
        # time.sleep(2)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(3)
        # Count divs again again.
        new_scroll_items = len(driver.find_elements_by_xpath("// *[ @ id = \"u_ps_jsonp_5_3_0\"]/div"))
        # If new_scroll_items >  scroll_items then more items were loaded. Scroll again. If not, bottom was reached.
        while new_scroll_items != scroll_items:
            scroll_items = new_scroll_items
            print('-+', end='', flush=True)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(3)
            new_scroll_items = len(driver.find_elements_by_xpath("// *[ @ id = \"u_ps_jsonp_5_3_0\"]/div"))
        # we have got to bottom of page. Load all elements into a list.
        items_list = driver.find_elements_by_xpath("//*[@id=\"BrowseResultsContainer\"]/div")
        # last two divs probably have useless information
        if len(items_list) > 3:
            items_list.pop()
            items_list.pop()
        print("finished scrolling. The length of items_list is " + str(len(items_list)))
        # get the URLs
        parse_items_groups(items_list, page_type)


def parse_items_pages(items_list, page_type):
    """Parses the list for DIVs we can use"""
    print("Parsing Items in the " + page_type + " list...")
    my_list = []
    time.sleep(2)
    # go through the divs and add individual divs inside to a list
    for i in range(len(items_list)):
        # The first div has different xpath
        if i == 0:
            first_list = items_list[i].find_elements_by_xpath("div")
            # check to see if New Zealand is in description. If it is then add to list.
            for j in range(len(first_list)):
                if first_list[j].text.find("New Zealand") >= 0:
                    my_list.append(first_list[j])
        # The second xpath has another different xpath
        elif i == 1:
            second_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/" +
                                                               "div/div/div[2]/div/div/div/div[2]/div/div/div")
            # check to see if New Zealand is in description. If it is then add to list.
            for j in range(len(second_list)):
                if second_list[j].text.find("New Zealand") >= 0:
                    my_list.append(second_list[j])
        else:
            # each xpath after the first two has same xpath pattern
            else_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]/" +
                                                             "div/div/div[2]/div/div/div/div[" + str(i + 1) +
                                                             "]/div/div")
            # check to see if New Zealand is in description. If it is then add to list.
            for j in range(len(else_list)):
                if else_list[j].text.find("New Zealand") >= 0:
                    my_list.append(else_list[j])
    print("Parsing the " + page_type + " list is finished.")
    get_hrefs(my_list, page_type)


def parse_items_groups(items_list, page_type):
    """Parses the list for DIVs we can use"""
    print("Parsing Items in the " + page_type + " list...")
    my_list = []
    time.sleep(2)
    # go through the divs and add individual divs inside to a list
    for i in range(len(items_list)):
        print("my_list length = " + str(len(my_list)))
        # The first div has different xpath
        if i == 0:
            first_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[3]/div[2]" +
                                                              "/div/div/div[2]/div/div/div/div[1]/div")
            my_list.extend(first_list)
            # check to see if items in this list are from New Zealand.
            """for j in range(len(first_list)):
                if first_list[j].text.find("New Zealand") >= 0:
                    my_list.append(first_list[j])"""
        elif i == 1:
            # The second xpath has another different xpath
            second_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]" +
                                                               "/div[1]/div[3]/div[2]/div[1]/div[1]/" +
                                                               "div[2]/div[1]/div[1]/div[1]/div/div/div/div")
            my_list.extend(second_list)
            # check to see if items in this list are from New Zealand.
            """for j in range(len(second_list)):
                if second_list[j].text.find("New Zealand") >= 0:
                    my_list.append(second_list[j])"""
        else:
            # each xpath after the first two has same xpath pattern
            else_list = items_list[i].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div[1]/div[3]" +
                                                             "/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]" +
                                                             "/div[" + str(i) + "]/div/div")
            my_list.extend(else_list)
            """"# check to see if items in this list are from New Zealand.
            for j in range(len(else_list)):
                if else_list[j].text.find("New Zealand") >= 0:
                    my_list.append(else_list[j])"""
    print("Parsing the " + page_type + " list is finished.")
    get_hrefs(my_list, page_type)


def get_hrefs(my_list, name):
    """This gets the URLS from the list of DIVs"""
    # in each div in the list, find the url. pause added to show progress ... When URL found, add to a global list
    # only getting the first five valid results.
    for i in range(5):
        try:
            time.sleep(2)
            temp = my_list[i].find_element_by_tag_name("a").get_attribute('href')
            list_of_links.append(temp)
        # if there isn't five valid HREFS then exception will just pass. There is only 5 we need so it will be fast.
        except IndexError:
            pass
    print("Finished getting HREFS for " + name + ".")


def open_links(driver, my_list, page_type):
    """Opens each link so we can start process of finding comments"""
    # navigating to each URL from the open driver
    for i in range(len(my_list)):
        # go to url
        driver.get(my_list[i])
        try:
            # click on the posts link to get to posts
            if page_type == "Pages":
                driver.find_element_by_partial_link_text('Posts').click()
            else:
                driver.find_element_by_partial_link_text('Discussion').click()
            # scrolls to bottom of page
            scroll_bottom_again(driver, my_list[i], page_type)
            # starts process for getting posts
            time.sleep(3)
            get_posts_lists(driver, my_list[i], page_type, )
        except (NoSuchElementException, ElementNotSelectableException, ElementNotInteractableException) as e:
            print("open_links There are no posts for " + my_list[i] + " " + str(e))
            pass
        except InvalidArgumentException as ex:
            print("open_links" + str(ex))
            pass


def scroll_bottom_again(driver, url, page_type):
    """Second time we are scrolling down. We are on an individual Pages or Groups Page.
       Scrolling down to get all of the posts and comments. May be quite large"""
    print("Scrolling " + url + "...")
    # Scrolling down whole page
    if page_type == "Pages":
        time.sleep(3)
        # scroll down, hoping to trigger more results. Pause to give time to load those results
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(3)
        xpath = "/html/body/div[1]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div"
        list_of_items = driver.find_elements_by_xpath(xpath)
        length = len(list_of_items)
        # wait for more divs to load.
        # time.sleep(3)
        # if the last div has class of _1xnd then there is more scrolling to be done.
        xpath2 = "/html/body/div[1]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/div[2]/" + \
                 "div/div[" + str(length) + "]"
        try:
            while list_of_items[length-1].get_attribute("class") == "_1xnd":
                # scroll down and allow time for new items to load
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                time.sleep(5)
                # clear old list and create new list with the new items that have been scrolled.
                list_of_items.clear()
                list_of_items = driver.find_elements_by_xpath(xpath2 + "/div")
                # get new length of the list of new divs
                length = len(list_of_items)
                # at the end of scrolling the list of items could be empty. This means there is nothing more to scroll.
                if length == 0:
                    break
                # create new xpath to find the children of the last item in the new list of items
                xpath_addition = "/div[" + str(length) + "]"
                xpath2 += xpath_addition
        except (ElementNotSelectableException, ElementNotInteractableException) as e:
            print("scroll_bottom_again. Error occured in  " + url + ". " + e)

        print("finished scrolling " + url + ".")

    else:
        time.sleep(3)
        no_of_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[2]/" +
                                                        "div/div[2]/div[2]/div[9]/div[5]/div/div[1]/div"))
        # scroll down, hoping to trigger more results. Pause to give time to load those results
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        # wait for more divs to load.
        time.sleep(5)
        # Count divs again again.
        total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[2]/" +
                                                        "div/div[2]/div[2]/div[9]/div[5]/div/div[1]/div"))
        # If total_items > no_of_items then more div were loaded. Scroll again. If not, bottom was reached.
        while total_items != no_of_items:
            no_of_items = total_items
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            print('-+', end='', flush=True)
            time.sleep(3)
            total_items = len(driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[2]" +
                                                            "/div/div[2]/div[2]/div[9]/div[5]/div/div[1]/div"))
        print("finished scrolling " + url + ".")
    """ # only scrolling down 10 times at maximum on each page.
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
            pass"""


def get_posts_lists(driver, url, page_type):
    """This starts the process of separating posts from a URL"""
    print("Getting posts for " + url)
    if page_type == "Groups":
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
         "/div[9]/div[5]/div/div", driver)
    # a list of each card on the page
    list_of_posts = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[2]/div/" +
                                                  "div[2]/div[2]/div[9]/div[5]/div/div/div")
    time.sleep(3)
    # recent activity and older divs to be removed
    try:
        if len(list_of_posts) > 0:
            # break up first element that contains recent and older posts
            temp_list = list_of_posts[0].find_elements_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]" +
                                                                "/div[2]/div/div[2]/div[2]/div[9]/div[5]/div/div/" +
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
    if length >= 9:
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
                    """CHECK HERE. IS THIS RIGHT?"""
                    new_xpath = xpath + "/div"
                    parse_cards(driver, new_xpath)
            except IndexError:
                pass
        else:
            for i in range(length):
                card_id = list_of_cards[i].get_attribute("id")
                if card_id != "www_pages_reaction_see_more_unitwww_pages_posts":
                    global_card_list.append(list_of_cards[i])
                else:
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
    for i in range(len(list_of_posts)):
        time.sleep(3)
        click_links(list_of_posts[i])
        # wait for just clicked links to register
        time.sleep(3)
        comment_divs = get_web_comment_groups(list_of_posts[i])
        comments_list = get_list_of_comments(comment_divs)
        global_list_of_comments.extend(comments_list)
        # print(str(len(global_list_of_comments)))
    print("Parsing the " + url + " list is finished.")


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
                comment_divs = driver.find_elements_by_xpath(".//div/div[3]/div[2]/form/div[2]/div/div[4]/div/div")
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


def set_driver():
    """returns a WebDriver to open either a Chrome or Firefox web browser"""
    # Choose which browser to use
    action = input('Do you want to use [C]hrome or [F]irefox?\n').upper()
    if action not in "CF" or len(action) != 1:
        print("You didn't pick [C]hrome or [F]irefox. Give it another go\n")
        set_driver()
    else:
        # Chrome browser
        if action == 'C':
            chrome_options = webdriver.ChromeOptions()
            prefs = {"profile.default_content_setting_values.notifications": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome(chrome_options=chrome_options)
            return driver
        # Firefox browser
        else:
            ffprofile = webdriver.FirefoxProfile()
            ffprofile.set_preference("dom.webnotifications.enabled", False)
            driver = webdriver.Firefox(firefox_profile=ffprofile)
            return driver


def search_town(driver, my_webdriver):
    """Search for a town or city."""
    searchtown = input("Enter a town to search for. Facebook has a very simple search function. \n" +
                       "Using special search characters such as \"+\" or quotes around terms will not work.\n" +
                       "Addington New Zealand or Maraenui are examples of good searches. \"Addington\" + New Zealand" +
                       " is not.\n")
    print("Searching for " + searchtown)
    my_webdriver.set_search(searchtown)
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
        time.sleep(5)
        search_box.send_keys(searchtown)
        search_button.click()
        print("Found results for " + searchtown + ".")
    except(NoSuchElementException, ElementNotSelectableException, ElementNotInteractableException) as e:
        print("search" + (str(e)) + ". Program has failed. Restart program.")
        sys.exit(1)


def type_search(driver, my_web_scraper):
    """This chooses either Pages or Groups then it goes to those search pages and scrolls to bottom of that page
       find the link to each page on that page and then finds each post on that page and gets any comments"""
    type_of_search = input("Are you looking for [P]ages or [G]roups.\n").upper()
    if type_of_search not in "PG":
        print("You didn't choose [P]ages or [G]roups. Try again.\n")
        type_search(driver, my_web_scraper)
    try:
        if type_of_search == 'P':
            driver.find_element_by_partial_link_text("Pages").click()
            time.sleep(5)
            scroll_bottom_results(driver, "Pages")
            open_links(driver, list_of_links, "Pages")
            output_to_file("Pages", my_web_scraper)
        elif type_of_search == 'G':
            driver.find_element_by_partial_link_text("Groups").click()
            time.sleep(5)
            scroll_bottom_results(driver, "Groups")
            open_links(driver, list_of_links, "Groups")
            output_to_file("Groups", my_web_scraper)
    except (Exception, NoSuchElementException, ElementNotInteractableException, ElementNotSelectableException) as e:
        print("Shutting down browser and program. " + e)
        # close browser, give time to read error message and shut down program.
        driver.close()
        time.sleep(25)
        sys.exit(1)


def output_to_file(page_type, my_web_scraper):
    """writes list of commets to file. Naming format should be like page_type_dd_mm_YYYY_H_M_S
    e.g. Maranui_Pages_22_7_2018_4_28_58.txt"""
    now = datetime.datetime.now()
    filename = my_web_scraper.search + "_" + page_type + "_" + str(now.strftime("%d_%m_%Y_%H_%M_%S")) + ".txt"
    file = open(filename, "w")
    for i in range(len(global_list_of_comments)):
        file.write(global_list_of_comments[i])


def run_scraper(my_web_scraper):
    """Chooses what browser to use and creates a driver for that browser"""
    start_time = time.clock()
    # get the WebDriver for selected browser and open the browser
    driver = set_driver()
    driver.get('http://facebook.com')
    # get user Facebook details and use them.
    enter_login_details(driver, my_web_scraper)
    # enter search parameter and search for it.
    search_town(driver, my_web_scraper)
    # decide what you are looking for. Pages or Groups and then get data
    type_search(driver, my_web_scraper)
    for i in range(len(global_list_of_comments)):
        print(global_list_of_comments[i])
    print("My program took", time.clock() - start_time, " to run.")
    print(str(len(global_list_of_comments)))


if __name__ == "__main__":
    """This is a webscraper for Facebook. The goal is to scrape commentsof people making those comments
       about a location that we type in."""
    web_scraper = WebScraper()
    run_scraper(web_scraper)
