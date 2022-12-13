import tweepy
import os
import pytz
import requests
import asyncio
from datetime import datetime, time, timedelta
import time
from app.utils import get_binancep2p_rate,format_binance_response_data

iso_code_list = set(("ARS","EUR","USD","AED","AUD","BDT","BHD","BOB","BRL","CAD","CLP","CNY","COP","CRC","CZK","DOP","DZD","EGP","GBP","GEL","GHS","HKD","IDR","INR","JPY","KES","KHR","KRW","KWD","KZT","LAK","LBP","LKR","MAD","MMK","MXN","MYR","NGN","OMR","PAB","PEN","PHP","PKR","PLN","PYG","QAR","RON","RUB","SAR","SDG","SEK","SGD","THB","TND","TRY","TWD","UAH","UGX","UYU","VES","VND","ZAR"))
api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_KEY_SECRET")
bearer_token = r"{0}".format(os.getenv("TWITTER_BEARER_TOKEN"))
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)
now = datetime.now() 
utc=pytz.UTC
endpoint_base = "https://api.streetrates.hng.tech/api/currency/currency/"
client_id=client.get_me().data.id
print(client_id)
start_id = 1
initialisation_resp = client.get_users_mentions(client_id)
if initialisation_resp.data != None:
    start_id = initialisation_resp.data[0].id
while True:
    response = client.get_users_mentions(client_id,since_id=start_id)
    if response.data != None:
        for tweet in response.data:
            try:
                full_text = tweet.text.split(" ")
                if len(full_text) == 1:
                    print("entered one input")
                    client.create_tweet(in_reply_to_tweet_id=tweet.id,text="You mentioned the twitter bot handle without placing an isocode e.g @streetrates ngn")
                    
                elif len(full_text) == 2:
                    print("entered two input")
                    first = full_text[1].upper()
                    url = f"{endpoint_base}{first}"
                    response = requests.get(url)
                    data = response.json()
                    name = data["data"]["name"]
                    if data["success"]:
                        sell = data["data"]["rate"]["parallel_sell"]
                    else:
                        print("request failed")
                    reply=f"One USD to {first} is {sell} {name}"
                    client.create_tweet(in_reply_to_tweet_id=tweet.id,text=reply)
                    
                elif len(full_text) == 3:
                    print("entered three input")
                    from_currency = full_text[1].upper()
                    to_currency = full_text[2].upper()
                    url1 = f"{endpoint_base}{from_currency}"
                    response1 = requests.get(url1)
                    url2 = f"{endpoint_base}{to_currency}"
                    response2 = requests.get(url2)
                    data1 = response1.json()
                    name1 = data["data"]["name"]
                    data2 = response2.json()
                    name2 = data2["data"]["name"]
                    if data1["success"] and data2["success"]:
                        sell1 = data1["data"]["rate"]["parallel_sell"]
                        sell2 = data2["data"]["rate"]["parallel_sell"]
                    else:
                        print("request failed")
                    final_result = round(float(sell2) / float(sell1),3)
                    reply=f"One {from_currency} to {to_currency} is {final_result} {name}"
                    client.create_tweet(in_reply_to_tweet_id=tweet.id,text=reply)
                else:
                    reply = f"Pls enter in the format required"
                    print(reply)
                start_id = tweet.id
            except Exception as error:
                pass
    else:
        print("nothing found")

    time.sleep(14400)


