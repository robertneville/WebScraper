# import libraries
import urllib3
import bs4
import certifi


class WebScraper:
    def __init__(self):
        self.username = "username"
        self.password = "password"

    def get_password(self, password):
        assert isinstance(password, str)
        self.password = password

    def get_username(self, username):
        assert isinstance(username, str)
        self.username = username


def test(my_web_scraper):
    print("Your username is: " + my_web_scraper.username + "\n")
    print("Your password is: " + my_web_scraper.password + "\n")
    # the url I am using
    quote_page = 'https://www.facebook.com'
    # create a PoolManager to make requests
    page = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    # make a request to a web page
    request = page.request('GET', quote_page)
    soup = bs4.BeautifulSoup(request, 'html.parser')
    # Take out the <div> of name and get its value
    name_box = soup.find('input', attrs={'class': 'inputtext', 'name': 'email'})
    # strip() is used to remove starting and trailing
    name = name_box
    print(name)
    # get the index price
    price_box = soup.find('div', attrs={'class': 'price’'})
    price: str = price_box
    print(price)


if __name__ == "__main__":
    web_scraper = WebScraper()
    print("What is your Facebook username?")
    u_name = input()
    print("What is your Facebook password?")
    p_word = input()
    web_scraper.get_username(u_name)
    web_scraper.get_password(p_word)
    test(web_scraper)
