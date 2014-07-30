from __future__ import print_function
import re
import time
from BeautifulSoup import *
import json
import requests

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
    self.session = requests.session()
    self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'})

  def connect(self, email, password):
    try:
      self.session.get(self.MAIN_URL)
    except:
      raise BettingConnectionError("Unable to connect to server.")
    self.session.get(self.MAIN_URL + "/authenticate?signin=1")
    r = self.session.post(self.MAIN_URL + "/authenticate?signin=1", data={"email":email, "pword":password, "authenticate":"signin"})

    response = r.text

    if "Invalid Email or Password" in response:
      raise BadLoginError("Invalid email or password.")

    self.__connected = True

    return r

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
    try:
      response = self.session.post(self.BET_URL, data=json.dumps({
        "radio":"on",
        "selectedplayer":player,
        "wager":amount
      }))
      return response.text
    except:
      self.disconnect()
      raise BettingConnectionError("A connection was lost!")

  def __cachedResponse(self, cacheIndex, wrapper=None):
    if self.__requestCache[cacheIndex] is not None and (time.time() - self.__requestTimes[cacheIndex] < self.waitTimeSeconds):
      return self.__requestCache[cacheIndex]
    try:
      response = self.session.get(self.__requestURLs[cacheIndex])
      self.__requestCache[cacheIndex] = response.text
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
