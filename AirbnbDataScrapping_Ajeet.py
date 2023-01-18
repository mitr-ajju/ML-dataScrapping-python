from concurrent.futures import ThreadPoolExecutor
from getpass import getuser
import gzip
from bs4 import BeautifulSoup
import re
import requests
from time import sleep
import json
import os
import sys
import mysql.connector
from datetime import datetime
#pip install mysql-connector-python-rf

scrapingDate = "28-12-2022"
listings = set()
username = 'dadepro'
password = 'dadepro_pwd'
logFileName = "log" + str(datetime.now().timestamp()) + ".txt"
logFileName = datetime.now().strftime('log_%H%M_%d%m%Y.txt')
proxy = f'http://{username}:{password}@all.dc.smartproxy.com:10001'

############ SCRAPE LOCATION ##################
#scrape page and return a beautiful soup object (using to get search results in specific area)
def scrape_page(page_url,times):  
    if times==6:
        file1 = open(logFileName, "a")  
        file1.write("Scrape Page failed 6 times with page url: " + str(page_url) +"\n")
        file1.close()
        return None
    try: 
        answer = requests.get(page_url,timeout=None,proxies={'http': proxy, 'https': proxy})
        # if "Parallel connections limit has been reached" in answer.text:
        #     raise requests.exceptions.RequestException("Zyte Parallel error")
    except requests.exceptions.RequestException as e: 
        file1 = open(logFileName, "a")  
        file1.write("Scrape Page: " + str(e) +"\n")
        file1.close()
        sleep(100)
        return scrape_page(page_url,times+1)
    content = answer.content
    
    soup = BeautifulSoup(content, 'html.parser')
    return soup

#scrapes given city and returns all listings using progressively shorter bounding boxes
def scrape_location(cityName,executor,level, offset, maxPrice, initRun): 
    global listings
    global countOfListing, lowerPriceLimit, upperPriceLimit

    mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "mysql@123",
            database = "airbnb2022",
            auth_plugin='mysql_native_password'
        )
    cursor = mydb.cursor()
    if level<9:
        try:
            scrape_location(cityName,executor,level+1, offset, maxPrice, initRun)
            
        except e:
            pass
    else:
        totalresponses=0
        responses=20
        offset = 0
        if initRun == 0:  #don't add duplicate listings to data
            countOfListing = 0
            lowerPriceLimit = 0
            upperPriceLimit = 0

        if (upperPriceLimit <= maxPrice) and (upperPriceLimit <= 1000):
            if initRun > 0:
                lowerPriceLimit += 1
            upperPriceLimit = lowerPriceLimit + 1
        # if(upperPriceLimit <= maxPrice) and (upperPriceLimit > 500) and (upperPriceLimit <= 1000):
        #     lowerPriceLimit += 100
        #     upperPriceLimit = lowerPriceLimit + 100
        if(upperPriceLimit <= maxPrice) and (upperPriceLimit > 1000):
            lowerPriceLimit += 1000
            upperPriceLimit = lowerPriceLimit + 1000


        while (upperPriceLimit <= maxPrice):
            responses=0
            try:
                print("price limit is " + str(lowerPriceLimit) + "&" + str(upperPriceLimit))
                pageUrl = "https://www.airbnb.com/s/" + cityName + "/homes?&tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=weekend_trip&date_picker_type=calendar&search_type=filter_change&price_min=" + str(lowerPriceLimit) + "&price_max=" + str(upperPriceLimit) + "&federated_search_session_id=30ee4d00-75f3-4ea9-a074-c2e41e0c828b&search_type=unknown&pagination_search=true&items_offset=" +str(offset)
                soup = scrape_page(pageUrl,0)
                #print(pageUrl)
                soup = soup.findAll('div',{'class':'cy5jw6o'})
                
                for listing in soup:
                    totalresponses+=1
                    responses+=1
                    for a in listing.findAll('a', href=True):
                        url = a['href']
                        #if "rooms" in url:
                        listingid = re.search('[0-9]+', url).group()
                        countOfListing += 1
                        print(str(countOfListing) + " - " + listingid)
                        if listingid in listings:  #don't add duplicate listings to data
                            break
                        listings.add(listingid)
                        executor.submit(getListingDetails,listingid,0)
                        break
                    if(totalresponses>=300): # create bounding boxes
                        initRun += 1
                        scrape_location(cityName,executor,level, offset, maxPrice,initRun)
                        break
                offset+=20
                if responses == 0:
                    initRun += 1
                    scrape_location(cityName,executor,level, offset, maxPrice,initRun)
                    break
            
            except Exception as e:
                print(e)
    try:
        file1 = open("current.txt", "a")  
        file1.close()
    except e:
        pass
    mydb.commit()
    mydb.close()

################ END OF SCRAPE LOCATION #####################



################ LISTINGS #################

