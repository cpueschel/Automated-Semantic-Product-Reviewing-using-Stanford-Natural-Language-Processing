import os
from bs4 import BeautifulSoup
import urllib2
import json
from pprint import pprint
from pyteaser import Summarize
import scrape
import csv
import re
import urlgenerate
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException 
from time import sleep
import string
import subprocess
import shlex
from re import split as regex_split, sub as regex_sub
import nltk.data
import time
from collections import defaultdict
import urllib
from random import randint
#////////////////////////////////////////////////////////


#SLEEP
#hours = 4
#print "Sleeping for " + str(hours) + " hours."
#time.sleep(60*60*hours)
#print "Done sleeping!"
#=======
websiteurl = "http://www.your-website.com/"

def check_for_repost(asinitem):
	columns_for_repost = defaultdict(list)

	csv_file = '/home/winterfell/Documents/generator/csvs/cookbooks2.csv' 
	with open(csv_file) as f:
	
		reader = csv.DictReader(f) 
		for row in reader: 
			for (k,v) in row.items(): 
				columns_for_repost[k].append(v) 
			     									
	f.close()
	print "Column length: " + str(len(columns_for_repost['asin']))
	#Repost to different categories. 
	count = 0
	asinset = columns_for_repost['asin']
	for each in asinset:
		if str(asinitem) == str(each):
			print "Item: " +str(each) + " posted already."
			return True

	return False

def get_review(review_url): 
	try:
		return scrape.get_review(review_url)
	except:
		return "none"

def split_sentences(text):    
	try:
		tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
		pre_review2 = tokenizer.tokenize(text)
		pre_review2 = [sent.capitalize() for sent in pre_review2]
		return pre_review2
	except: 
		sentences = regex_split('(?<![A-Z])([.!?]"?)(?=\s+\"?[A-Z])', text)
		s_iter = zip(*[iter(sentences[:-1])] * 2)
		s_iter = [''.join(map(unicode,y)).lstrip() for y in s_iter]
		s_iter.append(sentences[-1])
		return s_iter
	return ""

def get_setiment(review):
	try: 
		f = open("/home/winterfell/Downloads/stanford-corenlp-full-2014-06-16/foo.txt", 'w')
		f.write(review)
		f.close()

		proc = subprocess.Popen(["java -cp \"*\" -mx5g edu.stanford.nlp.sentiment.SentimentPipeline -file foo.txt"], cwd="/home/winterfell/Downloads/stanford-corenlp-full-2014-06-16", stdout=subprocess.PIPE, shell=True)
		(out, err) = proc.communicate()
		print "program output:", out
		args = shlex.split(out)
		print args
		sentiment = "None"
		for items in args:
			if "Negative" in items:
				sentiment = "Negative" 
			if "negative" in items:
				sentiment = "Negative"
			if "Positive" in items:
				sentiment = "Positive" 
			if "Neutral" in items:
				sentiment = "Neutral" 
			if "Very positive" in items:
				sentiment = "Positive"
		
		#print "Sentiment Detected: " + sentiment	
		return sentiment
	except:
		print "Sentiment Error..."
		return "Negative"

def unicode_check(a):
	if isinstance(a, str):
		print "ordinary string"
		return a
	elif isinstance(a, unicode):
		return filter(lambda x: x in string.printable, a)


def check_exists_by_class_name(driver,classname):
    try:
        driver.find_element_by_class_name(classname)
    except NoSuchElementException:
        return False
    return True

def replace_all(text, dic):
    for each in dic:
        text = text.replace(each,'')
    return text

def AMAZON_grabINFO(url):
	crumbs = []
	crumbed = False
	review = ""
	image_url =None
	#try:
	try:
		print "Requesting page..."
		page=urllib2.urlopen(url)
		soup = BeautifulSoup(page.read())
	except:
		return (None,None,None,None,None,False)

	#get images
	for item_IMAGE in soup.findAll("img",{ "id" : "landingImage" }): #alt of imgBlkFront
		image_url = item_IMAGE['src']
		print " New Link: " + str(image_url)
	#Product Review

	if image_url == None:
		print "Identified as none type."
		for item_IMAGE in soup.findAll("img",{ "id" : "imgBlkFront" }): #alt of imgBlkFront
			image_url = item_IMAGE['src']
			print " New Link: " + str(image_url)

	
	item_TITLE=soup.find("span",{ "id" : "productTitle" },text=True)
	if item_TITLE == None:
		print "No Title!"
		item_TITLE = "None"
	else:	
		text = ''.join(item_TITLE.findAll(text=True))
		item_TITLE = unicode_check(text).strip()
	print "TITLE: " + item_TITLE
	
	#Find Product Info
	dat_ladder = soup.find(attrs={'class' : 'zg_hrsr_ladder'})
	if dat_ladder is None:	
		print "No soup!"
		category = "none"
	else:
		get_rows = dat_ladder.findAll('a')
		print "Categories: "

		for hit in get_rows:
			text = ''.join(hit.findAll(text=True))
			data = unicode_check(text).strip()
	    		category = data
			print category
			crumbs.append(data.replace("&","and"))
		
	#print "Category: " + category
	review_soup = soup.find("div",attrs={"id":"revMHRL"})
	if review_soup == None:
		print "No Review Soup!"
		review_soup = ""
		review=""
	else:	
		#Scrape Review
		test = review_soup.findAll('a')
		review_url = url
		for reviews in test:
			if reviews.has_attr('href'):
				print "Reviews: " + reviews['href']
				review_url = reviews['href']
				if 'review' in reviews['href']:
					break
	
		#Get the Review
		pre_review = get_review(review_url)
		review = unicode_check(pre_review[:])
		print "Review: " + str(unicode_check(review))
		pre_review2 = split_sentences(review)
		print "Pre_Review2: "+ str(pre_review2)
	
		review = ""

		#Make the Review
		for each in pre_review2:
			sentiment = ""
			if len(review) < 500:
				sentiment = get_setiment(each)		
				print "Sentiment Detected: " + sentiment

				if ("Positive" == str(sentiment)) or ("Neutral" == str(sentiment))or ("positive" == str(sentiment)):
					print "Sentiment Found: " + sentiment
					review2 = review + each.replace("&","and") +" "
					if len(review2) < 500:
						review = review2
						print "Added sentence: " + each

			
	print "Summarized: " + str(review)
	return (image_url,review,item_TITLE,category,crumbs,False)

