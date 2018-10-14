from bs4 import BeautifulSoup
import requests
import sys
import os
import json

class Github:

    def __init__(self, url):
        self.endpoint = 'https://api.github.com/'
        self.raw_url = None
        self.url, self.owner, self.repo = self._parse(url)
        self.data = {
                'owner':self.owner,
                'repo':self.repo,
                'avatar':None,
                'description':None,
                'topics':None,
                'watchers':None,
                'stars':None,
                'forks':None,
                'commits':None,
                'branches':None,
                'releases':None,
                'contributors':None,
                'license':None,
                'latest-commit':None,
                'url':self.raw_url,
                'git-url':f'{self.raw_url}.git',
                'readme':None,
                'shields':None,
                'languages':None,
                }

    def _parse(self, url):
        self.raw_url = url.partition('.git')[0]
        url = self.raw_url[19:]
        if url[-1] == '/':
            url = url[:-1]
        owner, sep, repo = url.partition('/')
        return((url, owner, repo))

    def _fetch_repo(self):
        r = requests.get(self.raw_url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            self.data['avatar'] = soup.find("meta", attrs={"property":"og:image"})['content']
            self.data['description'] = soup.find("meta", attrs={"property":"og:description"})['content']
            if self.data['description'].endswith('development by creating an account on GitHub.'):
                self.data['description'] = self.data['description'][:-61-len(f"{self.owner}/{self.repo}")]
            self._set_topics(soup)
            self._set_repo_details(soup)
            self._set_numbers_summary(soup)
            self._set_latest_commit(soup)
            # @TODO parse encoded readme content to grab shields
            # self._set_readme()
            self._set_languages()

    def _set_readme(self):
        r = requests.get(f"{self.endpoint}repos/{self.owner}/{self.repo}/readme")
        if r.status_code == 200:
            self.data['readme'] = r.json()

    def _set_topics(self, soup):
        topics = soup.find("div", attrs={"class":"list-topics-container f6"})
        if topics:
            self.data['topics'] = [topic.text.strip() for topic in topics.find_all('a')]

    def _set_repo_details(self, soup):
        details = soup.find("div", attrs={"class":"repohead-details-container clearfix container"}).find_all('a', attrs={"class":"social-count"})
        self.data['watchers'] = details[0].text.strip()
        self.data['stars'] = details[1].text.strip()
        self.data['forks'] = details[2].text.strip()
    
    def _set_numbers_summary(self, soup):
        numbers = soup.find("ul", attrs={"class":"numbers-summary"})
        if numbers:
            summary = [li.text.strip().split()[0] for li in numbers.find_all('li')]
            self.data['commits'] = summary[0]
            self.data['branches'] = summary[1]
            self.data['releases'] = summary[2]
            self.data['contributors'] = summary[3]
            if len(summary) == 5:
                self.data['license'] = summary[4]
    
    def _set_latest_commit(self, soup):
        latest = soup.find('div', attrs={'class':'commit-tease'})
        if latest:
            latest_commit = {}
            commit_sha = latest.find('div', attrs={"class":"no-wrap"}).extract()
            latest_commit['latest'] = " ".join(commit_sha.text.strip().split())
            message = latest.find_all('a')
            latest_commit['author_avatar'] = message[0].img['src']
            commit = [elem.text.strip() for elem in message[1:]]
            latest_commit['author'] = commit[0]
            latest_commit['message'] = "".join([m for m in commit[1:]])
            self.data['latest-commit'] = latest_commit

    def _set_languages(self):
        r = requests.get(f"{self.endpoint}repos/{self.owner}/{self.repo}/languages")
        if r.status_code == 200:
            self.data['languages'] = r.json()

    def preview(self):
        self._fetch_repo()
        return self.data

host = {
        'https://github.com/':Github,
     }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[Error] Git repo web url or hosted git url required\ni\
                \tex.   https://github.com/<owner>/<repo>")
    url = sys.argv[1]
    for valid in host.keys():
        if url.startswith(valid):
            p = host[valid](url)
            print(p.preview())
