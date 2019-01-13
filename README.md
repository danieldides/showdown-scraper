# Showdown Scraper
A quick, hacked together Python program for scraping the MLB Showdown cards off 
http://www.showdowncards.com/mlb/ and putting them into a CSV.

## Usage
1. Activate a virutalenv with Pipenv
` pipenv shell`
2. Install all deps (BS4, aiohttp)
`pipenv install`
3. Run the program as a module:
`python -m showdown-scraper`
4. For configuration:

```python -m showdown-scraper --help

usage: Showdown Scraper [-h] [--local LOCAL] [-c CONCURRENT] [-r RATE]
                        [-o OUT]

Scrape the showdown card site

optional arguments:
  -h, --help            show this help message and exit
  --local LOCAL         load local file for testing
  -c CONCURRENT, --concurrenct CONCURRENT
                        Number of concurrent connections
  -r RATE, --rate RATE  Requests per second target
  -o OUT, --outfile OUT
                        output file
```

## Notes
This isn't great code, but it should work.
