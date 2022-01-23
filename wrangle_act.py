#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np
import requests
import os
import tweepy
from tweepy import OAuthHandler
import json
from timeit import default_timer as timer
get_ipython().run_line_magic('matplotlib', 'inline')


# # Gather

# In[141]:


# Reading the archive.csv for tweets of @dog_rates into a DataFrame
twt_archv_df = pd.read_csv('twitter-archive-enhanced.csv')


# In[21]:


# Downloading the tweet image predictions programmatically
url = 'https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv'
response = requests.get(url)
with open(url.split('/')[-1], mode = 'wb') as file:
    file.write(response.content)


# In[142]:


# Reading the Image Predictions.tsv-by-a-neural-network into a DataFrame
image_predictions = pd.read_csv('image-predictions.tsv', sep='\t')
image_predictions.head()


# In[9]:


# Query Twitter API for each tweet in the Twitter archive and save JSON in a text file
# These are intentionally hidden (after run) to comply with Twitter's API terms and conditions
consumer_key = 'HIDDEN'
consumer_secret = 'HIDDEN'
access_token = 'HIDDEN'
access_secret = 'HIDDEN'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Tweet IDs for which to gather additional data via Twitter's API
tweet_ids = twt_archv_df.tweet_id.values
len(tweet_ids)

# Query Twitter's API for JSON data for each tweet ID in the Twitter archive
count = 0
fails_dict = {}
start = timer()
# Save each tweet's returned JSON as a new line in a .txt file
with open('tweet_json.txt', 'w') as outfile:
    # This loop took 31.89 minutes to run including Twitter's rate limit
    for tweet_id in tweet_ids:
        count += 1
        # Printing out each tweet ID after it was queried
        print(str(count) + ": " + str(tweet_id))
        try:
            tweet = api.get_status(tweet_id, tweet_mode='extended')
            print("Success")
            json.dump(tweet._json, outfile)
            outfile.write('\n')
        except tweepy.TweepError as e:
            print("Fail")
            fails_dict[tweet_id] = e
            pass
end = timer()
print(end - start)
print(fails_dict)


# 25 out of 2356 fail for the query of Twitter API, and these are maybe because of deleted tweets. So, they are skipped. The rest 2331 shall be processed then.

# In[143]:


# Reading the json.txt file for the tweets data
tweets_list = []

with open('tweet_json.txt', encoding='utf-8') as file:
    for line in file:
        tweets_list.append(json.loads(line))
        
tweets_df = pd.DataFrame(tweets_list)

#user_list = pd.Series(tweets_df.user).tolist()
#user_df = pd.DataFrame(user_list)
# All user_df refer to the same user which is dog_rates. So, it is skipped

#place_list = pd.Series(tweets_df.place).tolist()
#place_df = pd.DataFrame(place_list)
# Just one entry for the 'place' attribute in the whole tweets_df; in Clifton, NJ, US. So, it is skipped


# In[144]:


# As per the key point wanting original ratings (no retweets) that have images
id_ls1 = tweets_df.id
id_ls2 = image_predictions.tweet_id
id_ls3 = twt_archv_df.tweet_id
tweets_df = tweets_df[tweets_df['id'].isin(set(id_ls1)&set(id_ls2))]
tweets_df = tweets_df[~(tweets_df.retweeted_status.notnull())]
id_ls1 = tweets_df.id
twt_archv_df = twt_archv_df[twt_archv_df['tweet_id'].isin(set(id_ls1)&set(id_ls3))]
image_predictions = image_predictions[image_predictions['tweet_id'].isin(set(id_ls1)&set(id_ls2))]


# # Assess
# ## Quality
# - TimeStamp is of the wrong data type.
# - IDs are of the wrong datatypes.
# - Some have multi dog stage!
# - One has a wrong rating of 1/2
# - A tweet with 2 dogs and no names for neither, however, the name attribute is not None
# - 'contributors', 'coordinates', 'geo', 'place' and 'retweeted' attributes are almost all NaN's through the tweets_df
# - Unnecessary columns in tweets from API include 'user'> same user, 'favorited' and 'truncated' > all false.
# - 25 tweets have been deleted from Twitter API, thus these from the Archive do not have 'retweet_count' nor 'favorite_count'
# - IDs of tweets sometimes called 'id' while others called 'tweet_id'
# - Fake rating of id:810984652412424192 as 24/7
# 
# ## Tidiness
# - Dog stags: doggo, floofer, pupper	and puppo columns in the Archive violates the 1st rule of tidiness.
# - 'retweet_count' and 'favorite_count' in the tweets_df refer to the data in the Archive DataFrame, violating the 3rd rule of tidiness
# - Image predictions data frame also is a data related to the ones in the Archive and the API.

