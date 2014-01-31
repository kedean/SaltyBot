from SaltyBot import SaltyBot
from getpass import getpass
from argparse import ArgumentParser
from threading import Thread
import json

def spawn(player, factor, amount, email, password, waitTime):
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
		exit()

	print("")

	botThread = Thread(target=bot.run, args=(wagerFunc, player, wager))
	botThread.daemon = True
	botThread.start()

	return botThread

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("--sourceFile", dest="source", type=str, help="JSON file containing player data. This will be used in addition to any command line parameters specifying another player.")
	parser.add_argument("--player", dest="player", default=None, choices=[1, 2], type=int, help="Player number to place bets on. If none is given, sourceFile is assumed to be used.")
	parser.add_argument("--factor, -f", dest="factor", type=int, default=0, choices=range(1, 100), help="Percent of balance to bet each round, from 1 to 100.")
	parser.add_argument("--amount, -a", dest="amount", type=int, default=0, help="Flat amount to bet each round. Overrides percentage arguments.")
	parser.add_argument("--waitTime", dest="waitTime", type=int, default=5, help="Time to wait between server requests. Be nice to the server!")
	
	args = parser.parse_args()

	bots = []

	if args.player is not None: #spawn a single player if one is specified
		player = "player1" if args.player == 1 else "player2"
		factor = args.factor
		amount = args.amount
		waitTime = args.waitTime

		email = raw_input("Email Address: ")
		password = getpass("Password: ")

		bots.append(spawn(player, factor, amount, email, password, waitTime))

	if args.source:
		with open(args.source, "r") as playerHandle:
			players = json.load(playerHandle)
			for playerData in players:
				if "player" not in playerData or playerData["player"] not in [1,2]:
					print "Player number must be either 1 or 2."
					continue
				player = "player1" if playerData["player"] == 1 else "player2"

				if "amount" not in playerData:
					playerData["amount"] = 0
				if "factor" not in playerData:
					playerData["factor"] = 0
				if "email" not in playerData:
					print "Please give a valid email."
					continue
				if "password" not in playerData:
					print "Please give a valid password."
					continue
				if "waitTime" not in playerData:
					playerData["waitTime"] = 5

				bots.append(spawn(player, playerData["factor"], playerData["amount"], playerData["email"], playerData["password"], playerData["waitTime"]))

	if len(bots) == 0:
		print("No bots were spawned. Check your arguments or source file.")
	else:
		while len(bots) > 0: #loop til we're out of bots
			bots = [bot for bot in bots if bot.isAlive()] #if a bot has terminated, remove it from the queue

