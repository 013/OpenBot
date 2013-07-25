#!/usr/bin/python
import sys
import urllib2
import csv
import praw
import signal
from time import gmtime, strftime, sleep
import pdb
from urlparse import urlparse

class oBot:
	def __init__(self, username=None, password=None):
		self.username, self.password = username, password
		self.gLimit = 10
		self.getsAttr = ['get_controversial', 'get_controversial_from_all', 'get_controversial_from_day', 'get_controversial_from_hour', 'get_controversial_from_month', 'get_controversial_from_week', 'get_controversial_from_year', 'get_new', 'get_rising', 'get_top', 'get_top_from_all', 'get_top_from_day', 'get_top_from_hour', 'get_top_from_month', 'get_top_from_week', 'get_top_from_year']
		self.running = True
		self.done = {} # Populated by the importLog() function
		self.importLog()
	
	def run(self):
		self.r = praw.Reddit(user_agent='Search /r/opendirectories for dead links')
		self.r.login(self.username, self.password)
		self.subreddit = self.r.get_subreddit('opentest')
		while self.running:
			for att in self.getsAttr:
				subredGet = getattr(self.subreddit, att)	
				for submission in subredGet(limit=self.gLimit):
					if submission.domain != 'self.opendirectories' and submission.id not in self.done:
						url = submission.url.replace('.nyud.net', '')
						self.done[submission.id] = strftime('%H:%M:%S', gmtime())
						workingLink = False
						try:
							response = urllib2.urlopen(url)
						except urllib2.HTTPError, e:
							message = "This URL failed to open with the following HTTP Status code: {0}".format(e.code)
						except urllib2.URLError, e:
							message = "This URL failed to open with the following error: {0}".format(e.args)
						else:
							workingLink = True
							print url
						if not workingLink:
							flatCom = praw.helpers.flatten_tree(submission.comments)
							# Check if we have made any previous comments
							prevComment = False
							for comment in flatCom:
								 if str(comment.author).lower() == self.username.lower():
									 prevComment = True
									 break
							if not prevComment:
								submission.add_comment(message)
						#pdb.set_trace()
					#print submission.id
					#print submission.url
					#print submission.title
					#print submission.permalink

			sleep(5)
			self.running = False

	def importLog(self):
		try:
			file = open('lastscan.csv', 'rb')
		except:
			open('lastscan.csv', "w").close()
		finally:
			file = open('lastscan.csv', 'rb')
			reader = csv.reader(file, delimiter=',')
			reader = list(reader)
			for row in reader:
				self.done[row[0]] = row[1]
			file.close()

	def createLog(self):
		file = open('lastscan.csv', 'wb')
		writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		for id, time in self.done.items():
			writer.writerow([id, time])
		file.close()

	def signal_handler(self, signal, frame):
		print "Saving results and exiting... :)"
		self.createLog()
		sys.exit(0)

	def nyud_appender(self, url):
		"""
		Checks if a given submission URL ends with .nyud.net, if not it adds it.
		Returns "False" if URL already is cached and there is no need to post a comment.

		This function requires urlparse
		"""
		if not "nyud.net" in url:
			parsed = urlparse(url)
			cachedURL = parsed.netloc + ".nyud.net" + parsed.path + parsed.params + parsed.query + parsed.fragment
			return cachedURL
		else:
			#URL has .nyud.net
			return False





if __name__ == "__main__":
	bot = oBot('OpenBot')
	signal.signal(signal.SIGINT, bot.signal_handler)
	bot.run()
