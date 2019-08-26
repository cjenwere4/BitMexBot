import requests as req
import threading
import array
import time
import hashlib
import hmac
from json import dumps
from urllib.parse import urlparse
from textblob import TextBlob
import timeinterval

dataArray = [0, 0, 0, 0, ""]
functionCallCount = 0

def sendChat(dataArray): 
    apiKey = 'DDx3EzxuME0HSx4_djyLB7ep'
    apiSecret = 'cMwoVdj8rWEIEpjVH2kLVLx_07nKc5r6bqt8Xk_qNTfRAHqg'
    verb = 'POST'
    path = '/api/v1/chat'
    expires = 1598374259 # 8/25/2020
    msg = dataArray[4]
    dict = {
        "message": msg,
        "channelID": 1
    }
    data = dumps(dict)
    signature = generate_signature(apiSecret, verb, path, expires, data)
    #print("\nsig:", signature)
    url = 'https://testnet.bitmex.com/api/v1/chat'
    headers = {
                'content-type': 'application/json',
                'api-expires' : '1598374259',
                'api-key': apiKey,
                'api-signature': signature
    }
    r = req.post(url = url, data=data, headers = headers)
    print(r)

def getChats(dataArray, functionCallCount):
    goodSentiment = 0
    badSentiment = 0
    noRekts = 0
    msgID = 0
    sentimentPts = 0
    # api-endpoint 
    URL = "https://www.bitmex.com/api/v1/chat?count=100&reverse=true&channelID=1"
    # sending get request and saving the response as response object 
    chats = req.get(url = URL) 
    # extracting data in json format
    count = 0
    usefulInfo = 0
    while (count < 100):
        data = chats.json()
        try:
            chatmessage = data[count]['message']
            chatmessageID = data[count]['id']
            blob = TextBlob(chatmessage)
            sentiment = blob.sentiment
            if (sentiment[0] != 0): 
                usefulInfo += 1
                sentimentPts += sentiment[0]
            if (data[count]['user'] == "REKT"):
               noRekts += 1
            if(sentiment[0] > 0):
                goodSentiment += 1
            elif(sentiment[0] < 0):
                badSentiment += 1
            # so the data won't repeat it's self you need to break out of loop
            if(chatmessageID == dataArray[3]):
                print("Messages from here and up have already been analyzed.")
                count += 100 #break
                
            msgID = chatmessageID
        except UnicodeEncodeError as probEmoji: 
            print("EMOJI CHAR :(")

        count+=1
    
    sentimentAvg = 1 + round(sentimentPts/usefulInfo, 3)
    updateMsg = ""
    dataArray[0] += goodSentiment
    dataArray[1] += badSentiment
    dataArray[2] += noRekts
    dataArray[3] = msgID #probably convert this to message id
    
    if (functionCallCount % 14 == 0 and functionCallCount != 0):
        traderSentimentSummary = "" # this will send every hour
        updateMsg = "Information collected in the last hour: \n" + "No. of REKTs: " + str(noRekts) + "\nNo. of bullish messages: " + str(dataArray[0]) + "\nNo. of bearish messages: " + str(dataArray[1]) + "\nCurrent trader sentiment: " + str(sentimentAvg)
        # reset for new hourly stats
        dataArray[0] = 0
        dataArray[1] = 0
        dataArray[2] = 0
    else:
        updateMsg = "Current Trader Sentiment on BitMex: " + str(sentimentAvg) # this will send every 3 minutes
        if (sentimentAvg < .75):
            sentimentMsg = " (Bearish). (Next update in 5 minutes)."
            updateMsg = updateMsg + sentimentMsg
        elif (sentimentAvg >= .75 and sentimentAvg < 1.25):
            sentimentMsg = " (Neutral). (Next update in 5 minutes)."
            updateMsg = updateMsg + sentimentMsg
        elif (sentimentAvg >= 1.25 and sentimentAvg < 1.45):
            sentimentMsg = " (Bullish). (Next update in 5 minutes)."
            updateMsg = updateMsg + sentimentMsg
        else:
            sentimentMsg = " Bitcoin to 100k EOY! (Next update in 4 minutes)."
            updateMsg = updateMsg + sentimentMsg
        
    
    dataArray[4] = updateMsg
    sendChat(dataArray)
    functionCallCount += 1
    

# Generates an API signature.
# A signature is HMAC_SHA256(secret, verb + path + expires + data), hex encoded.
# Verb must be uppercased, url is relative, expires must be unix timestamp (in seconds)
# and the data, if present, must be JSON without whitespace between keys.
def generate_signature(secret, verb, url, expires, data):
    """Generate a request signature compatible with BitMEX."""
    # Parse the url so we can remove the base and extract just the path.
    parsedURL = urlparse(url)
    path = parsedURL.path
    if parsedURL.query:
        path = path + '?' + parsedURL.query

    if isinstance(data, (bytes, bytearray)):
        data = data.decode('utf8')
    
    message = verb + path + str(expires) + data

    signature = hmac.new(bytes(secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
    return signature

def do_every(period,f,*args):
    def g_tick():
        t = time.time()
        count = 0
        while True:
            count += 1
            yield max(t + count*period - time.time(),0)
    g = g_tick()
    while True:
        time.sleep(next(g))
        f(*args)

getChats(dataArray, functionCallCount) # intial count 
do_every(240, getChats, dataArray, functionCallCount) # set interval every 4 minutes
