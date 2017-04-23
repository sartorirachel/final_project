#Final 206 Project Option 2 by Rachel Sartori

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

#twitter caching process
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}

#define twitter_search_with_caching that caches data
def twitter_search_with_caching(consumerKey, consumerSecret, accessToken, accessSecret, searchQuery):
	results_url = api.search(q=searchQuery)

	if searchQuery in CACHE_DICTION:
		response_text = CACHE_DICTION["twitter_"+searchQuery]
	else:
		results = results_url
		CACHE_DICTION["twitter_"+searchQuery] = results

		jsonFile = open('twitter_finalproject_cache.json', 'w')
		jsonFile.write(json.dumps(CACHE_DICTION))
		jsonFile.close()

		response_text = CACHE_DICTION["twitter_"+searchQuery]
	return response_text

#invocation of function for twitter_search_with_caching
searchedTweets = twitter_search_with_caching(consumer_key, consumer_secret, access_token, access_token_secret, "Grease")

#movie_title_twitter_data takes in a movie title and returns data about ten tweets that mention the movie title and caches data
def movie_title_twitter_data(movie_title):
	unique_identifier = "twitter_{}".format(movie_title) 

	if unique_identifier in CACHE_DICTION:
		twitter_results = CACHE_DICTION[unique_identifier]
	else:
		twitter_results = api.statuses_lookup(movie_title)

		CACHE_DICTION[unique_identifier] = twitter_results
		
		f = open(CACHE_FNAME,'w')
		f.write(json.dumps(CACHE_DICTION)) 
		f.close()

	tweets = [] 
	for tweet in twitter_results:
		tweets.append(tweet)
	return tweets[:10]

#write invocation of function movie_title_twitter_data
twitter_data = movie_title_twitter_data("Let's Be Cops")

#write function get_user_tweets to access data about a Twitter user to get information about each of the Users in the "neighborhood" -- every user who posted any of the tweets retreived and every user who is mentioned in them
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

# Write an invocation of function get_user_tweets
umich_tweets = get_user_tweets('umich')

#cache file for OMDB data
CACHE_FNAME2 = 'omdb_finalproject_cache.json'

#OMDB caching process
try: 
	cache_file2 = open(CACHE_FNAME2, 'r')
	cache_contents2 = cache_file2.read()
	CACHE_DICTION2 = json.loads(cache_contents2)
except:
	CACHE_DICTION2 = {}

#pick 3 movie title search terms for OMDB and put those strings in list
movie_title_list = ['Contact', 'The Martian', 'Interstellar']

#write function omdb_data that takes in movie title and returns all information about movie and caches data
def omdb_data(movie_list):
	movie_info = []
	for movie in movie_list:
		unique_identifier = 'omdb_{}'.format(movie)
		if unique_identifier in CACHE_DICTION2:
			movie_info.append(CACHE_DICTION2[unique_identifier])
		else:
			r = requests.get("http://www.omdbapi.com/?t="+movie)
			omdb_results = r.text
			movie_info.append(omdb_results)
			CACHE_DICTION2[unique_identifier] = omdb_results
			f = open(CACHE_FNAME2, 'w')
			f.write(json.dumps(CACHE_DICTION2))
			f.close()
	return movie_info

#define class Movie that accepts dictionary that represents movie, has 3 instance variables, has 2 methods besides constructor

#optional: create class to handle Twitter data

#make request to OMDB on each of the 3 search terms in movie_title_list using function to accumulate all dictionaries retrieved from doing this, each representing one movie, into a list

#using above list of dictionaries, create list of instances of class Movie

#create database file with 3 tables: Tweets, Users, Movies
conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()

#Tweets table with rows:
	# Tweet text
	# Tweet ID (primary key)
	# The user who posted the tweet (represented by a reference to the users table)
	# The movie search this tweet came from (represented by a reference to the movies table)
	# Number favorites
	# Number retweets

statement = ('DROP TABLE IF EXISTS Tweets')
cur.execute(statement)
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Tweets (tweet_id STRING PRIMARY KEY, '
table_spec += 'text TEXT, user_id STRING, movie_title TEXT, retweets INTEGER, num_favs INTEGER)'
cur.execute(table_spec)

#Users table with rows:
	# User ID (primary key)
	# User screen name
	# Number of favorites that user has ever made

statement = ('DROP TABLE IF EXISTS Users')
cur.execute(statement)
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Users (user_id STRING PRIMARY KEY, '
table_spec += 'screen_name TEXT, num_likes INTEGER)'
cur.execute(table_spec)

#Movies table with rows:
	# ID (primary key)
	# Title of the movie
	# Director of the movie 
	# Number of languages the movie has
	# IMDB rating of the movie
	# The top billed (first in the list) actor in the movie

statement = ('DROP TABLE IF EXISTS Movies')
cur.execute(statement)
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Movies (movie_id STRING PRIMARY KEY, '
table_spec += 'movie_title TEXT, director TEXT, num_languages INTEGER, IMDB_rating REAL, top_billed TEXT)'
cur.execute(table_spec)

#load data about all tweets gathered from timeline of each search into Tweets table
for tweet in searchedTweets['statuses']:
  query = searchedTweets['search_metadata']['query']
  cur.execute('INSERT INTO Tweets (tweet_id, text, user_id, movie_title, num_favs, retweets) VALUES (?, ?, ?, ?, ?, ?)', (tweet['id_str'], tweet['text'], tweet['user']['id_str'], query, tweet['favorite_count'], tweet['retweet_count']))
  conn.commit()

cur.close() 

#make a query to select all of the tweets (full rows of tweet information) that have been retweeted more than 25 times

#make a JOIN query that accesses the user who posted the tweet from the Tweets table and the user screen name from the Users table

#make a query to select all of the user screen names from the database and use a list comprehension to save a resulting list of strings in the variable screen_names

#use a Counter in the collections library to find the most common word among all of the words (combinations of characters separated by whitespace) in the Tweet text in Tweets table

#write data to text file "Contact, The Martian, and Interstellar Twitter Summary" in which I have each result of my data processing clearly written to the file on several different lines 

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
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Tweets table")
		conn.close()
	def test_tweets_table(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT tweet_id FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1][0])>=2,"Testing that a tweet tweet_id value fulfills a requirement of being a Twitter user id rather than an integer, etc")
		conn.close()
class UsersTable(unittest.TestCase):
	def test_users_table(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==3,"Testing that there are 3 columns in the Tweets table")
		conn.close()
class MoviesTable(unittest.TestCase):
	def test_movies_table(self):
		conn = sqlite3.connect('finalproject.db')
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