import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
from tweepy import Cursor
from tweepy import API
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## You can get these details from the Twitter Developers page
access_token = 'YOUR_ACCESS_TOKEN'
access_token_secret = 'YOUR_ACCESS_TOKEN_SECRET'
consumer_key = 'CONSUMER_KEY'
consumer_secret = 'CONSUMER_KEY_SECRET'

#### TWITTER CLIENT####

class TwitterClient():
	def __init__(self,twitter_user=None):
		self.auth = TwitterAuthenticator().authenticate_twitter()
		self.twitter_client = API(self.auth)
		self.twitter_user = twitter_user

    ## Getting Twitter client
	def get_twitter_client_api(self):    
		return self.twitter_client

    ## Getting the latest tweet of any account
	def get_user_timeline_tweets(self,num_tweets):
		tweets = []
		for tweet in Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
			tweets.append(tweet)
		return tweets

    ## Getting the List of Friends
	def get_friend_list(self,num_friends):
		friends=[]
		for friend in Cursor(self.twitter_client.friends,id=self.twitter_user).items(num_friends):
			friends.append(friend)
		return friends

    ##Getting the tweets of your Home Page
	def get_home_timeline_tweets(self,num_tweets):
		tweets = []
		for tweet in Cursor(self.twitter_client.home_timeline,id=self.twitter_user).items(num_tweets):
			tweets.append(tweet)
		return tweets

##Twitter Authenticator
class TwitterAuthenticator():
	def authenticate_twitter(self):
		auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
		auth.set_access_token(access_token,access_token_secret)
		return auth

class TwitterStreamer():

	#Class for streaming and processing live tweets

	def __init__(self):
		self.twitter_authenticator = TwitterAuthenticator()
	def stream_tweets(self,fetched_tweets_filename,hash_tag_list):
		listener = TwitterListener(fetched_tweets_filename)
		
		auth = self.twitter_authenticator.authenticate_twitter()
		stream = Stream(auth,listener)
		stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):
	# This is just a tweet to print the received tweets in stdout.

	def __init__(self,fetched_tweets_filename):
		self.fetched_tweets_filename = fetched_tweets_filename

	def on_data(self,data):
		try:
			print(data)
			with open(self.fetched_tweets_filename,'a') as f:
				f.write(data)

			return True

		except BaseException as e:
			print("Error on data: %s" %str(e))
			return True

	def on_error(self,status):
		## In case rate limit is exceeded
		if status==420:
			return False

		print(status)

class TweetAnalyzer():
	#Functionality of Analyzing and Categorizing content from tweets
	def tweets_to_dataframe(self,tweets):
		# DataFrame created
		df = pd.DataFrame(data=[tweet.text for tweet in tweets],columns=['Tweets'])
		# Created a new column 'id' to get the ID  of each tweet
		df['id'] = np.array([tweet.id for tweet in tweets])
		# Created a new column 'date' to get the date on which the tweet was created
		df['date'] = np.array([tweet.created_at for tweet in tweets])
		# Created a new column 'len' to get the length  of each tweet
		df['len'] = np.array([len(tweet.text) for tweet in tweets])
		# Created a new column 'likes' to get the number of likes  of each tweet
		df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
		# Created a new column 'retweet_count' to get the number of retweets of each tweet
		df['retweet_count'] = np.array([tweet.retweet_count for tweet in tweets])

		return df

if __name__ == '__main__':
	twitter_client = TwitterClient()
	api = twitter_client.get_twitter_client_api()
	## Screen_name is User name in Twitter Profile and count is the number of latest tweets
	tweets = api.user_timeline(screen_name='MoHFW_INDIA',count=20)   #

	tweet_analyzer = TweetAnalyzer()
	df = tweet_analyzer.tweets_to_dataframe(tweets)   ## To convert tweets to a DataFrame


	###Time series
	###Plot Number of likes vs Date
	time_likes = pd.Series(data=df['likes'].values,index=df['date'])
	time_likes.plot(figsize=(16,8),label='Likes',legend=True)
	###Plot Number of Retweets vs Date
	time_likes = pd.Series(data=df['retweet_count'].values,index=df['date'])
	time_likes.plot(figsize=(16,8),label='Retweets',legend=True)
	plt.show()