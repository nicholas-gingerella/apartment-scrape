#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup

from time import sleep
import datetime
import re
from random import randint
from warnings import warn
from time import time
from IPython.core.display import clear_output
import numpy as np
import json

currTime = datetime.datetime.now()
print(currTime)

# Create class to store and operate on craigslist listings
class ApartmentListing:
    def __init__(
            self,
            listingId=np.nan,
            price=np.nan,
            listingTime='',
            title='',
            rooms=np.nan,
            sqft=np.nan,
            link='',
            area=''
        ):
        self.listingId = listingId
        self.price = price
        self.listingTime = listingTime
        self.title = title
        self.rooms = rooms
        self.sqft = sqft
        self.link = link
        self.area = area
    
    def __init__(self, listing):
        self.set_listing_details(listing)
    
    def __str__(self):
        listingStr = f'{self.listingId}\n{self.title}\n{self.price}\n{self.rooms}\n{self.sqft}\n{self.area}\n{self.listingTime}\n{self.link}'
        return listingStr
    
    def __iter__(self):
        yield 'title', self.title
        yield 'listingTime', self.listingTime
        yield 'price', self.price
        yield 'sqft', self.sqft
        yield 'area', self.area
        yield 'link', self.link

    def set_listing_details(self, listing):
        self.listingId = self.get_id(listing)
        self.price = self.get_price(listing)
        self.listingTime = self.get_time(listing)
        self.title = self.get_title(listing)
        self.rooms = self.get_rooms(listing)
        self.sqft = self.get_sqft(listing)
        self.link = self.get_link(listing)
        self.area = self.get_area(listing)
    
    def sanitize_nan(self):
        if self.listingId is np.nan:
            self.listingId = 0
        if self.price is np.nan:
            self.price = 0
        if self.rooms is np.nan:
            self.rooms = 0
        if self.sqft is np.nan:
            self.sqft = 0
    
    def print_listing(self):
        print(f'Id: {self.listingId}')
        print(f'Title: {self.title}')
        print(f'Price: {self.price}')
        print(f'Rooms: {self.numRooms}')
        print(f'Sqft: {self.sqft}')
        print(f'List Time: {self.listingTime}')
        print(f'Area: {self.area}')
        print(f'Link: {self.link}')
    
    def get_rooms(self, listing):
        rooms = np.nan
        housingElem = listing.find('span', class_='housing')
        if housingElem is None:
            return rooms
        
        if len(housingElem.text.split()) > 0:
            for s in housingElem.text.split():
                if s.endswith("br"):
                    rooms = s.strip()[:-2]
                    rooms = int(rooms)
        return rooms
    
    def get_sqft(self, listing):
        sqft = np.nan
        
        # Contains num bedrooms and sqft, split into list and
        # find the sqft entry
        housingElem = listing.find('span', class_='housing')
        
        if housingElem is None:
            return sqft
        
        if len(housingElem.text.strip().split()) > 0:
            for s in housingElem.text.split():
                if s.endswith("ft2"):
                    sqft = int(s.strip()[:-3])
        return sqft
    
    def get_price(self, listing):
        priceStr = listing.find('span', class_='result-price').text.strip()
        regexPattern = '[$,]'
        cleanedPriceStr = re.sub(regexPattern, '', priceStr)
        return int(cleanedPriceStr)
    
    def get_title(self, listing):
        titleStr = listing.find('a', class_='result-title hdrlnk').text.strip()
        return titleStr

    def get_area(self, listing):
        areaStr = listing.find('span', class_='result-hood').text.strip()
        areaStr = areaStr[1:] if areaStr.startswith('(') else areaStr
        areaStr = areaStr[:-1] if areaStr.endswith(')') else areaStr
        return areaStr.strip()

    def get_time(self, listing):
        timeStr = listing.find('time', class_='result-date')['datetime'].strip()
        return timeStr

    def get_link(self, listing):
        linkStr = listing.find('a', class_='result-title hdrlnk')['href'].strip()
        return linkStr
    
    def get_id(self, listing):
            resultTitleElem = listing.find('a', class_='result-title hdrlnk')
            listingId = resultTitleElem['id']
            cutPrefixCount = len("postid_")
            listingId = listingId[cutPrefixCount:]
            return listingId.strip()


# Build loop for apartment listings
# Make request and get a total count of all listings from craigslist
response = requests.get('https://inlandempire.craigslist.org/search/apa?hasPic=1&availabilityMode=0&sale_date=all+dates')
html_soup = BeautifulSoup(response.text, 'html.parser')

# Get total number of listings
resultsElem = html_soup.find('div', class_='search-legend')
resultsTotal = int(resultsElem.find('span', class_='totalcount').text)

# Each page has 119 posts. So we step in increments of 120 for page number
pages = np.arange(0, resultsTotal+1, 120)
#pages = [0,120,240]

# List we will collect all the apartment listings in
apartmentsList = []

# Get Request Params (Craigslist)
hasPictures = 1
availabilityMode = 0

iterations = 0
for page in pages:
    # Create and send http request to craigslist for apartments
    httpGetStr = 'https://inlandempire.craigslist.org/search/apa?'
    httpGetStr = httpGetStr + f's={page}'
    httpGetStr = httpGetStr + f'&hasPic={hasPictures}'
    httpGetStr = httpGetStr + f'&availabilityMode={availabilityMode}'
    response = requests.get(httpGetStr)
    
    # If this request failed, skip this iteration
    if response.status_code != 200:
        warn(f'Request: {requests}; Status Code: {response.status_code}')
        continue
    
    # Parse the html from the response and get all listing results from page
    pageHtml = BeautifulSoup(response.text, 'html.parser')
    pageListings = pageHtml.find_all('li', class_='result-row')
    
    # Convert these listings to a formatted listing object for easier processing
    for rawListing in pageListings:
        apartmentsList.append(ApartmentListing(rawListing))
    
    # Don't ping the site as fast as possible, or requests  will
    # fail (also don't DDOS them please...)
    sleep(randint(1,5))

print("Num Listings:",len(apartmentsList))

# Create a dict that will hold all of the listings for this scrape.
# Format this in a way that it can easily be dumped to a json file:
# {
#   "listings":
#        {
#            "<postID>":<listing json object>
#        }
# }
allListingDict = {}
allListingDict['listings'] = {}

# Go through all listings and add them to the master dicitonary
for apt in apartmentsList:
    testEntry = {}
    testEntryId = apt.listingId
    apt.sanitize_nan()
    testEntry = apt.__dict__ #maybe make copy?
    allListingDict['listings'][testEntryId] = testEntry

# Dump the master dictionary that now contains all of our listings
# to a json file
with open("craigslist_listings.json", 'w') as f:
    json.dump(allListingDict, f)



