import json
import urllib.request
import logging
import os
import boto3
import time

import conductor

#ユーザ設定を保存するデータベース
table = boto3.resource('dynamodb').Table('User_setting')

#環境変数からLINEBotのチャンネルアクセストークンを読み込む
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

#ログ関係
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#メッセージ関係
json_open = open('input_ask_buble.json', 'r')
input_ask_buble = json.load(json_open)

json_open = open('result_ask_buble.json', 'r')
result_ask_buble = json.load(json_open)

json_open = open('result_only_score.json', 'r')
result_only_score = json.load(json_open)

json_open = open('result_detail.json', 'r')
result_detail = json.load(json_open)

input_save_text = {
    "type": "text",
    "text": "入力設定を保存しました"
}

result_save_text = {
    "type": "text",
    "text": "結果設定を保存しました"
}

setting_text = {
    "type": "text",
    "text": "設定はリッチメニューからいつでも変更できます"
}

accept_text = {
    "type": "text",
    "text": "判定したいキーワード・文章を送信してください"
}

wait_text = {
    "type": "text",
    "text": "...判定中です..."
}

input_ask_message = [
    input_ask_buble
]

input_save_message = [
    input_save_text,
    result_ask_buble
]

result_save_message = [
    result_save_text,
    setting_text,
    accept_text
]

wait_message = [
    wait_text
]

#文章全体のスコア
final_score = False
caution_num = 0

#データベースに登録
def put_data(user_id, input, result):
    table.put_item(
        Item = {
            'user_id': user_id,
            'input': input,
            'result': result
        }
    )
    
#データベースの修正
def modify_data(user_id, input = None, result = None):
    if input is not None:
        option = {
            'Key': {'user_id': user_id},
            'UpdateExpression': 'set #input = :input',
            'ExpressionAttributeNames': {
                '#input': 'input'
            },
            'ExpressionAttributeValues': {
                ':input': input
            }
        }
        table.update_item(**option)
        
    if result is not None:
        option = {
            'Key': {'user_id': user_id},
            'UpdateExpression': 'set #result = :result',
            'ExpressionAttributeNames': {
                '#result': 'result'
            },
            'ExpressionAttributeValues': {
                ':result': result
            }
        }
        table.update_item(**option)
        
#データベースから取得
def get_data(user_id):
    user = table.get_item(
        Key = {
            'user_id': user_id
        }
    )
    return user

#リプライを送る
def send_reply(events, message):
    time.sleep(1)
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + channel_access_token
    }
    data = {
        'replyToken': events['replyToken'],
        'messages': message
    }
    req = urllib.request.Request(url=url, data=json.dumps(data).encode("utf-8"), method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            logger.info(res.read().decode("utf-8"))
    except:
        print("error")

#メッセージを送る
def send_message(events, message):
    time.sleep(1)
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + channel_access_token
    }
    body = {
        'to': events['source']['userId'],
        'messages': message
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), method='POST', headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            logger.info(res.read().decode("utf-8"))
    except:
        print("error")

def send_result_only_score(events, result):
    global final_score
    
    score = 0.0
    try:
        score = result['google_top_10_result']['score']
    except:
        score = 0.0
        
    if score > 0.004:
        final_score = True
        result_only_score['contents']['contents'][0]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/dangerous2.png"
    elif score > 0.001:
        caution_num += 1
        result_only_score['contents']['contents'][0]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/caution2.png"
    else:
        result_only_score['contents']['contents'][0]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/safe2.png"
    result_only_score['contents']['contents'][0]['body']['contents'][2]['contents'][1]['text'] = str(score)
    
    try:
        score = result['google_news_result']['score']
    except:
        score = 0.0
    
    if score > 0.004:
        final_score = True
        result_only_score['contents']['contents'][1]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/dangerous2.png"
    elif score > 0.001:
        caution_num += 1
        result_only_score['contents']['contents'][1]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/caution2.png"
    else:
        result_only_score['contents']['contents'][1]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/safe2.png"
    result_only_score['contents']['contents'][1]['body']['contents'][2]['contents'][1]['text'] = str(score)
    
    result_only_score_message = [
        result_only_score
    ]
    send_message(events, result_only_score_message)

