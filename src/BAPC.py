import json
import praw
import re
import requests

# Checks if the title contains the part you're looking for
def isNameInString(value, title):
    splitVal = value.split(' ')
    price = splitVal[-1]
    price = float(price[1:])
    splitVal = splitVal[:-1]
    splitValCount = len(splitVal)
    totalVal = 0
    for subVal in splitVal:
        if subVal in title:
            totalVal = totalVal + 1
            
    if totalVal < splitValCount:
        return False
    if not isPriceBetter(price, title):
        return False
    return True

# Checks if the sale price is lower than the current price
def isPriceBetter(CurrentPrice, title):
    r = re.compile(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})')
    newPrice = r.findall(title)

    if len(newPrice) == 0:
        return False
    newPrice = float(newPrice[0])
    if newPrice >= CurrentPrice:
        return False
    return True

path = './parts.json'

with open(path) as json_file:
    json_data = json.load(json_file)

# Register your own app at: https://www.reddit.com/prefs/apps/
# copy the client_id, secret, password, username and useragent from reddit
reddit = praw.Reddit(client_id='YOUR_REDDIT_CLIENT_ID_GOES_HERE',
                     client_secret="YOUR_REDDIT_CLIENT_SECRET_GOES_HERE", password='YOUR_REDDIT_PASSWORD_GOES_HERE',
                     user_agent='BAPC VectorBot', username='YOUR_REDDIT_USERNAME_GOES_HERE')

subreddit = reddit.subreddit('buildapcsales')

submissionList = {}

# Crawls subreddit sorted by new
for submission in subreddit.new(limit=200):
    flair = submission.link_flair_text
    if(flair == "Out Of Stock"):
        continue
    if("Expired" in flair):
        continue
    if(flair == "PSU"):                     # REMOVE THIS LINE IF YOU WANT TO FIND PSU
        continue
    if(flair == "Cooler"):                  # REMOVE THIS LINE IF YOU WANT TO FIND A COOLER
        continue
    for(part, value) in json_data.items():
        if(flair != part):
            continue
        else:
            title = submission.title
            if(isNameInString(value, title)):
                submissionList[title] = submission.url

# Crawls subreddit sorted by hot
for submission in subreddit.hot(limit=100):
    flair = submission.link_flair_text
    if(flair == "Out Of Stock"):
        continue
    if("Expired" in flair):
        continue
    if(flair == "PSU"):                 # REMOVE THIS LINE IF YOU WANT TO FIND PSU
        continue
    if(flair == "Cooler"):              # REMOVE THIS LINE IF YOU WANT TO FIND A COOLER
        continue
    for(part, value) in json_data.items():
        if(flair != part):
            continue
        else:
            title = submission.title
            if(isNameInString(value, title)):
                submissionList[title] = submission.url


#Register at: https://www.mailgun.com/
#Fill: API URL, API Key, MailGun Address and To fields below
def send_simple_message(data):
	return requests.post(
		"YOUR_API_URL_GOES_HERE",
		auth=("api", "YOUR_API_KEY_GOES_HERE"),
		data={"from": "Mailgun Sandbox <YOUR_MAILGUN_DOMAIN_ADDRESS_GOES_HERE>",
			"to": ["YOUR_EMAIL_ADDRESS_GOES_HERE"],
			"subject": "BAPC Digest",
			"text": data})


data = "The following items were found to be on sale on r/buildapcsales:\n"
data = data + "----------------------------------------------------\n"
for(title, link) in submissionList.items():
    data = data + "Item: %s \n" % title + "Link: %s \n" % link
    data = data + "----------------------------------------------------\n"

# function call to send you an email if sales are found
send_simple_message(data)