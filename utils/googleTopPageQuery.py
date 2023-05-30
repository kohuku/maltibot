import requests
from bs4 import BeautifulSoup
from typing import Tuple
from utils import fileUtils,myUtils
from time import sleep
import urllib.parse


"""
    google検索のトップ10の情報を解析して返す。
"""

class OneSite:
    """
        構造体：タイトル、URL構造、説明など検索トップで表示される1つのサイトに関する情報。
    """
    
    def __init__(self, title:str, description:str,url_structure:str, url:str) -> None:
        self.title = title
        self.description = description
        self.url_structure = url_structure
        self.url = url
    
    def get_as_json(self) -> dict:
        return {"title" : self.title, "url_structure" : self.url_structure, "description" : self.description, "url" : self.url }

    def is_contain_keyword(self, target_word:str):
        hitted_contents = []
        if target_word in self.title:
            hitted_contents.append("title")
        if target_word in self.url_structure:
            hitted_contents.append("url_structure")
        if target_word in self.description:
            hitted_contents.append("description")
        if hitted_contents:
            return hitted_contents, self
        return hitted_contents,None

class GoogleTopTen:
    """
        構造体：各サイトの情報、関連キーワードなど検索トップ1画面に関する情報。
    """

    def __init__(self) -> None:
        self.site_list:OneSite = []
        self.related_keyword_list:str = []
    
    def add_site_list(self, site:OneSite) -> None:
        self.site_list.append(site)

    def add_related_keyword(self, related_keyword:str) -> None:
        self.related_keyword_list.append(related_keyword)

    def store_related_keyword(self, related_keyword:list) -> None:
        self.related_keyword_list = related_keyword
    
    def get_as_json(self) -> dict:
        return {"OneSiteList" : self.site_list, "RelatedKeyword" : self.related_keyword_list}
    
    # target_keyword_listは、dictにして{keyword : 100}など重みを設定してもよい。
    def search_keyword(self,target_keyword_list:dict):
        result_json = []
        score = 0
        article_num = len(self.site_list)
        # サイトごとに各単語を検索
        for one_site in self.site_list:
            hitted_word = []
            hit_site_contents_to_keyword = {}       # {"逮捕" : ["title", description], ...}
            for keyword, weight in target_keyword_list.items():
                hitted_contents, hit_site_info = one_site.is_contain_keyword(keyword)
                if hit_site_info:
                    score += weight / article_num
                    hitted_word.append(keyword)
                    hit_site_contents_to_keyword[keyword] = hitted_contents
            if hitted_word:
                result_json.append({"site" : one_site.get_as_json(), "hitted_keyword" : hitted_word, "hit_site_contents_to_keyword" : hit_site_contents_to_keyword})
        return result_json, score

# CSS セレクタのクラスネーム
cssSelectorClassName_item = "Gx5Zad fP1Qef xpd EtOod pkphOe"
cssSelectorClassName_title = "BNeawe vvjwJb AP7Wnd"
cssSelectorClassName_url_structure = "BNeawe UPmit AP7Wnd"
cssSelectorClassName_description = "BNeawe s3v9rd AP7Wnd"
cssSelectorClassName_related_work = "BNeawe s3v9rd AP7Wnd lRVwie"


def getRelatedKeyword(soupAll:BeautifulSoup):
    related_leyword_list = []
    related_work_list_soup = soupAll.find_all("div", class_=cssSelectorClassName_related_work)
    for related_work_soup in related_work_list_soup:
        keyword = related_work_soup.get_text()
        related_leyword_list.append(keyword)
    print(related_leyword_list)
    return related_leyword_list

def googleQueryRequest(search_word:str):
    # 変数
    result_google_top_ten_info:GoogleTopTen = GoogleTopTen()
    pages_num = 10 + 1          # これで10件
    
    # const
    target_url = f'https://www.google.co.jp/search?hl=ja&num={pages_num}&q={search_word}'

    request = requests.get(target_url)
    soup = BeautifulSoup(request.text, "html.parser")
    try:
        item_list = soup.find_all("div", class_=cssSelectorClassName_item) # 項目(タイトル、説明とかを含んだもの)
    except AttributeError:
        print("Error : Google検索に失敗しました。")
        return None
    for item in item_list:
        try:
            title           = item.find("div", class_=cssSelectorClassName_title).get_text()
            url_structure   = item.find("div", class_=cssSelectorClassName_url_structure).get_text()
            description     = item.find("div", class_=cssSelectorClassName_description).get_text()
            url = myUtils.urlGet(item)
        except AttributeError:
            print("Error : Google検索に失敗しました。")
            return None
        one_site_info = OneSite(title,url_structure,description, url)
        result_google_top_ten_info.add_site_list(one_site_info)
    
    # 関連キーワードも取る
    related_keyword = getRelatedKeyword(soup)
    result_google_top_ten_info.store_related_keyword(related_keyword)
    return result_google_top_ten_info

request_limit = 0

def queryIsNotEnded(google_top_result) -> bool:
    global request_limit
    if request_limit >= 5:
        print("Error : Google 検索が上限に達したため、検索失敗しました。")
        request_limit = 0
        return False
    if not google_top_result:
        request_limit += 1
        return True
    request_limit = 0
    return False
    

def googleTop10CheckerConductor(targetPhrase:str, file_name:str = "Keyword.txt"):
    """
        外部からの呼び出しはこちらの関数を使用する。
    """
    weight_to_keyword = fileUtils.getWeightToKeyword(file_name)
    weight_to_keyword = myUtils.normalizeWeightToKeyword(weight_to_keyword) # 追加
    google_top_result = None
    limit = 0
    while queryIsNotEnded(google_top_result):
        if limit >= 1:
            print("Log : Google検索に失敗したので再検索します。")
        if limit >= 5:
            break
        google_top_result = googleQueryRequest(targetPhrase)
        limit += 1
    result_json, score = google_top_result.search_keyword(weight_to_keyword)
    return result_json, score

# テスト
if __name__ == "__main__":
    targetPhrase = "事業家集団"
    targetPhrase = "三菱商事"
    file_name = "Keyword.txt"
    weight_to_keyword = fileUtils.getWeightToKeyword(file_name)
    google_top_result = None
    while queryIsNotEnded(google_top_result):
        google_top_result = googleQueryRequest(targetPhrase)
    result_json, score = google_top_result.search_keyword(weight_to_keyword)