keysListing = { 'city', 'user_id', 'price', 'price_formatted', 'country', 'state', 'person_capacity', 'zipcode', 'reviews_count' }
listinghHost = {'first_name', 'last_name', 'picture_large_url', 'reviewee_count', 'response_rate', 'acceptance_rate', 'recommendation_count'}

def getListingDetails(listingid,times):
    if times==3:
        file1 = open(logFileName, "a")  
        file1.write("GetListing failed 3 times with listingid: " + str(listingid) +"\n")
        file1.close()
        return
    url = "https://www.airbnb.com/api/v1/listings/" + str(listingid)
    payload={}
    headers = {
    'x-airbnb-api-key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20'
    }
    try:
        print(url)
        response = requests.request("GET", url, headers=headers, data=payload,proxies={'http': proxy, 'https': proxy})
        contentById = response.content
    
        soupById = BeautifulSoup(contentById, 'html.parser')
        print(soupById)
        # if "Parallel connections limit has been reached" in response.text:
        #     raise requests.exceptions.RequestException("Zyte Parallel error")
    except requests.exceptions.RequestException as e:
        file1 = open(logFileName, "a")  
        file1.write("GetListingDetails: "+ str(listingid) +" "+ str(e) +"\n")
        file1.close()
        sleep(10)
        return getListingDetails(listingid,times+1)
        
    mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "mysql@123",
            database = "airbnb2022",
            auth_plugin='mysql_native_password'
        )
    cursor = mydb.cursor()
    try:
        os.makedirs('data/'+scrapingDate+'/listings/tokyo/')
    except OSError as e:
        pass
    # with gzip.open('data/'+scrapingDate+'/listings/'+str(listingid)[:2]+'/'+str(listingid)[:4]+'/'+str(listingid) +'.gz', 'wt') as f:
    #     f.write(response.text)
    try:
        temp = json.loads(response.text)
        
        # Writing to sample.json
        filePathJson = 'data/'+scrapingDate+'/listings/tokyo/' + str(listingid) + '.json'
        with open(filePathJson, "w") as outfile:
            outfile.write(str(temp))
        

        addData(listingid,temp,cursor)
    except Exception as e:
        file1 = open(logFileName, "a")  
        file1.write("Listing " + str(listingid) + ": " + str(e) +"\n")
        file1.close()
    mydb.commit()
    mydb.close()


def addData(listingid,jsonLoaded,cursor): 
    try:
        listingProperty = ""
        listingPropertyData = ""
        currValues2 = []
        count=0
        for i in jsonLoaded['listing']:
            if i in keysListing:
                count+=1
                listingProperty += ", "+ str(i)     
                currValues2.append(str(jsonLoaded['listing'][i]))
        
               
        for i in range(count):
            listingPropertyData += ",%s"
            
        statement1 = "insert ignore into airbnb_listing_details_tokyo(id"+listingProperty+") values ('"+str(listingid)+"'"+listingPropertyData+")"
        hostProperty = ""
        hostPropertyData = ""
        hostValues = []
        count = 0
        id = ""
        for i in jsonLoaded['listing']['primary_host']:
            id = jsonLoaded['listing']['primary_host']['id']
            if i in listinghHost:
                count+=1
                hostProperty += ", "+ str(i)     
                hostValues.append(str(jsonLoaded['listing']['primary_host'][i]))
                
        for i in range(count):
            hostPropertyData += ",%s"
        hostStatement = "insert ignore into airbnb_listing_host_tokyo(id"+hostProperty+") values ('"+str(id)+"'"+hostPropertyData+")"
        try:
            cursor.execute(statement1,currValues2)
            cursor.execute(hostStatement, hostValues)
        except Exception as e:
            file1 = open(logFileName, "a")  
            file1.write("Listing " + str(listingid) + ": " + str(e) +"\n")
            file1.close()
    except Exception as e:
        file1 = open(logFileName, "a")  
        file1.write("Listing " + str(listingid) + ": " + str(e) +"\n")
        file1.close()
        pass 

################ END OF LISTINGS ####################



try:
    cityName = ['Hong-Kong', 'Tokyo--Japan', 'Singapore', 'Bangkok-Thailand', 'New-York--NY--United-States', 'Las-Vegas--NV--United-States', 'Boston--MA--United-States', 'Los-Angeles--CA--United-States']
    #cityName = ['Tokyo--Japan']
    maxPrice = 1000
    offset = 0
    initRun = 0
    print("Scrape started")

    for city in cityName:
        initRun = 0
        offset = 0
        executor = ThreadPoolExecutor(max_workers=50)
        scrape_location(city,executor,10, offset, maxPrice, initRun)
        executor.shutdown(wait=True)
    
   
    print("Scrape ended")
except Exception as e:
    print(e)
finally:
    file1 = open("listings.txt", "w")  
    file1.write(str(listings))
    file1.close()    