# # Clean
# ## Code

# In[217]:


# Reading copied dataFrame
twt_archv_filt = twt_archv_df.copy()
img_pred_filt = image_predictions.copy()
twt_api_filt = tweets_df.copy()


# In[218]:


twt_api_filt = twt_api_filt.loc[:,['favorite_count','id','retweet_count']]
twt_archv_filt.drop(columns=['source','retweeted_status_id','retweeted_status_user_id','retweeted_status_timestamp'], inplace=True)
twt_archv_filt.timestamp = pd.to_datetime(twt_archv_filt.timestamp)


# In[219]:


# Figuiring out 11 duplicated DogStages as
twt_archv_filt[(twt_archv_filt.doggo=='doggo')&(twt_archv_filt.pupper=='pupper')]
twt_archv_filt[(twt_archv_filt.doggo=='doggo')&(twt_archv_filt.floofer=='floofer')]
twt_archv_filt[(twt_archv_filt.doggo=='doggo')&(twt_archv_filt.puppo=='puppo')]
# Cleaning
twt_archv_filt.loc[twt_archv_filt.tweet_id==855851453814013952,'doggo'] = 'None'
twt_archv_filt.loc[twt_archv_filt.tweet_id==854010172552949760,'doggo'] = 'None'
twt_archv_filt.loc[twt_archv_filt.tweet_id==817777686764523521,'doggo'] = 'None'
twt_archv_filt.loc[twt_archv_filt.tweet_id==808106460588765185,['doggo','pupper']] = 'None' # more than one dog
twt_archv_filt.loc[twt_archv_filt.tweet_id==802265048156610565,['doggo','pupper']] = 'None' # more than one dog
twt_archv_filt.loc[twt_archv_filt.tweet_id==801115127852503040,'doggo'] = 'None'
twt_archv_filt.loc[twt_archv_filt.tweet_id==785639753186217984,['doggo','pupper']] = 'None' # Not a dog 
twt_archv_filt.loc[twt_archv_filt.tweet_id==759793422261743616,['doggo','pupper']] = 'None' # more than one dog
twt_archv_filt.loc[twt_archv_filt.tweet_id==751583847268179968,'pupper'] = 'None'
twt_archv_filt.loc[twt_archv_filt.tweet_id==741067306818797568,['doggo','pupper']] = 'None' # more than one dog
twt_archv_filt.loc[twt_archv_filt.tweet_id==741067306818797568,'name'] = 'None' # A tweet with 2 dogs and no names
twt_archv_filt.loc[twt_archv_filt.tweet_id==733109485275860992,['doggo','pupper']] = 'None' # more than one dog


# In[220]:


twt_archv_filt.loc[(twt_archv_filt.doggo==twt_archv_filt.floofer)&
                   (twt_archv_filt.pupper==twt_archv_filt.puppo), 'doggo'] = 'not_doggo'
twt_archv_filt = pd.melt(twt_archv_filt, id_vars=['tweet_id', 'in_reply_to_status_id', 'in_reply_to_user_id', 'timestamp',
                                                  'text', 'expanded_urls', 'rating_numerator', 'rating_denominator', 'name'],
                         var_name='tmp_stage', value_name='dog_stage')
twt_archv_filt = twt_archv_filt[twt_archv_filt.dog_stage != 'None']
twt_archv_filt['dog_stage'].replace('not_doggo',np.nan, inplace=True)
twt_archv_filt.drop(columns=['tmp_stage'], inplace=True)
twt_archv_filt.reset_index(drop=True, inplace=True)


# In[249]:


twt_archv_filt.loc[:,['tweet_id','in_reply_to_status_id','in_reply_to_user_id']] = twt_archv_filt.astype({
    'tweet_id':str,'in_reply_to_status_id':str,'in_reply_to_user_id':str})
twt_archv_filt.in_reply_to_status_id.replace('nan',np.nan, inplace=True)
twt_archv_filt.in_reply_to_user_id.replace('nan',np.nan, inplace=True)
twt_api_filt.loc[:,['id']] = twt_api_filt.astype({'id':str})
img_pred_filt.loc[:,['tweet_id']] = img_pred_filt.astype({'tweet_id':str})


