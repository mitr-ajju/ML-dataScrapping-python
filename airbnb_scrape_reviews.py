from bs4 import BeautifulSoup
import requests
from time import sleep
import json
import os
import sys
import mysql.connector
from datetime import datetime
import pandas as pd


scrapingDate = "29-12-2022"
listings = set()
username = 'dadepro'
password = 'dadepro_pwd'
logFileName = "log" + str(datetime.now().timestamp()) + ".txt"
logFileName = datetime.now().strftime('log_%H%M_%d%m%Y.txt')
proxy = f'http://{username}:{password}@all.dc.smartproxy.com:10001' 


mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "mysql@123",
            database = "airbnb2022",
            auth_plugin='mysql_native_password'
        )


def getAllReviewsforListing(listingId, times):
    offset=0
    responses=50
    url = "https://www.airbnb.com/api/v3/PdpReviews?operationName=PdpReviews&locale=en&currency=USD&_cb=1cagpk00ljni7z11i6gg80qwltna&variables={\"request\":{\"fieldSelector\":\"for_p3\",\"limit\":50,\"listingId\":"+str(listingId)+",\"offset\":"+str(offset)+",\"showingTranslationButton\":false,\"numberOfAdults\":\"1\",\"numberOfChildren\":\"0\",\"numberOfInfants\":\"0\"}}&extensions={\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"ecf7222b1ad7e13da1bf39cf3cf05daa6bbc88709f06ea9cf669deca7e2e2de2\"}}"    
    payload={}
    headers = {'x-airbnb-api-key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20'}
    print(url)

    try:
        while responses==50:
            responses=0
            try:
                response = requests.request("GET", url, headers=headers, data=payload,proxies={'http': proxy, 'https': proxy})
                review = response.content    
                reviewSoup = BeautifulSoup(review, 'html.parser')
                print(reviewSoup)
                # if "Parallel connections limit has been reached" in response.text:
                #     raise requests.exceptions.RequestException("Zyte Parallel error")
            except requests.exceptions.RequestException as e: 
                file1 = open(logFileName, "a")  
                file1.write("GetReviews: "+ str(listingId) +" "+ str(e) +"\n")
                file1.close()
                return getAllReviewsforListing(listingId,times+1)
            responseReview = json.loads(response.text)
            responses = len(responseReview)
            addReviews(responseReview, listingId)
            offset+=50
    except Exception as e:
        print(e)


def addReviews(responseReview, listingId):    
    cursor = mydb.cursor()
    count = 0
    print('\n')
    print(str(count) + 'in resp review' + ' - ' + str(listingId) )
    for review in responseReview['data']['merlin']['pdpReviews']['reviews']:
        reviewStatement = "INSERT IGNORE INTO airbnb_listing_review_japan_tokyo(`listing_Id`,`id`,`host_id`,`guest_id`,`rating`,`createdAt`) "
        reviewStatement = reviewStatement + "VALUES('" + str(listingId) + "','" + str(review['id'])+ "','" + str(review['reviewee']['id'])+ "','" + str(review['reviewer']['id']) + "','" + str(review['rating']) + "','" + str(review['createdAt']) + "')"
        print(reviewStatement)
        hostPictureUrl = str(review['reviewee']['pictureUrl']).split("?", 1)[0]
        guestPictureUrl = str(review['reviewer']['pictureUrl']).split("?", 1)[0]
        guestStatement = "INSERT IGNORE INTO airbnb_listing_guests_japan_tokyo(`id`,`first_name`,`picture_large_url`)VALUES"
        guestStatement+="('" + str(review['reviewer']['id']) + "','" + str(review['reviewer']['firstName']) + "','" + guestPictureUrl + "')"
        
        hostStatement = "INSERT IGNORE INTO airbnb_listing_hosts_japan_tokyo(`id`,`first_name`,`picture_large_url`)VALUES"
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
    print(str(count) + 'in resp review' + ' - ' + str(listingId) )


# Main method to start the program
db_Info = mydb.get_server_info()
print("Connected to MySQL Server version ", db_Info)
cursor = mydb.cursor()
cursor.execute("select database();")
record = cursor.fetchone()
print("You're connected to database: ", record)

cursor.execute('''SELECT id FROM airbnb2022.airbnb_listing_details_japan_tokyo where id not in (select distinct listing_id from airbnb_listing_review_japan_tokyo);''')

df = pd.DataFrame(cursor.fetchall(), columns = ['id'])

for index, row in df.iterrows():
    print(row['id'])
    getAllReviewsforListing(row['id'], 0)
    

mydb.commit()
mydb.close()
