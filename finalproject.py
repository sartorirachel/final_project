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
searchedTweets = twitter_search_with_caching(consumer_key, consumer_secret, access_token, access_token_secret, "Hairspray")

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
		self.ID = movie_dict['imdbID']
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
		self.num_favs = tweet_dict['favorite_count']
		self.num_retweets = tweet_dict['retweet_count']

	#use regex to find all mentioned users
	def mentioned_users(self):
		mentioned_users = re.findall('\B\@([\w\-]+)', self.text)
		if len(mentioned_users) < (1):
			return "no mentioned users"
		else:
			return mentioned_users

	#create movie_names() to find movie title of searched movie for Tweets Table later
	def movie_names(self):
		if "Contact" in self.text:
			return "Contact"
		if "The Martian" in self.text:
			return "The Martian"
		if "Interstellar" in self.text:
			return "Interstellar"

#use twitter_search_with_caching to search for each of the titles of three movies in movie_instances
movie_title_search = []
movie_title_search_lst = []
for movie in movie_instances:
	movie_title_search = twitter_search_with_caching(consumer_key, consumer_secret, access_token, access_token_secret, movie.title)
	movie_title_search_lst.append(movie_title_search)

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
		self.num_likes = user_dict['user']['favourites_count']

##create list of instances of each user
user_instance_lst = []
for user in users_info:
	dict = twitter_user_with_caching(consumer_key, consumer_secret, access_token, access_token_secret, user)
	one_user = TwitterUser(dict[0])
	user_instance_lst.append(one_user)

#create database file finalproject.db with 3 tables: Tweets, Users, Movies
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
table_spec += 'text TEXT, user_id STRING, movie_title TEXT, num_favs INTEGER, retweets INTEGER)'
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

#load data into databases

	##load data in Tweets table
# unique_tweet_ids = []
# tweet_table_lst = []
# for tweet in tweet_instance_lst:
# 	data_tuple = (tweet.text, tweet.tweet_id, tweet.user_id, tweet.movie_names(), tweet.num_favs, tweet.num_retweets)
# 	if tweet.tweet_id not in unique_tweet_ids:
# 		unique_tweet_ids.append(tweet.tweet_id)
# 		tweet_table_lst.append(data_tuple)
# statement = 'INSERT INTO Tweets VALUES (?,?,?,?,?,?)'
# for x in tweet_table_lst:
# 	cur.execute(statement, x)
# 	conn.commit()

	##load all of users that are tweeting about searched movie into Users table
unique_user_ids = []
user_table_lst = []
for user in user_instance_lst:
	id_num = user.user_id
	data_tuple = (user.user_id, user.screen_name, user.num_likes)
	if id_num not in unique_user_ids:
		unique_user_ids.append(id_num)
		user_table_lst.append(data_tuple)
statement = 'INSERT INTO Users VALUES (?,?,?)'
for x in user_table_lst:
	cur.execute(statement, x)
conn.commit()

	##load data into Movies table
movie_table_lst = []
for movie in movie_instances:
	data_tuple = (movie.ID, movie.title, movie.director, movie.num_languages(), movie.rating, movie.first_actor())
	movie_table_lst.append(data_tuple)
statement = 'INSERT INTO Movies VALUES (?,?,?,?,?,?)'
for x in movie_table_lst:
	cur.execute(statement, x)
conn.commit()

#make an INNER JOIN query that accesses movie_title from Tweets table and the user screen_name from the Users table who posted the tweet from the Tweets table
query = "SELECT movie_title, Users.screen_name FROM Tweets INNER JOIN Users on Tweets.user_id = Users.user_id"
movie_title_and_screen_name_joined = cur.execute(query).fetchall()

#make a query to select all of the text of tweets that have been retweeted more than 25 times
query = "SELECT text FROM Tweets WHERE retweets > 25"
tweet_text_RT_more_than_25 = cur.execute(query).fetchall

##Access all those strings, and save them in a variable called RT_tweet_text_lst, which should ultimately be a list of strings
query = "SELECT text FROM Tweets WHERE retweets > 25"
cur.execute(query).fetchall
RT_tweet_text_lst = []
for element in cur:
	RT_tweet_text_lst.append(element)

# Use a set comprehension to get a set of all words (combinations of characters separated by whitespace) among the tweet text in the RT_tweet_text_lst list. Save the resulting set in a variable called words_set.
words_set = set()
for element in RT_tweet_text_lst:
	match = re.findall(r'(\S+)', element)
	if match:
		for each in match:
			words_set.add(each)
		else:
			words_set = set()

#use a Counter in the collections library to find the most common characters among all of the words (combinations of characters separated by whitespace) in the Tweet texts in RT_tweet_text_lst. Save that most common character in a variable called most_common_char. Break any tie alphabetically
from collections import Counter
c = Counter()
most_common_chars = {}
for ch in RT_tweet_text_lst:
	most_common_char = Counter(ch[0]).most_common(1)
	if ch[0] not in most_common_chars:
		most_common_chars[ch[0]] = most_common_char[0][0]

#write data to text file "Contact, The Martian, and Interstellar Twitter Summary April 25 2017" in which I have each result of my data processing clearly written to the file on several different lines 
summary_file = open("206_final_output.txt", "w")

summary_file.write("Contact, The Martian, and Interstellar Twitter Summary April 25 2017 \n")
summary_file.write("\n")

