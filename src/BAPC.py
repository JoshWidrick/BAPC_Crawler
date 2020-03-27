import json
import praw
import re
import requests
import asyncio
from config import Config


class BAPC:
    parts = {}
    submission_list = {}

    def __init__(self):

        # load in config, and all associated info
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

        self.blacklisted_flairs = self.config.get_option('extras', 'blacklisted_flairs')

        self.subreddit = self.reddit.subreddit('buildapcsales')

    async def is_name_in_string(self, value, title):
        if "in-store" in title:
            return False
        split_val = value.split(' ')
        price = split_val[-1]
        price = float(price[1:])
        split_val = split_val[:-1]
        split_val_count = len(split_val)
        total_val = 0

        for sub_val in split_val:
            if sub_val in title:
                total_val = total_val + 1

        return False if total_val < split_val_count or not await self.is_price_better(price, title) else True

    @staticmethod
    async def is_price_better(current_price, title):
        r = re.compile(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})')
        new_price = r.findall(title)
        return False if len(new_price) == 0 or float(new_price[0]) >= current_price else True

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
        for (title, link) in self.submission_list.items():
            data = data + "Item: %s \n" % title + "Link: %s \n" % link
            data = data + "----------------------------------------------------\n"
        return data

    async def crawl_new(self):
        for submission in self.subreddit.new(limit=200):
            # TODO add recommended 'Out Of Stock' and 'Expired' flairs to README.md

            flair = submission.link_flair_text
            if flair in self.blacklisted_flairs:
                continue
            for (part_type, value) in self.parts.items():
                for part in value:
                    if flair != part_type:
                        continue
                    else:
                        title = submission.title
                        if await self.is_name_in_string(part, title):
                            self.submission_list[title] = submission.url

    async def crawl(self):
        task = asyncio.create_task(self.crawl_new())
        for submission in self.subreddit.hot(limit=100):
            flair = submission.link_flair_text
            if flair in self.blacklisted_flairs:
                continue
            for (partType, value) in self.parts.items():
                for part in value:
                    if flair != partType:
                        continue
                    else:
                        title = submission.title
                        if await self.is_name_in_string(part, title):
                            self.submission_list[title] = submission.url
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
