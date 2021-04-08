from bs4 import BeautifulSoup


def main_text_from_html(html):
    """
    Return text from the 'main' tag of some html
    Allows easier maintenance of email templates, since no separate .txt template is required
    """
    soup = BeautifulSoup(html, features="html.parser")
    main = soup.find("main")
    if not main:
        raise ValueError("Passed html does not include a 'main' element")
    return main.get_text()
