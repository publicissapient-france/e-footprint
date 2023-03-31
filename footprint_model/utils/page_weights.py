import requests
from bs4 import BeautifulSoup
import http.cookiejar
import os
import tempfile


def get_page_size(url):
    """
    Returns the size of a web page in megabytes
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers, stream=True)
    with tempfile.TemporaryFile() as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
        f.seek(0)
        size = os.fstat(f.fileno()).st_size
    size_in_mb = size / (1024 * 1024)
    return size_in_mb


def get_page_sizes(urls):
    """
    Returns a list of the sizes of web pages for a list of URLs
    """
    page_sizes = []
    for url in urls:
        size = get_page_size(url)
        page_sizes.append(size)
    return page_sizes


def get_links(url):
    """
    Extracts all URL links from a webpage and returns them as a list
    """
    session = requests.Session()
    cookie_jar = http.cookiejar.CookieJar()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
    session.get(url, cookies=cookie_jar)
    soup = BeautifulSoup(session.get(url, cookies=cookie_jar).text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href: #and href.startswith('http'):
            links.append(href)
    return links


if __name__ == "__main__":
    url = 'https://www.sonepar.fr/catalog/fr-fr/search/cable?filters=%7B%22category%22%3A%5B%22SCC0102%22%5D%7D'
    links = get_links(url)
    catalog_links = ["https://www.sonepar.fr" + href for href in links if "catalog" in href]

    sizes = get_page_sizes(catalog_links)