summary_file.write("Movie Titles Searched: \n")
for movie_title in movie_list:
	summary_file.write(movie_title)
	summary_file.write("\n")

summary_file.write("The strings of each tweet text: \n")
for text in RT_tweet_text_lst:
	summary_file.write(text)
	summary_file.write("\n")

summary_file.write("set of all words (combinations of characters separated by whitespace) among the tweet texts: \n")
for wrd in words_set:
	summary_file.write(wrd)
	summary_file.write("\n")

summary_file.write("most common character among all of the words (combinations of characters separated by whitespace) in the Tweet texts")
for ch in most_common_chars:
	summary_file.write(ch)
	summary_file.write("\n")

#close database
cur.close()

# Put your tests here----------------------------------------------------------------------------------------------------------------------------------------------------------------------
class TwitterCache(unittest.TestCase):
	def test_twitter_cache(self):
		fpt = open("twitter_finalproject_cache.json","r")
		fpt_str = fpt.read()
		fpt.close()
		obj = json.loads(fpt_str)
		self.assertEqual(type(obj),type({"hi":"bye"}))
	def test_cache_diction(self):
		self.assertEqual(type(CACHE_DICTION),type({}),"Testing whether I have a CACHE_DICTION dictionary")
	def test_umich_caching(self):
		fstr = open("twitter_finalproject_cache.json","r").read()
		self.assertTrue("umich" in fstr)

class OMDBCache(unittest.TestCase):
	def test_omdb_cache(self):
		fpt = open("omdb_finalproject_cache.json", "r")
		fpt_str = fpt.read()
		fpt.close()
		obj = json.loads(fpt_str)
		self.assertEqual(type(obj), type ({"hello":"Goodbye"}))
	def test_cache_diction2(self):
		self.assertEqual(type(CACHE_DICTION2),type({}),"Testing whether I have a CACHE_DICTION2 dictionary")

# class TweetsTable(unittest.TestCase):
# 	def test_tweets_table(self):
# 		conn = sqlite3.connect('finalproject.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Tweets');
# 		result = cur.fetchall()
# 		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Tweets table")
# 		cur.close()
# 	def test_tweets_table(self):
# 		conn = sqlite3.connect('finalproject.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT tweet_id FROM Tweets');
# 		result = cur.fetchall()
# 		self.assertTrue(len(result[1][0])>=2,"Testing that a tweet tweet_id value fulfills a requirement of being a Twitter user id rather than an integer, etc")
# 		cur.close()
class UsersTable(unittest.TestCase):
	def test_users_table(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==3,"Testing that there are 3 columns in the Users table")
		cur.close()
class MoviesTable(unittest.TestCase):
	def test_movies_table(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Movies table")
		cur.close()

class ClassMovie(unittest.TestCase):
	def test_class_movie_method_num_languages(self):
		value = Movie({'imdbID':'g1234','Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.num_languages(), 2)
	def test_class_movie_method_num_languages2(self):
		value = Movie({'imdbID':'l1234','Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(type(value.num_languages()), type(2))
	def test_class_movie_method_first_actor(self):
		value = Movie({'imdbID':'k1234','Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.first_actor(), 'Ryan Gosling')
	def test_class_movie_method_first_actor2(self):
		value = Movie({'imdbID':'h1234','Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(type(value.first_actor()), type('Ryan'))
	def test_class_movie_method_list_of_actors(self):
		value = Movie({'imdbID':'j1234','Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.list_of_actors(), ['Ryan Gosling', 'Ellen Degeneres'])
	def test_class_movie_method_list_of_actors2(self):
		value = Movie({'imdbID':'m1234','Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(type(value.list_of_actors()), type(['Ryan', 'Ellen']))
	def test_class_movie_method_str(self):
		value = Movie({'imdbID':'i1234','Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(value.__str__(), 'Plot description: Three little pigs run from wolf')
	def test_class_movie_method_str2(self):
		value = Movie({'imdbID':'n1234','Title':'Toy Story','Director':'Rachel','imdbRating':4,'Actors':'Ryan Gosling, Ellen Degeneres', 'Language':'English, Spanish','Plot':'Three little pigs run from wolf'})
		self.assertEqual(type(value.__str__()), type('Plot'))

class ClassTweet(unittest.TestCase):
	def test_class_tweet_method_mentioned_users(self):
		tweet = Tweet(searchedTweets['statuses'][3]) 
		tweet.text = "Apparently hairspray was part of the uniform back then. https://t.co/Z9bdFmrgZP"
		self.assertEqual(tweet.mentioned_users(), 'no mentioned users')
	def test_class_tweet_method_mentioned_users2(self):
		tweet = Tweet(searchedTweets['statuses'][3])
		tweet.text = "Apparently hairspray was part of the uniform back then. https://t.co/Z9bdFmrgZP"
		self.assertEqual(type(tweet.mentioned_users()), type('hi'))
	def test_class_tweet_method_movie_names(self):
		tweet = Tweet(searchedTweets['statuses'][3])
		tweet.text = "Contact is the best movie ever"
		self.assertEqual(tweet.movie_names(), "Contact")
	def test_class_tweet_method_movie_names(self):
		tweet = Tweet(searchedTweets['statuses'][3])
		tweet.text = "Interstellar is the best movie ever"
		self.assertEqual(tweet.movie_names(), "Interstellar")

if __name__ == "__main__":
	unittest.main(verbosity=2)