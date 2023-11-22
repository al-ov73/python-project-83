from page_analyzer.requests import response_from
from bs4 import BeautifulSoup


def get_tags(url):
    html_content = response_from(url).text
    soup = BeautifulSoup(html_content, "html.parser")
    if soup.h1:
        h1 = str(soup.h1.string)
    else:
        h1 = ''
    if soup.title:
        title = str(soup.title.string) if soup.title.string else ''
    else:
        title = ''
    if soup.find('meta', {'name': 'description'}):
        description = soup.find('meta', {'name': 'description'}).get('content')
    else:
        description = ''
    return h1, title, description
