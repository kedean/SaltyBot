from __future__ import print_function
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

class BettingConnectionError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class SaltyInterface(object):
  MAIN_URL = "http://www.saltybet.com"
  BET_URL = "http://www.saltybet.com/ajax_place_bet.php"
  STATE_URL = "http://www.saltybet.com/state.json"
  waitTimeSeconds = 10.0

  __connected = False
  __requestURLs = [MAIN_URL, STATE_URL]
  __requestTimes = [0, 0] #order is main, state. More could be added later.
  __requestCache = [None, None]

  def __init__(self):
    self.__browser = mechanize.Browser()
    self.__browser.add_handler(PrettifyHandler())
    self.__browser.set_handle_robots(False)
    self.__browser.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36')]

  def connect(self, email, password):
    try:
      self.__browser.open(self.MAIN_URL)
    except:
      raise BettingConnectionError("Unable to connect to server.")
    #r1 = self.__browser.follow_link(text_regex=r"Sign In")
    self.__browser.open(self.MAIN_URL + "/authenticate?signin=1")
    #self.__browser.select_form(nr=0)
    #self.__browser["email"] = email
    #self.__browser["pword"] = password
    #self.__browser.submit()
    self.__browser.open(self.MAIN_URL + "/authenticate?signin=1", urlencode({"email":email, "pword":password}))

    response = self.__browser.response()
    if "Invalid Email or Password" in response.get_data():
      raise BadLoginError("Invalid email or password.")

    self.__connected = True

    return response

  def disconnect(self):
    self.__connected = False
    self.__requestTimes = [0, 0]
    self.__requestCache = [None, None]

  @property
  def connected(self):
    return self.__connected

  @property
  def status(self):
    return self.getState()["status"]
  @property
  def balance(self):
    return int(self.getMain().find("span", {"id":"balance"}).text.replace(",", ""))

  @property
  def player1(self):
    return self.getState()["p1name"]
  @property
  def player2(self):
    return self.getState()["p2name"]

  def wager(self, player, amount):
    data = urlencode({
      "radio":"on",
      "selectedplayer":player,
      "wager":amount
    })
    try:
      self.__browser.open(self.BET_URL, data)
      return self.__browser.response().get_data()
    except:
      self.disconnect()
      raise BettingConnectionError("A connection was lost!")

  def __cachedResponse(self, cacheIndex, wrapper=None):
    if self.__requestCache[cacheIndex] is not None and (time.time() - self.__requestTimes[cacheIndex] < self.waitTimeSeconds):
      return self.__requestCache[cacheIndex]
    try:
      self.__browser.open(self.__requestURLs[cacheIndex])
      self.__requestCache[cacheIndex] = self.__browser.response().get_data()
    except:
      self.disconnect()
      raise BettingConnectionError("A connection was lost!")
    finally:
      if wrapper is not None:
        assert callable(wrapper)
        self.__requestCache[cacheIndex] = wrapper(self.__requestCache[cacheIndex])
      self.__requestTimes[cacheIndex] = time.time()
      return self.__requestCache[cacheIndex]

  def getMain(self):
    return self.__cachedResponse(0, BeautifulSoup)

  def getState(self):
    return self.__cachedResponse(1, json.loads)