#Setup
profile = FirefoxProfile("/home/winterfell/.mozilla/firefox/nrw5axxu.default")
driver = webdriver.Firefox(profile)

#Avoid ICS & Sign into pintrest..
driver.get("http://www.google.com")
time.sleep(randint(5,8))
driver.get("http://www.pintrest.com")

#Load Json
csv_file = '/home/winterfell/Documents/generator/csvs/cookbooks_asin.csv'
columns = defaultdict(list) # each value in each column is appended to a list

with open(csv_file) as f:
	reader = csv.DictReader(f) # read rows into a dictionary format
	for row in reader: # read a row as {column1: value1, column2: value2,...}
		for (k,v) in row.items(): # go over each column name and value 
			columns[k].append(v) # append the value into the appropriate list
                             # based on column name k

f.close()	
for each,boardstring in zip(columns['asin'],columns['board']):
	print "Checking for Repost!"
	if check_for_repost(each): 
		print "This is a repost!..NEXT!"
		continue

	#ASIN BESTSELLER DATA
	asin = each
	print "ASIN: " + str(asin) + " and the board to be used is: " + str(boardstring)
	
	#URL OPENS DIRECTLY TO AMAZON. 
	amazon_url = "http://www.amazon.com/dp/" + str(asin)
	print "AMAZON URL: " + amazon_url
	crumbed = False
	image_url, review,item_TITLE,category, crumbs, crumbed = AMAZON_grabINFO(str(amazon_url))
	if review is None:
		continue
	#Check for Values
	if ("none" == category):
		category = boardstring

	if ("none" == item_TITLE):
		item_TITLE = page_title
	if crumbed == False:
		print "Breading the review with crumbs: " + str(crumbs)
		for each in crumbs:
				if len(review) < 500:
					breaded = review + " #"+ each
					if len(breaded) >= 500:
						print "Too many crumbs, too much bread!"
					else:
						review = breaded
						crumbed = True
	print "Review with Bread: " + review		
	#Increase Count.

	# Save to CSV
	f = open('/home/winterfell/Documents/generator/csvs/cookbooks2.csv', 'a')
	w = csv.writer(f)
	w.writerow([(time.strftime("%d/%m/%Y")), item_TITLE,category,asin])
	f.close()

	#Generate URL for Boston Outftters
	encrypted_url = urlgenerate.generateENCRPYTEDurl(str(asin), "")
	# Push to Pinterest

	#Generate pin page. 
	encrypted_url = websiteurl + encrypted_url
	

	#Checks for None Type of Image URL
	if image_url == None:
		continue
		
	pin_url = 'http://pinterest.com/pin/create/button/?url='+encrypted_url+'&media='+urllib.quote_plus(image_url)+'&description='
	
	category = boardstring
	print pin_url


	#Clean Up Product Review
	html_dic = ['andquot;','newandquot;','<u>','</u>','<b>','</b>','<i>','</i>','&quot;new&quot;','<br','&quot;','<p>', '</p>' ,'<span>','<link>','</link>','</span>','<i>','<br>','</br>','</i>','<em>','</em>','<h1>','</h1>','new&quot;','<','/>','>']
	product_review = replace_all(review,html_dic) 
	product_review = product_review.replace(' i ',' I ').replace("  "," ")
	print "Cleaned Review: " + product_review

	#Get pin'd page. 
	driver.get(pin_url)
	sleep(randint(5,8))

	#Add Description - 3/26 find_element_by_id
	elem = driver.find_element_by_class_name("pinDescriptionInput")
	elem.send_keys(product_review)
	sleep(randint(5,8))

	#Select the Board 
	elem = driver.find_element_by_class_name("Input")
	elem.click()
	sleep(randint(5,8))

	#Select the Board & Click again
	elem = driver.find_element_by_class_name("Input")
	elem.click()
	sleep(randint(5,8))

	#Select the Board & Click again
	elem = driver.find_element_by_class_name("Input")
	elem.click()
	sleep(randint(5,8))

	elem.send_keys(category) 
	sleep(randint(5,8))
	elem.send_keys(Keys.ENTER)

	print "Done with item. Sleeping for 5 seconds."
	sleep(randint(5,8))

	#sleep for a minute to allow for some "rest" 
	minsleep = randint(1, 5)
	sleep(60*minsleep)

driver.close()












