
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


if __name__ == "__main__":
    web_scraper = WebScraper()
    print("What is your Facebook username?")
    u_name = input()
    print("What is your Facebook password?")
    p_word = input()
    web_scraper.get_username(u_name)
    web_scraper.get_password(p_word)
    test(web_scraper)
