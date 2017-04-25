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

#define twitter_search_with_caching that caches data based on a search term
def twitter_search_with_caching(consumerKey, consumerSecret, accessToken, accessSecret, searchQuery):
	results_url = api.search(q=searchQuery)
	if searchQuery in CACHE_DICTION:
		response_text = CACHE_DICTION["twitter_"+searchQuery]
	else:
		results = results_url
		CACHE_DICTION["twitter_"+searchQuery] = results
		cache_file = open(CACHE_FNAME, 'w')
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()
		response_text = CACHE_DICTION["twitter_"+searchQuery]
	return response_text

#invocation of function for twitter_search_with_caching
searchedTweets = twitter_search_with_caching(consumer_key, consumer_secret, access_token, access_token_secret, "Grease")

#define twitter_user_with_caching that caches data about a Twitter user
def twitter_user_with_caching(consumerKey, consumerSecret, accessToken, accessSecret, handle):
	results_url = api.user_timeline(id=handle)
	if handle in CACHE_DICTION:
		response_text = CACHE_DICTION[handle]
	else:
		results = results_url
		CACHE_DICTION[handle] = results
		cache_file = open(CACHE_FNAME, 'w')
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()
		response_text = CACHE_DICTION[handle]
	return response_text

#invocation of function twitter_user_with_caching
userTweets = twitter_user_with_caching(consumer_key, consumer_secret, access_token, access_token_secret, "umich")

#cache file for OMDB data
CACHE_FNAME2 = 'omdb_finalproject_cache.json'

#OMDB caching process
try: 
	cache_file2 = open(CACHE_FNAME2, 'r')
	cache_contents2 = cache_file2.read()
	cache_file2.close()
	CACHE_DICTION2 = json.loads(cache_contents2)
except:
	CACHE_DICTION2 = {}

#write function omdb_data that takes in movie title and returns all information about movie and caches data
def omdb_data(movie_title):
	results_url = 'http://www.omdbapi.com/?'
	parameters = {'t': movie_title}
	resp = requests.get(url = results_url, params = parameters)
	response = json.loads(resp.text)
	if ('imdb_'+movie_title) in CACHE_DICTION2:
		response_text = CACHE_DICTION2['imdb_'+movie_title]
	else:
		omdb_results = response
		CACHE_DICTION2['imdb_'+movie_title] = omdb_results
		cache_file2 = open(CACHE_FNAME2, 'w')
		cache_file2.write(json.dumps(CACHE_DICTION2))
		cache_file2.close()
		response_text = CACHE_DICTION2['imdb_'+movie_title]
	return response_text

#write invocation of function omdb_data
movie_data = omdb_data('Toy Story')

#define class Movie that accepts dictionary that represents movie, has 6 instance variables, has 3 methods besides constructor
class Movie():
	def __init__(self, movie_dict={}):
		#instance variables
		self.title = movie_dict['Title']
		self.director = movie_dict['Director']
		self.rating = movie_dict['imdbRating']
		self.actors = movie_dict['Actors']
		self.languages = movie_dict['Language']
		self.plot = movie_dict['Plot']

	#num_languages finds the number of languages of the searched movie 
	def num_languages(self):
		num = self.languages.split(', ')
		return (len(num))

	#first_actor finds the name of the first actor listed for the searched movie
	def first_actor(self):
		return self.actors.split(', ')[0]

	#list_of_actors returns a list of all actors in searched movie
	def list_of_actors(self):
		return self.actors.split(', ')

	#returns human readable string of plot of searched movie beginning with "Plot description: "
	def __str__(self):
		return "Plot description: {}".format(self.plot)

#pick 3 movie title search terms for OMDB and put those strings in list
movie_list = ['Contact', 'The Martian', 'Interstellar']

#make request to OMDB using omdb_data function on each of 3 search terms in movie_list and accumulate all dictionaries you get, each representing one movie, into list
movie_data_lst = [omdb_data(movie) for movie in movie_list]

