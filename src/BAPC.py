import json
import praw
import re
import requests
import asyncio

class BAPC:

	def __init__(self):
		self.reddit = reddit = praw.Reddit(client_id='YOUR_REDDIT_CLIENT_ID_GOES_HERE',
							client_secret="YOUR_REDDIT_CLIENT_SECRET_GOES_HERE", password='YOUR_REDDIT_PASSWORD_GOES_HERE',
							user_agent='vectorbot', username='YOUR_REDDIT_USERNAME_GOES_HERE')
							
		self.api_url = "YOUR_MAILGUN_DOMAIN_GOES_HERE"
		self.api_key = "YOUR_API_KEY_GOES_HERE"
		self.from_text = "Mailgun Sandbox <postmaster@YOUR_DOMAIN_NAME_GOES_HERE.mailgun.org>"
		self.to_email = "YOU_EMAIL_ADDRESS_GOES_HERE"
		self.subject = "BAPC Digest"
		###########
		self.subreddit = reddit.subreddit('buildapcsales')
		self.parts = {}
		self.submissionList = {}
		###########

	async def is_name_in_string(self, value, title):
		if "in-store" in title:
			return False
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
		if not await self.is_price_better(price, title):
			return False
		return True


	@staticmethod
	async def is_price_better(current_price, title):
		r = re.compile(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})')
		new_price = r.findall(title)

		if len(new_price) == 0:
			return False
		new_price = float(new_price[0])
		if new_price >= current_price:
			return False
		return True

	async def send_simple_message(self, data):
		return requests.post(
			self.api_url,
			auth=("api", self.api_key),
			data={"from": self.from_text,
				"to": [self.to_email],
				"subject": self.subject,
				"text": data})

	async def print_content(self):
		data = "The following items were found to be on sale on r/buildapcsales:\n"
		data = data + "----------------------------------------------------\n"
		for(title, link) in self.submissionList.items():
			data = data + "Item: %s \n" % title + "Link: %s \n" % link
			data = data + "----------------------------------------------------\n"
		return data

	async def crawl_new(self):
		for submission in self.subreddit.new(limit=200):
			flair = submission.link_flair_text
			if flair == "Out Of Stock":
				continue
			if "Expired" in flair:
				continue
			if flair == "PSU":
				continue
			if flair == "Cooler":
				continue
			for(partType, value) in self.parts.items():
				for part in value:
					if flair != partType:
						continue
					else:
						title = submission.title
						if await self.is_name_in_string(part, title):
							self.submissionList[title] = submission.url

	async def crawl(self):
		task = asyncio.create_task(self.crawl_new())
		for submission in self.subreddit.hot(limit=100):
			flair = submission.link_flair_text
			if flair == "Out Of Stock":
				continue
			if "Expired" in flair:
				continue
			if flair == "PSU":
				continue
			if flair == "Cooler":
				continue
			for(partType, value) in self.parts.items():
				for part in value:
					if flair != partType:
						continue
					else:
						title = submission.title
						if await self.is_name_in_string(part, title):
							self.submissionList[title] = submission.url
		await task
		data = await self.print_content()
		result = await self.send_simple_message(data)
		print(result)

	async def begin(self):
		path = './parts.json'
		delay = 14400
		with open(path) as json_file:
			self.parts = json.load(json_file)
		print("Started Crawling...")
		await self.crawl()
		print("Done! going to sleep for {} seconds".format(delay))
		await asyncio.sleep(delay)
		await self.begin()

bapc = BAPC()
asyncio.run(bapc.begin())


