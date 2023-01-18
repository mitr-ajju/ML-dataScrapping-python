
from bs4 import BeautifulSoup
import re
import requests

scrapingDate = "21-11-2022"
listings = set()

url = 'https://ipinfo.io'

username = 'dadepro'
password = 'dadepro_pwd'
proxy = f'http://{username}:{password}@all.dc.smartproxy.com:10001'
keysListing = { 'city', 'user_id', 'price', 'price_formatted', 'country', 'state', 'person_capacity', 'zipcode', 'cancellation_policy', 'reviews_count' }
listinghHost = {'id','first_name', 'last_name', 'picture_large_url', 'reviewee_count', 'response_rate', 'acceptance_rate', 'recommendation_count'}

#response = requests.get(url, proxies={'http': proxy, 'https': proxy})
listingid = "30883070"
#print(response.text)

url = "https://www.airbnb.com/api/v1/listings/" + listingid
payload={}
headers = {
'x-airbnb-api-key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20'
}
response = requests.request("GET", url, headers=headers, data=payload ,proxies={'http': proxy, 'https': proxy})
contentById = response.content

soupById = BeautifulSoup(contentById, 'html.parser')
print(soupById)

        