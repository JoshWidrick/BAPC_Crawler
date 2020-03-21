# BAPC_Crawler
Crawler

## First time setup
Python 3.X is required to run

1. Go to: https://www.reddit.com/prefs/apps/ and register a new application to the reddit API. remember the clientID, clientSecret
2. Go to: https://www.mailgun.com/ and register for their free API 
3. Go to src/BAPC.py and fill out varibles with the information you got from the 2 websites you just registered on. 
Lines in question are (Line 43-45) for Reddit API info and (Line 94-97) for MailGun API info
4. pip install praw
5. Set up search criteria by editing src/parts.json (see below on how to set this up)

6. (Optional) the script will not search for PSU and Cooler deals as they are cheap and most people don't look for sales on them
you can turn this feature on by removing the following lines:
Line 58-61
Line 77-80

7. You can now run the script and it will email you all sales that match your criteria by typing:
```
python BAPC.py
```
in your command line terminal

## How to setup up criteria to search
Search Criteria is set in src/parts.json

here is how it works:
1. The criteria needs to end with a price tag as shown below in the example, this should be the current price of the item, the script will only look for items that are LESS than the price you enter here.
2. It is encouraged to have general specs in the criteria, avoid Model numbers and specific informations

    for example "AMD Ryzen 7 3700X" will search for any AMD Ryzen 7 3700X CPU regardless of model and brand.
    
    DO not put specific model information in the search criteria, the code is not optmized to handle that input.
    
    generalize it as much as possible.
    
    For example, instead of searching for "	Fractal Design Meshify C ATX Mid Tower Case"
    you should search for "ATX Mid Tower Case". the latter will yield results and email them to you.
   
3. this is what it should closely look like:
```
{
    "CPU":"AMD Ryzen 7 3700X $298.99",
    "Cooler":"Noctua NH-L9i 33.84 CFM CPU Cooler $0.00",    <--- DO NOT DO THIS
    "MOBO":"MSI B450 TOMAHAWK MAX $114.99",
    "RAM":"16GB DDR4 $67.99",
    "SSD":"500 GB $89.99",
    "GPU":"GeForce RTX 2060 $299.99",
    "Case":"ATX Mid Tower Case $99.98",
    "PSU":"ATX Power Supply $54.45"
}
```

## Additional info
The script crawls the r/buildapcsales, it sorts the subreddit by Hot and crawls 100 submissions, it also sorts the subreddit by New and crawls 200 submissions, you may increase the limit by editing line 52 and line 71

it ignores posts that are marked "out of stock" and "expired"
