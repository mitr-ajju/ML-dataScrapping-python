
from bs4 import BeautifulSoup
import re
import requests
from time import sleep
import json
import os
import sys
import mysql.connector
from PIL import Image

   
mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "mysql@123",
        database = "airbnb2022",
        auth_plugin='mysql_native_password'
    )
cursor = mydb.cursor()

listingid = '10061035'
offset = '0'


url = "https://www.airbnb.com/api/v3/PdpReviews?operationName=PdpReviews&locale=en&currency=USD&_cb=1cagpk00ljni7z11i6gg80qwltna&variables={\"request\":{\"fieldSelector\":\"for_p3\",\"limit\":50,\"listingId\":"+str(listingid)+",\"offset\":"+str(offset)+",\"showingTranslationButton\":false,\"numberOfAdults\":\"1\",\"numberOfChildren\":\"0\",\"numberOfInfants\":\"0\"}}&extensions={\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"ecf7222b1ad7e13da1bf39cf3cf05daa6bbc88709f06ea9cf669deca7e2e2de2\"}}"    
payload={}
headers = {'x-airbnb-api-key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20'}

response = requests.request("GET", url, headers=headers, data=payload)
review = response.content    
reviewSoup = BeautifulSoup(review, 'html.parser')
#print(response.text)

responseReview = json.loads(response.text)
#print(responseReview['data']['merlin']['pdpReviews']['reviews'])
count = 0
for review in responseReview['data']['merlin']['pdpReviews']['reviews']:
  reviewStatement = "INSERT IGNORE INTO airbnb_listing_reviews(`listingId`,`id`,`host_id`,`guest_id`,`rating`,`createdAt`) "
  reviewStatement = reviewStatement + "VALUES('" + str(listingid) + "','" + str(review['id'])+ "','" + str(review['reviewee']['id'])+ "','" + str(review['reviewer']['id']) + "','" + str(review['rating']) + "','" + str(review['createdAt']) + "')"
  print(reviewStatement)
  hostPictureUrl = str(review['reviewee']['pictureUrl']).split("?", 1)[0]
  guestPictureUrl = str(review['reviewer']['pictureUrl']).split("?", 1)[0]
  guestStatement = "INSERT IGNORE INTO airbnb_listing_users(`id`,`first_name`,`picture_large_url`)VALUES"
  guestStatement+="('" + str(review['reviewer']['id']) + "','" + str(review['reviewer']['firstName']) + "','" + guestPictureUrl + "')"
  
  hostStatement = "INSERT IGNORE INTO airbnb_listing_users(`id`,`first_name`,`picture_large_url`)VALUES"
  hostStatement+="('" + str(review['reviewee']['id']) + "','" + str(review['reviewee']['firstName']) + "','" + hostPictureUrl + "')"
  print(guestStatement)
  print(hostStatement)
  try:
      cursor.execute(reviewStatement)
      cursor.execute(guestStatement)
      cursor.execute(guestStatement)
  except Exception as e:
      print(str(e) +"\n")
  count+=1
   
mydb.commit()
mydb.close()
