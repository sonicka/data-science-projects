# MINI PROJECT 1
# Author: Soňa Leitmanová
# Report: A goal of this project was to find 5 best restaurants in Helsinki that meet certain requirements. 
# First I filtered as many requirements as possible via web user interface including price range,
# acceptance of credit cards, being "breakfast and brunch" restaurant and location in Helsinki.
# Then I scraped through 3 hmtl pages of results, filtering restaurants according to number of review
# and opening hours constraint using a few custom Python functions and BeautifulSoup library.
# Final set of 5 restaurants is based on number of reviews and average rating and it's displayed
# in a table using Pandas framework.

# coding: utf-8

## all imports
from IPython.display import HTML
import numpy as np
import urllib2
import bs4 #this is beautiful soup
import time
import operator
import socket
import cPickle
import re # regular expressions

from pandas import Series
import pandas as pd
from pandas import DataFrame

import matplotlib
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

import seaborn as sns
sns.set_context("talk")
sns.set_style("white")
from lxml import html
import requests

import win_unicode_console
from numpy import median

sourcestr1 = "https://www.yelp.com/search?find_desc=Restaurants&start="
sourcestr2 = "&cflt=breakfast_brunch&attrs=BusinessAcceptsCreditCards,RestaurantsPriceRange2.2&ed_attrs=RestaurantsPriceRange2.4,RestaurantsPriceRange2.1,RestaurantsPriceRange2.3&l=p:FI-18:Helsinki::"

url1 = "".join((sourcestr1, "0", sourcestr2))
url2 = "".join((sourcestr1, "10", sourcestr2))
url3 = "".join((sourcestr1, "20", sourcestr2))

r1 = urllib2.urlopen(url1).read()
r2 = urllib2.urlopen(url2).read()
r3 = urllib2.urlopen(url3).read()

soup1 = bs4.BeautifulSoup(r1, "lxml")
soup2 = bs4.BeautifulSoup(r2, "lxml")
soup3 = bs4.BeautifulSoup(r3, "lxml")

restaurants = []
restaurants1 = soup1.find_all("div", class_="search-result natural-search-result")
restaurants2 = soup2.find_all("div", class_="search-result natural-search-result")
restaurants3 = soup3.find_all("div", class_="search-result natural-search-result")
restaurants = restaurants1 + restaurants2 + restaurants3

# functions to get name, url, rating and number of reviews of a restaurant and filter restaurants closed at the weekend

def getname(element):
    name = ""
    name = element.span.get_text()
    name = name[3:]
    return name.strip()

def geturl(num):
    url = restaurants[num].a["href"]
    return "".join(("https://www.yelp.com", url))

def getrating(num):
    ratingattr = restaurants[num].find('div', {'class' : 'biz-rating biz-rating-large clearfix'}).findNext('div').attrs
    return float(ratingattr['title'][:3])

def getnumberofreviews(num):
    numofreviewsstring = restaurants[num].find('span', attrs={'class':'review-count rating-qualifier'}).get_text()
    numofreviewslist = re.findall('([0-9]+)', numofreviewsstring)
    numberencoded = numofreviewslist[0].encode('utf-8')
    return int(numberencoded)

def filterclosed(dic):
    finalrests = dict(dic)
    for key, value in dic .iteritems():
        r = urllib2.urlopen(value).read()
        soup = bs4.BeautifulSoup(r, "lxml")
        timetable = soup.find_all('th', {'scope' : 'row'}, text=["Sat", "Sun"])
        closed = ""
        for day in timetable:
            closed = day.findNext('td').contents[0].strip()
            if closed == "Closed":
                del finalrests[key]
                break
    return finalrests

ratings = []
sumofratings = 0
averagerating = 0
numofratings = 0
sumofnumberofratings = 0
averagenumofratings = 0
medianvalue = 0

# dict rests1 contains names and links to restaurants matching criteria and having at least 5 reviews
rests1 = {}
i = 0
for element in restaurants:
    numofreviews = getnumberofreviews(i)
    url = geturl(i)
    if (numofreviews >= 5):
        numofratings = numofratings+1
        sumofratings = sumofratings+getrating(i)
        sumofnumberofratings = sumofnumberofratings+numofratings
        ratings.append(numofreviews)
        key = getname(element)
        
        if key not in rests1:
            rests1[key] = url
        else:
            key = " ".join((key, "2"))
            rests1[key] = url
    i = i+1

# dict rests2 contains filtered results without restaurants closed on Saturday or Sunday    
rests2 = filterclosed(rests1)

averagerating = sumofratings/numofratings
averagenumofratings = sumofnumberofratings/numofratings
medianvalue = median(ratings)

# dict rests3 contains only restaurants with high number of reviews
# dict new collects preliminary set of data used in data plot later
rests3 = {}
new = {}
j = 0
for element in restaurants:
    numofreviews = getnumberofreviews(j)
    rating = getrating(j)
    if numofreviews >= medianvalue+averagenumofratings:
        rests3[getname(element)] = geturl(j)
        if rating >= averagerating:
            new[getname(element)] = [rating, numofreviews]
    j = j+1

# dict rests contains final set of the best restaurants based on average rating and number of ratings
rests = {x:rests2[x] for x in rests2 if x in rests3}

# dict final is used for plotting data
final = {x:new[x] for x in new if x in rests}

# data plot of 5 best restaurants represented by a table
df = pd.DataFrame(data=final).transpose()
df.columns = ['rating', 'number of ratings']
df = df.sort_values(['number of ratings'], ascending=[0])
df