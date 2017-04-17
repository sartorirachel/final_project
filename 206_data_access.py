###### INSTRUCTIONS ###### 

# An outline for preparing your final project assignment is in this file.

# Below, throughout this file, you should put comments that explain exactly what you should do for each step of your project. You should specify variable names and processes to use. For example, "Use dictionary accumulation with the list you just created to create a dictionary called tag_counts, where the keys represent tags on flickr photos and the values represent frequency of times those tags occur in the list."

# You can use second person ("You should...") or first person ("I will...") or whatever is comfortable for you, as long as you are clear about what should be done.

# Some parts of the code should already be filled in when you turn this in:
# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 
# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
# - At least enough code to load data into 1 of your dtabase tables (this should accord with your instructions/tests)

######### END INSTRUCTIONS #########

# Put all import statements you need here.

import unittest
import itertools
import collections
import tweepy
import re
import twitter_info
import json
import sqlite3
import random
import requests

# Begin filling in instructions....

# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 

#authentication information in twitter_info.py file, imported above
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

#twitter caching file
CACHE_FNAME = "twitter_finalproject_cache.json"

try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}

#write function to get and cache data based on search term

#write invocation of function

#write function called get_user_tweets to get and cache data about a Twitter user. should accept a specific Twitter user handle and return data that represents tweets from that user's timeline

def get_user_tweets(user_handle):
	unique_identifier = "twitter_{}".format(user_handle)
	if unique_identifier in CACHE_DICTION:
		public_tweets = CACHE_DICTION[unique_identifier]
	else:
		public_tweets = api.user_timeline(user_handle)
		CACHE_DICTION[unique_identifier] = public_tweets
		cache_file = open(CACHE_FNAME, 'w')
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()
	return public_tweets

# Write an invocation to the function for the "umich" user timeline and save the result in a variable called umich_tweets:

umich_tweets = get_user_tweets('umich')

# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
#^for this part, see tests under classTwitterCache below in tests area

# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.



# - At least enough code to load data into 1 of your database tables (this should accord with your instructions/tests)



# Put your tests here, with any edits you now need from when you turned them in with your project plan.

class TwitterCache(unittest.TestCase):
	def test_twitter_cache(self):
		fpt = open("twitter_finalproject_cache.json","r")
		fpt_str = fpt.read()
		fpt.close()
		obj = json.loads(fpt_str)
		self.assertEqual(type(obj),type({"hi":"bye"}))
	def test_cache_diction(self):
		self.assertEqual(type(CACHE_DICTION),type({}),"Testing whether you have a CACHE_DICTION dictionary")
	def test_umich_caching(self):
		fstr = open("twitter_finalproject_cache.json","r").read()
		self.assertTrue("umich" in fstr)
	def test_get_user_tweets(self):
		res = get_user_tweets("umsi")
		self.assertEqual(type(res),type(["hi",3]))
	def test_umich_tweets(self):
		self.assertEqual(type(umich_tweets),type([]))
	def test_umich_tweets2(self):
		self.assertEqual(type(umich_tweets[18]),type({"hi":3}))
class TweetsTable(unittest.TestCase):
	def test_tweets_table(self):
		conn = sqlite3.connect('final_project_tweets.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Tweets table")
		conn.close()
	def test_tweets_table(self):
		conn = sqlite3.connect('final_project_tweets.db')
		cur = conn.cursor()
		cur.execute('SELECT tweet_id FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1][0])>=2,"Testing that a tweet tweet_id value fulfills a requirement of being a Twitter user id rather than an integer, etc")
		conn.close()
class UsersTable(unittest.TestCase):
	def test_users_table(self):
		conn = sqlite3.connect('final_project_tweets.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==3,"Testing that there are 3 columns in the Tweets table")
		conn.close()
class MoviesTable(unittest.TestCase):
	def test_movies_table(self):
		conn = sqlite3.connect('final_project_tweets.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Tweets table")
		conn.close()

class ClassMovie(unittest.TestCase):
	def test_class_movie_instance_variables(self):
		value = Movie({'Forrest Gump'})
		self.assertEqual(value.movie_title, "Forrest Gump")
	def test_class_movie_instance_variables_type_movie_title(self):
		value = Movie({'Forrest Gump'})
		self.assertEqual(type(value.movie_title), type("movie title"))
	def test_class_movie_instance_variables_type_movie_director(self):
		value = Movie({'Forrest Gump'})
		self.assertEqual(type(value.movie_director), type("move_director"))
	def test_class_movie_instance_variables_type_IMDB_rating(self):
		value = Movie({'Forrest Gump'})
		self.assertEqual(type(value.IMDB_rating), type(1))

if __name__ == "__main__":
	unittest.main(verbosity=2)

# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)