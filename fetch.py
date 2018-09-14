import requests
import json
from bs4 import BeautifulSoup

class Fetch:

	def __init__(self, url):
		self.url = url
		self.r = requests.get(url)

	def get_description(self):
		if self.r.status_code == 200:
			soup = BeautifulSoup(self.r.content, 'html5lib')
			return soup.find_all('meta', attrs={"property":"og:description"})

if __name__ == "__main__":
	url = "http://www.github.com/adagiox/hn-whos-hiring-search"
	f = Fetch(url)
	for x in f.get_description():
		print(x)
