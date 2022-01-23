# DogsRatingAnalysis
Data Analysis project on Tweets for dogs' ratings.<br>
This work included access to the Twitter API in order to complete this Data Wrangling student project. I am using _Tweepy_ (Python library) to query Twitter's API for data included in the _'WeRateDogs'_ Twitter archive. This data includes retweet count and favorite count. Before I can run my API querying code, I needed to set up my own Twitter Developer Account application. Once I had this set up, I developed some code to create an API object that used to gather Twitter data. After querying each tweet ID listed in _twitter-archive-enhanced.csv_, I wrote its JSON data to a *tweet_json.txt* file with each tweet's JSON data on its own line. I then read this file - line by line - to create a pandas DataFrame that I have then assessed for quality and tideness issues, and cleaned.
