import re
import time
import mechanize
from BeautifulSoup import *
from urllib import urlencode
import json

class PrettifyHandler(mechanize.BaseHandler):
    def http_response(self, request, response):
        if not hasattr(response, "seek"):
            response = mechanize.response_seek_wrapper(response)
        # only use BeautifulSoup if response is html
        if response.info().dict.has_key('content-type') and ('html' in response.info().dict['content-type']):
            soup = BeautifulSoup(response.get_data())
            response.set_data(soup.prettify())
        return response

class BadLoginError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SaltyBot(object):
	__browser = None
	__state = None
	waitTime = 5
	balance = None

	def __init__(self, mainUrl, betUrl, stateUrl, waitTime=5):
		self.__browser = mechanize.Browser()
		self.__browser.add_handler(PrettifyHandler())
		self.__browser.set_handle_robots(False)
		self.__browser.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36')]

		self.mainUrl = mainUrl
		self.betUrl = betUrl
		self.stateUrl = stateUrl
		self.waitTime = waitTime

	def login(self, email, password):
		self.__browser.open(self.mainUrl)
		r1 = self.__browser.follow_link(text_regex=r"Sign In")
		self.__browser.select_form(nr=0)
		self.__browser["email"] = email
		self.__browser["pword"] = password
		self.__browser.submit()

		response = self.__browser.response()
		if "Invalid Email or Password" in response.get_data():
			raise BadLoginError("Invalid email or password.")

	def isBettingOpen(self):
		self.__browser.open(self.stateUrl)
		self.__state = json.loads(self.__browser.response().get_data())
		return (self.__state["status"] == "open")

	def getBalance(self):
		self.__browser.open(self.mainUrl)
		soup = BeautifulSoup(self.__browser.response().get_data())
		return int(soup.find("span", {"id":"balance"}).text)

	def wagerAmount(self, player, amount=0):
		data = urlencode({
			"radio":"on",
			"selectedplayer":player,
			"wager":amount
		})

		print("Waiting for bets to open...")

		while not self.isBettingOpen(): #loop til the betting is open again
			time.sleep(self.waitTime)

		newBalance = self.getBalance()
		if self.balance is not None:
			diff = newBalance - self.balance
			print("You {0} the last bet.".format("won" if diff > 0 else "lost"))
		self.balance = newBalance

		self.__browser.open(self.betUrl, data)
		print("Wagered ${0} on {1}".format(amount, self.__state["p1name" if player == "player1" else "p2name"]))
		
		print("Current Balance: ${0}".format(self.balance))

		while self.isBettingOpen(): #wait til betting is closed again to prevent rebetting
			time.sleep(self.waitTime)

		winnings = self.__state["p1total" if player == "player1" else "p2total"]
		print("Potential Winnings: ${0}".format(winnings))

	def wagerPercent(self, player, factor):
		assert factor < 1 and factor > 0
		balance = self.getBalance()
		amount = int(balance * factor)

		self.wagerAmount(player, amount)