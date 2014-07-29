from __future__ import print_function
import re
import time
import mechanize
from BeautifulSoup import *
from urllib import urlencode
import json
import SaltyInterface

class SaltyBot(object):
	waitTime = 5
	balance = None
	messagingFunc = print
	__email = None

	def __init__(self, waitTime=5):
		self.__interface = SaltyInterface.SaltyInterface()
		self.__interface.waitTimeSeconds = waitTime

		self.waitTime = waitTime

	def login(self, email, password):
		self.__interface.connect(email, password)
		self.__email = email

	def isBettingOpen(self):
		try:
			status = self.__interface.status
		except BettingConnectionError:
			self.messagingFunc("{0} was disconnected.".format(self.__email))
			raise
		else:
			return (status == "open")

	def wagerAmount(self, player, amount=0):
		self.messagingFunc("{0} is waiting for bets to open...".format(self.__email))

		while not self.isBettingOpen(): #loop til the betting is open again
			time.sleep(self.waitTime)

		newBalance = self.__interface.balance
		if self.balance is not None:
			diff = newBalance - self.balance
			self.messagingFunc("{0} {1} the last bet.".format(self.__email, "won" if diff > 0 else "lost"))
		self.balance = newBalance

		try:
			self.__interface.wager(player, amount)
		except BettingConnectionError:
			self.messagingFunc("{0} was disconnected.".format(self.__email))
			raise
		else:
			self.messagingFunc("{0} wagered ${1} on {2}".format(self.__email, amount, self.__interface.player1 if player == "player1" else self.__interface.player2))
			self.messagingFunc("{0}'s current balance: ${1}".format(self.__email, self.balance))

			while self.isBettingOpen(): #wait til betting is closed again to prevent rebetting
				time.sleep(self.waitTime)

	def wagerPercent(self, player, factor):
		assert factor < 1 and factor > 0
		balance = self.__interface.balance
		amount = int(balance * factor)

		self.wagerAmount(player, amount)

	def disconnect(self):
		self.__interface.disconnect()
	@property
	def connected(self):
		return self.__interface.connected

	def run(self, func, player, wager):
		while self.connected:
			func(player, wager)