#use movie_data_lst to create list of instances of class Movie
movie_instances = [Movie(movie) for movie in movie_data_lst]

##create Tweet class to make it easier to get data and keep organized. Define mentioned_users method to help find user neighborhood
class Tweet():
	def __init__(self, tweet_dict = {}):
		self.user_id = tweet_dict['user']['id_str']
		self.text = tweet_dict['text']
		self.tweet_id = tweet_dict['id_str']
		self.user = tweet_dict['user']['screen_name']

	#use regex to find all mentioned users
	def mentioned_users(self):
		mentioned_users = re.findall('\B\@([\w\-]+)', self.text)
		if len(mentioned_users) < (1):
			return "no mentioned users"
		else:
			return mentioned_users

#use twitter_search_with_caching to search for each of the titles of three movies in movie_instances
movie_title_search = []
for movie in movie_instances:
	movie_title_search = twitter_search_with_caching(consumer_key, consumer_secret, access_token, access_token_secret, movie.title)

##save the above dictionary as list of instances of class Tweet
tweet_instance_lst = []
for tweet in movie_title_search['statuses']:
	one_tweet = Tweet(tweet)
	tweet_instance_lst.append(one_tweet)

##create list of information about user who psoted tweet you retrieved and every user who is mentioned in them
users_info = []
for tweet in tweet_instance_lst:
	user = tweet.user
	users_info.append(user)
	users_mentioned = tweet.mentioned_users()
	if users_mentioned != 'no mentioned users':
		for user in users_mentioned:
			users_info.append(user)

##create TwitterUser class to make it easier to get data and keep organized
class TwitterUser():
	def __init__(self, user_dict = {}):
		self.user_id = user_dict['user']['id_str']
		self.screen_name = user_dict['user']['screen_name']
		self.description = user_dict['user']['description']
		self.num_followers = user_dict['user']['followers_count']

##create list of instances of each user
user_instance_lst = []
for user in users_info:
	dict = twitter_user_with_caching(consumer_key, consumer_secret, access_token, access_token_secret, user)
	one_user = TwitterUser(dict[0])
	user_instance_lst.append(one_user)


#-------------------------------------------------------------------------

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

#create database file with 3 tables: Tweets, Users, Movies
conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()

#create Tweets table with rows:
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

#create Users table with rows:
	# User ID (primary key)
	# User screen name
	# Number of favorites that user has ever made

statement = ('DROP TABLE IF EXISTS Users')
cur.execute(statement)
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Users (user_id STRING PRIMARY KEY, '
table_spec += 'screen_name TEXT, num_likes INTEGER)'
cur.execute(table_spec)

#create Movies table with rows:
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

# Put your tests here
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
	def test_class_movie_instance_var_actors(self):
		value = Movie({'Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.actors, 'Ryan Gosling, Ellen Degeneres')
	def test_class_movie_instance_var_type_actors(self):
		value = Movie({'Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(type(value.actors), type('Ryan Gosling, Ellen Degeneres'))
	def test_class_movie_instance_var_languages(self):
		value = Movie({'Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.languages, 'English, Spanish')
	def test_class_movie_instance_var_type_languages(self):
		value = Movie({'Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(type(value.languages), type('English, Spanish'))
	def test_class_movie_instance_var_plot(self):
		value = Movie({'Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.plot, 'Three little pigs run from wolf')
	def test_class_movie_instance_var_type_plot(self):
		value = Movie({'Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(type(value.plot), type('Three little pigs run from wolf'))
	def test_class_movie_method_num_languages(self):
		value = Movie({'Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.num_languages(), 2)
	def test_class_movie_method_first_actor(self):
		value = Movie({'Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.first_actor(), 'Ryan Gosling')
	def test_class_movie_method_str(self):
		value = Movie({'Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.__str__(), 'Plot description: Three little pigs run from wolf')

if __name__ == "__main__":
	unittest.main(verbosity=2)