# In[256]:


# Testing
twt_archv_filt.info()
twt_api_filt.info()
img_pred_filt.info()


# In[252]:


twt_archv_filt.loc[twt_archv_filt.rating_numerator==1,'rating_numerator'] = 9
twt_archv_filt.loc[twt_archv_filt.rating_denominator==2,'rating_denominator'] = 10
twt_api_filt.rename(columns={'id':'tweet_id'}, inplace=True)


# In[257]:


# Making our data Tidy
frst_mrg = pd.merge(twt_archv_filt, twt_api_filt, on='tweet_id')
scnd_mrg = pd.merge(frst_mrg, img_pred_filt, on='tweet_id')
# Now we can solve last quality issue, by deleting the whole row of the fake rating
scnd_mrg.drop(index=345,inplace=True)


# In[258]:


# Test
scnd_mrg.info()


# In[259]:


scnd_mrg.to_csv('twitter_archive_master.csv', index=False)


# # Analysis

# In[4]:


twt_archv_mstr = pd.read_csv('twitter_archive_master.csv')
twt_archv_mstr.sample(5)


# In[5]:


twt_archv_mstr.loc[:,['tweet_id','in_reply_to_status_id','in_reply_to_user_id']] = twt_archv_mstr.astype({
    'tweet_id':str,'in_reply_to_status_id':str,'in_reply_to_user_id':str})
# For simplicity of analysis, only needed rows would be displayed
twt_archv_mstr = twt_archv_mstr.iloc[:,np.r_[0:4,6:12,14:23]]


# In[6]:


twt_archv_mstr.describe()


# In[7]:


twt_archv_mstr[twt_archv_mstr.rating_numerator==0]
twt_archv_mstr[twt_archv_mstr.rating_numerator==1776]
max_idx = twt_archv_mstr[twt_archv_mstr['rating_numerator']==1776].index
twt_archv_mstr[twt_archv_mstr.rating_numerator==max(twt_archv_mstr['rating_numerator'].drop(max_idx))].index
twt_archv_mstr[twt_archv_mstr.rating_numerator==max(twt_archv_mstr['rating_numerator'].drop([1474,649]))]


# Through the entire set of WeRateDogs tweets, only 2 times where they gave nothing (0/10) for nothing also (no dogs). As, one for criticizing a plagiarism of a similar page, and another for disappointing about no dogs are in the near.
# 
# In the same set, max ratings have been given to #1st 'Atticus' received 1776/10 wearing America flag as well as the USA flag in the background. While the #2nd 'Calvin Cordozar' or 'Dogg' received 420/10 although being a rapper person. But a set of dogs received the third place of ratings 204 even from 170.

# In[16]:


twt_archv_mstr[twt_archv_mstr.favorite_count==70]
twt_archv_mstr[twt_archv_mstr.favorite_count==153185]
twt_archv_mstr[twt_archv_mstr.retweet_count==11]
twt_archv_mstr[twt_archv_mstr.retweet_count==75908]


# For the favorite count; a dog with its twins received the lowest favorites of 70 while, a dog swims in a pool receives the highest favorites of 153185.
# 
# For the retweet count; the same dog with its twins received the lowest favorites count, received also the lowest retweets of only 11. But the highest retweets of 75908 goes again for the swimmer dog in the pool with the highest favorites.

# In[134]:


mean_stage = twt_archv_mstr.loc[twt_archv_mstr.dog_stage.notnull()].groupby(['dog_stage'],
                                                               as_index=False)['favorite_count','retweet_count'].mean()
print(mean_stage)
mean_stage.rename(index=mean_stage['dog_stage'], inplace=True)
mean_stage.plot(x='dog_stage',y=['favorite_count','retweet_count'],subplots=True,kind='Pie', figsize=(15,7));


# It appears from the above analysis that doggo dogs (elderly ones) are more popular as the Puppo ones (small ones).

# In[55]:


max_pred = twt_archv_mstr.groupby(['p1'], as_index=False)['favorite_count','retweet_count'].sum().sort_values(
    'favorite_count', ascending=False)
max_pred


# In[73]:


max_pred.iloc[:13,:].plot('p1','favorite_count', kind='bar',figsize=(15,15),title='Dog breeds favorites reactions',
                          legend=False, fontsize=17);

