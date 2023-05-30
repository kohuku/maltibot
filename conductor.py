import utils.googleNewsQuery as GoogleNewsQ
import utils.googleTopPageQuery as GoogleTopPageQ
import utils.yahooKeyPhraseExtraction as YahooPhraseE
import json

class analyzeConductor:
    """
        このクラスは状態を持たない。
        →アノテーションで
        文章の処理:
            yahooのAPIに投げてキーワードを抽出する。
            キーワードの上位5つをgoogleの2つのAPIに投げ直して、分析を行い、
            分析結果をまとめて返す。
            [{"キーワード" : , "Top10Info" : , "googleNewsInfo" : },...]
        キーワード(会社名や暗号資産名...etc)の処理:
            キーワードをgoogleの2つのAPIに投げ直して、分析を行い、
            分析結果をまとめて返す。
            {"キーワード" : , "Top10Info" : , "googleNewsInfo" : }
        
        インスタンス時引数:
            is_only_score : スコアだけか、説明も加えるかを設定します。
                スコアだけの場合→True
                スコア+説明場合→False
    """

    def __init__(self) -> None:
        self.yahooAPI = YahooPhraseE.YahooRequestProxy()
        self.filename = "./utils/Keyword.txt"

    def singleQueryAndAnalyze(self, userSpecificPhrase:str,is_only_score:bool= False):
        NewsResult,scoreByNews = GoogleNewsQ.googleNewsCheckerConductor(userSpecificPhrase,self.filename)
        TopPageResult,scoreByTopPage = GoogleTopPageQ.googleTop10CheckerConductor(userSpecificPhrase,self.filename)
        if is_only_score:
            return {"keyword" : userSpecificPhrase, "google_top_10_result" : {"score" : scoreByNews},
            "google_news_result" : {"score" : scoreByTopPage}}
        return {"keyword" : userSpecificPhrase, "google_top_10_result" : {"result" : NewsResult, "score" : scoreByNews},
            "google_news_result" : {"result" : TopPageResult, "score" : scoreByTopPage}}

    def singleQueryAndAnalyzeForSpecificPhrase(self, userSpecificPhrase:str, is_only_score:bool = False ):
        """
            追記：メソッド単位でscore or 詳細を選択できるようにしました。
        """
        NewsResult,scoreByNews = GoogleNewsQ.googleNewsCheckerConductor(userSpecificPhrase, self.filename)
        TopPageResult,scoreByTopPage = GoogleTopPageQ.googleTop10CheckerConductor(userSpecificPhrase, self.filename)
        if is_only_score:
            return {"specific_keyword" : userSpecificPhrase, "google_top_10_result" : {"score" : scoreByNews},
            "google_news_result" : {"score" : scoreByTopPage}}
        return {"specific_keyword" : userSpecificPhrase, "google_top_10_result" : {"result" : NewsResult, "score" : scoreByNews},
            "google_news_result" : {"result" : TopPageResult, "score" : scoreByTopPage}}

    def multiQueryAndAnalyze(self, userSpecificPhrase:list):
        allResult = []
        for aPhrase in userSpecificPhrase:
            allResult.append(self.singleQueryAndAnalyze(aPhrase))
        return allResult

    def InTheCaseOfUsertextParse(self, usertext:str, keyword_max:int = 3, is_only_score:bool= False):
        resultAll = []
        yahoo_keyphrase_extraction_result = self.yahooAPI.requestKeyPhrase(usertext)
        yahoo_keyphrase_extraction_result_dict = json.loads(yahoo_keyphrase_extraction_result)
        prase_list = yahoo_keyphrase_extraction_result_dict["result"]["phrases"]
        
        indexnum = 0
        for content in prase_list:
            if indexnum == keyword_max:
                break
            score = content["score"]
            text = content["text"]
            resultDict = self.singleQueryAndAnalyze(text, is_only_score)
            resultAll.append({"keyword_score" : score, "result" : resultDict})
            indexnum += 1 # ここを追加
        return resultAll
    
    # これでjsondumpできる。
    def jsonDump(self, dict_:dict):
        return json.dumps(dict_)

if __name__ == "__main__":
    # 文章について
    conductor = analyzeConductor()
    # userText = "これからまだまだ、上がるから絶対に良いと思うよ\n下回る事も有るし、逆に2倍3倍～10倍になる事も有るよ！\nでも下回る月も有るけど、使わずに溜めてもらってて、最終的に上がれば全てがプラスなるよ\n2.3年後は確実に上がるよ" # lineであった事例
    
    # userText = "事業家集団には気を付けよう！"
    # result = conductor.InTheCaseOfUsertextParse(userText)
    # print(result)
    # print("="*100)
    # try:
    #     url_0 = result[0]["result"]["google_top_10_result"]["result"][0]["site"]["url"]
    #     url_1 = result[0]["result"]["google_top_10_result"]["result"][0]["site"]["url"]
    # except:
    #     url_0 = "Query failed."
    #     url_1 = "Query failed."
    # print(url_0) # url アクセス
    # print(url_1) # url アクセス

    # print("="*100)

    # キーワードについて
    keyword = "事業家集団"
    result = conductor.singleQueryAndAnalyzeForSpecificPhrase(keyword, is_only_score=False)
    print("="*100)
    print(result)
    print("="*100)
    sites = result["google_top_10_result"]["result"]
    # print(len(sites))
    for site in sites:
        try:
            url = site["site"]
        except:
            url = "Query failed."
        # print(url)
    # 出力形式の保存
    with open('./test.json', 'w', encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)