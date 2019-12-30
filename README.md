# BitMex Trader Sentiment Bot

A web app that executes a Python script that calculates current sentiment of traders on BitMex. Trader sentiment is posted to the chatbox once every 4 minutes and a complete summary is posted once every hour. Script makes use of BitMex API for chatbox data and chatbox access. Sentiment is judged and calculated via certain key words and makes use of the NLP library, TextBlob for more accurate results. The reason why the web app was needed was so the script can run for as long as possible. Currently hosted on http://bitmexbot.us-east-2.elasticbeanstalk.com/