def send_result_detail(events, result):
    global final_score
    global caution_num
    
    score = 0.0
    try:
        score = result['google_top_10_result']['score']
    except:
        score = 0.0
    
    if score > 0.004:
        final_score = True
        result_detail['contents']['contents'][0]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/dangerous2.png"
    elif score > 0.001:
        caution_num += 1
        result_detail['contents']['contents'][0]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/caution2.png"
    else:
        result_detail['contents']['contents'][0]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/safe2.png"
    result_detail['contents']['contents'][0]['body']['contents'][2]['contents'][1]['text'] = str(score)
    
    try:
        score = result['google_news_result']['score']
    except:
        score = 0.0
    
    if score > 0.004:
        final_score = True
        result_detail['contents']['contents'][1]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/dangerous2.png"
    elif score > 0.001:
        caution_num += 1
        result_detail['contents']['contents'][1]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/caution2.png"
    else:
        result_detail['contents']['contents'][1]['hero']['url'] = "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/safe2.png"
    result_detail['contents']['contents'][1]['body']['contents'][2]['contents'][1]['text'] = str(score)
    
    #初期化
    for i in range(3):
        result_detail['contents']['contents'][0]['footer']['contents'][i+2]['contents'][1]['text'] = "なし"
        result_detail['contents']['contents'][1]['footer']['contents'][i+2]['contents'][1]['text'] = "なし"
        result_detail['contents']['contents'][0]['footer']['contents'][i+2]['contents'][1]['action']['uri'] = "https://www.google.com/"
        result_detail['contents']['contents'][1]['footer']['contents'][i+2]['contents'][1]['action']['uri'] = "https://www.google.com/"

    for i in range(min(3, len(result['google_top_10_result']['result']))):
        try:
            result_detail['contents']['contents'][0]['footer']['contents'][i+2]['contents'][1]['text'] = result['google_top_10_result']['result'][i]['site']['title']
            result_detail['contents']['contents'][0]['footer']['contents'][i+2]['contents'][1]['action']['uri'] = result['google_top_10_result']['result'][i]['site']['url']
        except:
            result_detail['contents']['contents'][0]['footer']['contents'][i+2]['contents'][1]['text'] = "なし"
            result_detail['contents']['contents'][0]['footer']['contents'][i+2]['contents'][1]['action']['uri'] = "https://www.google.com/"
    for i in range(min(3, len(result['google_news_result']['result']))):
        try:
            result_detail['contents']['contents'][1]['footer']['contents'][i+2]['contents'][1]['text'] = result['google_news_result']['result'][i]['site']['title']
            result_detail['contents']['contents'][1]['footer']['contents'][i+2]['contents'][1]['action']['uri'] = result['google_news_result']['result'][i]['site']['url']
        except:
            result_detail['contents']['contents'][1]['footer']['contents'][i+2]['contents'][1]['text'] = "なし"
            result_detail['contents']['contents'][1]['footer']['contents'][i+2]['contents'][1]['action']['uri'] = "https://www.google.com/"
    
    result_detail_message = [
        result_detail
    ]
    send_message(events, result_detail_message)

#Lambdaのメインの動作
def lambda_handler(event, context):
    global final_score
    global caution_num
    
    final_score = False
    caution_num = 0
    
    type = json.loads(event["body"])["events"][0]["type"]
    
    #フォロー時
    if type =="follow":
        for events in json.loads(event["body"])["events"]:
            #データベースに登録
            userId = events['source']['userId']
            put_data(userId, 1 ,1)
            
            #初期設定
            #send_reply(events, input_ask_message)
                
    #ポストバック時
    elif type =="postback": 
        for events in json.loads(event["body"])["events"]:
            data = events["postback"]["data"]
            userId = events['source']['userId']
            
            if data.startswith("input"):
                #入力設定の保存
                if data.endswith("0"):
                    modify_data(userId, input = 0)
                elif data.endswith("1"):
                    modify_data(userId, input = 1)
            
                #結果設定の質問
                send_reply(events, input_save_message)
            
            elif data.startswith("result"):
                #結果設定の保存
                if data.endswith("0"):
                    modify_data(userId, result = 0)
                elif data.endswith("1"):
                    modify_data(userId, result = 1)
            
                #設定完了メッセージ
                send_reply(events, result_save_message)
    
    #メッセージを受け取った場合
    elif type == "message": 
        for events in json.loads(event["body"])["events"]:
            userText = events['message']['text']
            userId = events['source']['userId']
            
            #リッチメニューから設定を変更
            if userText == "設定変更":
                send_reply(events, input_ask_message)
            
            else:
                #analyzer作成
                analyzer = conductor.analyzeConductor()
                
                #判定中メッセージ
                send_reply(events, wait_message)
                
                #結果設定
                only_score_flg = False
                userInfo = get_data(userId)
                if int(userInfo["Item"]["result"]) == 0:
                    only_score_flg = True
                
                #判定を行う
                result = None
                if int(userInfo["Item"]["input"]) == 0:
                    result = analyzer.singleQueryAndAnalyzeForSpecificPhrase(userText, is_only_score=only_score_flg)
                else:
                    result = analyzer.InTheCaseOfUsertextParse(userText, is_only_score=only_score_flg)
                
                #結果出力
                if int(userInfo["Item"]["input"]) == 0:
                    if int(userInfo["Item"]["result"]) == 0:
                        send_result_only_score(events, result)
                    else:
                        send_result_detail(events, result)
                else:
                    if int(userInfo["Item"]["result"]) == 0:
                        for keyword in result:
                            text = "キーワード「" + keyword['result']['keyword'] + "」の危険度"
                            tmp_message = [{
                                "type": "text",
                                "text": text
                            }]
                            send_message(events, tmp_message)
                            send_result_only_score(events, keyword['result'])
                            time.sleep(1)
                    else:
                        for keyword in result:
                            text = "キーワード「" + keyword['result']['keyword'] + "」の危険度"
                            tmp_message = [{
                                "type": "text",
                                "text": text
                            }]
                            send_message(events, tmp_message)
                            send_result_detail(events, keyword['result'])
                            time.sleep(1)
                    
                    tmp_message = [{
                                "type": "text",
                                "text": "...判定結果！！"
                            }]
                    send_message(events, tmp_message)
                    
                    if caution_num > len(result) * 2 * 0.3:
                        final_score = True
                    
                    if final_score == True:
                        tmp_img = [{
                          "type": "image",
                          "originalContentUrl": "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/dangerous_cat.png",
                          "previewImageUrl": "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/dangerous_cat.png"
                        }]
                        send_message(events, tmp_img)
                    else:
                        tmp_img = [{
                          "type": "image",
                          "originalContentUrl": "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/safe_cat.png",
                          "previewImageUrl": "https://mws-line-bot-image.s3.ap-northeast-1.amazonaws.com/safe_cat.png"
                        }]
                        send_message(events, tmp_img)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    