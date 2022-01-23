# DogsRatingAnalysis
Data Analysis project on Tweets for dogs' ratings
This work included access to the Twitter API in order to complete this Data Wrangling student project. I am using Tweepy to query Twitter's API for data included in the 'WeRateDogs' Twitter archive. This data includes retweet count and favorite count. Before I can run my API querying code, I needed to set up my own Twitter developer application. Once I had this set up, I developed some code to create an API object that used to gather Twitter data. After querying each tweet ID listed in 'twitter-archive-enhanced.csv', I wrote its JSON data to a tweet_json.txt file with each tweet's JSON data on its own line. I will then read this file, line by line, to create a pandas DataFrame that I will assess and clean.
<br>
