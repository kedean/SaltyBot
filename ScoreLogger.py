import SaltyInterface
import time

class Averager(object):
  support = {}
  matchCounts = {}
  #wagers = []

  def open(self, name1, name2, total1, total2):
    currentSupport = [self.support.get(name1, 0), self.support.get(name2, 0)]
    counts = (self.matchCounts.get(name1, 0), self.matchCounts.get(name2, 0))

    averages = ((currentSupport[0] + total1) / (counts[0] + 1),
                (currentSupport[1] + total2) / (counts[1] + 1))

    self.support[name2] = averages[0]
    self.support[name2] = averages[1]
    self.matchCounts[name1] = counts[0] + 1
    self.matchCounts[name2] = counts[1] + 1

    if currentSupport[0] > currentSupport[1]:
      return "1"
    elif currentSupport[0] < currentSupport[1]:
      return "2"
    else:
      return "3"

  def close(self, winner):
    pass

class PriorWinsTotaler(object):
  winCounts = {}

  def open(self, name1, name2, total1, total2):
    currentSupport = [self.winCounts.get(name1, 0), self.winCounts.get(name2, 0)]

    if currentSupport[0] > currentSupport[1]:
      return "1"
    elif currentSupport[0] < currentSupport[1]:
      return "2"
    else:
      return "3"

  def close(self, winnerName):
    self.winCounts[winnerName] = self.winCounts.get(winnerName, 0) + 1

if __name__ == "__main__":
  interface = SaltyInterface.SaltyInterface()
  interface.connect("bot123@mailinator.com", "botbot")
  interface.waitTimeSeconds = 2

  wait = 2

  averager = Averager()
  winTotaler = PriorWinsTotaler()

  with open("logging.txt", "w") as log:
    log.write("Winner, AverageSupported, TotalerSupported\n")
  rounds = 0
  while True:
    rounds += 1
    print("Round {0}".format(rounds))
    while interface.status != "open":
      time.sleep(wait)
    while interface.status == "open":
      time.sleep(wait)
    state = interface.getState()
    names = [state["p1name"], state["p2name"]]
    newSupport = [int(state["p1total"].replace(",","")), int(state["p2total"].replace(",", ""))]

    supporting = (averager.open(names[0], names[1], newSupport[0], newSupport[1]),
                  winTotaler.open(names[0], names[1], newSupport[0], newSupport[1])
                  )

    while interface.status == "locked":
      time.sleep(wait)

    winner = interface.status
    winnerName = names[0] if winner == "1" else names[1]

    averager.close(winnerName)
    winTotaler.close(winnerName)

    with open("logging.txt", "a") as log:
      log.write("{0}, {1}, {2}\n".format(winner, supporting[0], supporting[1]))


  #print zip(winners, averager.wagers)
