from bs4 import BeautifulSoup
from time import sleep
import urllib.parse

"""
    googleNewsQuery.py
    googleTopPageQuery.py
    で共用される関数の記述。
"""

def HrefToURL(hrefText:str):
    """
        hrefの内容からurlのみを抽出する。
    """
    return hrefText.strip("/url?q=").split(r"&sa=U")[0]

# AタグからURLを取ってくる
def urlGet(article_soup:BeautifulSoup):
    """
        Aタグを取って、URLを返す。
    """
    a_tag_contents_str =str(article_soup.select("a")[0].get('href'))
    url = HrefToURL(a_tag_contents_str)
    url = urllib.parse.unquote(url)
    # print(url)
    # sleep(2)
    return url

def normalizeWeightToKeyword(target_keyword_list:dict):
    sum = 0
    for keyword, weight in target_keyword_list.items():
        sum += weight
    for keyword, weight in target_keyword_list.items():
       target_keyword_list[keyword] = weight / sum
    # print(target_keyword_list) # float確認
    return target_keyword_list