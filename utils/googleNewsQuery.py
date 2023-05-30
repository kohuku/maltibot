from time import sleep
import requests
from bs4 import BeautifulSoup
from utils import fileUtils,myUtils
import re
import urllib.parse


class NewsData:
    def __init__(self, title:str, publicier:str, contents:str, url:str):
        self.title      = title
        self.publicier  = publicier
        self.contents   = contents
        self.url = url
    
    def get_as_json(self):
        return {"title": self.title, "publicier" : self.publicier,
         "contents" : self.contents, "url" : self.url}

    def is_contain_keyword(self, target_word:str):
        """
            return :
                hitted_contents : 該当要素名
                Any             : 該当していれば自身
        """
        hitted_contents = []
        if target_word in self.title:
            hitted_contents.append("title")
        if target_word in self.publicier:
            hitted_contents.append("publicier")
        if target_word in self.contents:
            hitted_contents.append("contents")
        if hitted_contents:
            return hitted_contents, self
        return hitted_contents,None

class NewsDataSet:

    def __init__(self) -> None:
        self.newsdata_list:NewsData = []
        self.publiciers:str = []
    
    def add_newsdata_list(self, a_news_data:NewsData) -> None:
        self.newsdata_list.append(a_news_data)
    
    def add_publiciers(self, publicier:str) -> None:
        self.publiciers.append(publicier)

    def get_as_json(self) -> dict:
        return {"NewsdataList" : self.newsdata_list, "Publiciers" : self.publiciers}

    def search_keyword(self,target_keyword_list:dict):
        result_json = []
        score = 0
        # max = 0
        article_num = len(self.newsdata_list)
        for one_news in self.newsdata_list:
            hitted_word = []
            hit_news_contents_to_keyword = {}
            for keyword, weight in target_keyword_list.items():
                # max += weight/100 * 1
                hitted_contents, hit_site_info = one_news.is_contain_keyword(keyword)
                if hit_site_info:
                    score += weight / article_num
                    # print(weight / article_num)
                    hitted_word.append(keyword)
                    hit_news_contents_to_keyword[keyword] = hitted_contents
            if hitted_word:
                result_json.append({"site" : one_news.get_as_json(), "hitted_keyword" : hitted_word, "hit_news_contents_to_keyword" : hit_news_contents_to_keyword})
        return result_json, score

# def hrefStrGetterFromHrefTag(soupText:BeautifulSoup):
#     return str(soupText.select("a")[0].get('href'))

# def HrefToURL(hrefText:str):
#     return hrefText.strip("/url?q=").split(r"&sa=U")[0]

# def getLinkList(parsedTextATagList:list):
#     articleURLList = []
#     for an_a_tag in parsedTextATagList:
#         a_href_tag = hrefStrGetterFromHrefTag(an_a_tag)
#         if a_href_tag.startswith("/url?q="):
#             a_url = HrefToURL(a_href_tag)
#             articleURLList.append(a_url)
#     # print(articleURLList)           # URL リスト
#     # print(len(articleURLList))      # 長さ
#     return articleURLList

# def getATag(soup:BeautifulSoup):
#     return soup.select('div.Gx5Zad')


# CSS セレクタのクラスネーム
cssSelectorClassName_item = "Gx5Zad fP1Qef xpd EtOod pkphOe"
cssSelectorClassName_title = "BNeawe vvjwJb AP7Wnd"
cssSelectorClassName_publicier = "BNeawe UPmit AP7Wnd"
cssSelectorClassName_contents = "BNeawe s3v9rd AP7Wnd"
# cssSelectorClassName_related_work = "BNeawe s3v9rd AP7Wnd lRVwie"


def googleNewsQueryRequest(search_word:str):

    # setting
    pages_num = 10 + 1
    result_google_news_top_ten_info:NewsDataSet = NewsDataSet()
    target_url = f'https://www.google.co.jp/search?hl=ja&num={pages_num}&q={search_word}&tbm=nws' # ニュースの際はこちらを使用
    
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
            publicier       = item.find("div", class_=cssSelectorClassName_publicier).get_text()
            contents        = item.find("div", class_=cssSelectorClassName_contents).get_text()
            url = myUtils.urlGet(item)
        except AttributeError:
            print("Error : Google検索に失敗しました。")
            return None
        a_news_article = NewsData(title,publicier,contents, url)
        result_google_news_top_ten_info.add_newsdata_list(a_news_article)
    
    return result_google_news_top_ten_info

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

def googleNewsCheckerConductor(targetPhrase:str, file_name:str = "Keyword.txt"):
    """
        外部からの呼び出しはこちらの関数を使用する。
    """
    weight_to_keyword = fileUtils.getWeightToKeyword(file_name)
    weight_to_keyword = myUtils.normalizeWeightToKeyword(weight_to_keyword) # 追加
    new_data_result = None
    limit = 0 # 汚いけど念のため
    while queryIsNotEnded(new_data_result):
        if limit >= 1:
            print("Log : Google検索に失敗したので再検索します。")
        if limit >= 5:
            break
        new_data_result = googleNewsQueryRequest(targetPhrase)
        limit += 1
    result_json, score = new_data_result.search_keyword(weight_to_keyword)
    return result_json, score
    
# テスト
if __name__ == "__main__":
    targetPhrase = "三菱商事"
    targetPhrase = "事業家集団"
    file_name = "Keyword.txt"
    weight_to_keyword = fileUtils.getWeightToKeyword(file_name)
    new_data_result = None
    while queryIsNotEnded(new_data_result):
        new_data_result = googleNewsQueryRequest(targetPhrase)
    result_json, score = new_data_result.search_keyword(weight_to_keyword)