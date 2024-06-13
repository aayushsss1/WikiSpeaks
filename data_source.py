from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import requests
import wikipedia
from bs4 import BeautifulSoup

def get_wikipedia_content(search):
    # set language to English (default is auto-detect)
    lang = "en"

    # create URL based on user input and language
    url = f"https://{lang}.wikipedia.org/wiki/{search}"

    # send GET request to URL and parse HTML content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # extract main content of page
    content_div = soup.find(id="mw-content-text")

    # extract all paragraphs of content
    paras = content_div.find_all('p')

    # concatenate paragraphs into full page content
    full_page_content = ""
    for para in paras:
        full_page_content += para.text

    # print the full page content
    return full_page_content