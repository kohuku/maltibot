import json
from urllib import request

class YahooRequestProxy:

    APPID = "????????????????????????????????????????????????????????"  # アプリケーションID
    URL = "https://jlp.yahooapis.jp/KeyphraseService/V2/extract"        # APIのリクエストURL

    def __init__(self):
        self.APIKeyGetter()
        
    def APIKeyGetter(self):
        with open("./utils/APIKey.txt") as api_key_file_f:
            self.APPID = api_key_file_f.read()

    def post(self, query):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Yahoo AppID: {}".format(self.APPID),
        }
        param_dic = {
          "id": "1234-1",
          "jsonrpc" : "2.0",
          "method" : "jlp.keyphraseservice.extract",
          "params" : {
            "q" : query
          }
        }
        params = json.dumps(param_dic).encode()
        req = request.Request(self.URL, params, headers)
        with request.urlopen(req) as res:
            body = res.read()
        return body.decode()

    def requestKeyPhrase(self, post_text):
        response = self.post(post_text)
        return response

if __name__ == "__main__":
    test_txt = "私は～大学の学生です。私はテストしています。"        # ユーザーから送られてくる。
    yahoo_request_proxy = YahooRequestProxy()                       # このように使う。
    result = yahoo_request_proxy.requestKeyPhrase(post_text=test_txt)
    print(result)