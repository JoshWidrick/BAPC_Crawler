import json
import praw
import re
import requests
import asyncio
from config import Config


class BAPC:

    reddit = None
    parts = {}
    submissionList = {}

    def __init__(self):

        self.config = Config()

        self.reddit = praw.Reddit(client_id=self.config.get_option('reddit', 'client_id'),
                                  client_secret=self.config.get_option('reddit', 'client_secret'),
                                  username=self.config.get_option('reddit', 'username'),
                                  password=self.config.get_option('reddit', 'password'),
                                  user_agent=self.config.get_option('reddit', 'user_agent'))

        self.api_url = self.config.get_option('api', 'api_url')
        self.api_key = self.config.get_option('api', 'api_key')
        self.from_text = f"Mailgun Sandbox <postmaster@{self.config.get_option('api', 'mailgun_domain')}.mailgun.org>"
        self.to_email = self.config.get_option('api', 'email_address')
        self.subject = self.config.get_option('api', 'emails_subject')

        self.subreddit = self.reddit.subreddit('buildapcsales')

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
        for (title, link) in self.submissionList.items():
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
            for (partType, value) in self.parts.items():
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
            for (partType, value) in self.parts.items():
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


if __name__ == '__main__':
    bapc = BAPC()
    asyncio.run(bapc.begin())
