from CommandSourceInterface import CommandSourceInterface as CSI
import Queue
from SaltyBot import SaltyBot
from threading import Thread
import time

class Commander(object):
  messages = Queue.Queue()
  tickSpeed = .5 #in seconds
  slaves = []
  slaveThreads = []

  @property
  def numSlaves(self):
    return len(self.slaves)

  def __init__(self):
    pass

  def run(self):
    [bot.start() for bot in self.slaveThreads if bot is not None]
    while True:
      message = self.messages.get(True, 6000)
      if type(message) is str:
        print(message)
      time.sleep(self.tickSpeed)
    [bot.join() for bot in self.slaveThreads if bot is not None] #TODO: note that this doesn't do anything right now

  def addBot(self, player, factor, amount, email, password, waitTime):
    if type(waitTime) != int or waitTime < 0:
      print("Negative wait times are not possible.")
      exit()

    bot = SaltyBot(mainUrl="http://www.saltybet.com",
            betUrl="http://www.saltybet.com/ajax_place_bet.php",
            stateUrl="http://www.saltybet.com/state.json",
            waitTime=waitTime)

    wager = None
    wagerFunc = None

    if amount > 0:
      wagerFunc = bot.wagerAmount
      wager = amount
    elif factor > 0 and factor < 100:
      wagerFunc = bot.wagerPercent
      wager = factor / 100.0
    else:
      print("Please use either a positive amount or a factor between 1 and 100.")
      exit()

    try:
      bot.login(email=email, password=password)
    except Exception as e:
      print("Bad login for {0}.".format(email))
      return None

    bot.messagingFunc = self.messages.put
    self.slaves.append(bot)
    botThread = Thread(target=bot.run, args=(wagerFunc, player, wager))
    botThread.daemon = True
    self.slaveThreads.append(botThread)
