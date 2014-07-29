from getpass import getpass
from argparse import ArgumentParser
import json
import time
from Commander import Commander

if __name__ == "__main__":
	defaultWaitTime = 10

	parser = ArgumentParser()
	parser.add_argument("--sourceFile", dest="source", type=str, help="JSON file containing player data. This will be used in addition to any command line parameters specifying another player.")
	parser.add_argument("--player", dest="player", default=None, choices=[1, 2], type=int, help="Player number to place bets on. If none is given, sourceFile is assumed to be used.")
	parser.add_argument("--factor, -f", dest="factor", type=int, default=0, choices=range(1, 100), help="Percent of balance to bet each round, from 1 to 100.")
	parser.add_argument("--amount, -a", dest="amount", type=int, default=0, help="Flat amount to bet each round. Overrides percentage arguments.")
	parser.add_argument("--waitTime", dest="waitTime", type=int, default=defaultWaitTime, help="Time to wait between server requests. Be nice to the server!")

	args = parser.parse_args()

	commander = Commander()

	if args.player is not None: #spawn a single player if one is specified
		player = "player1" if args.player == 1 else "player2"
		factor = args.factor
		amount = args.amount
		waitTime = args.waitTime
		try:
			email = raw_input("Email Address: ")
		except NameError:
			email = input("Email Address: ")
		finally:
			password = getpass("Password: ")
			commander.addBot(player, factor, amount, email, password, waitTime)

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

				commander.addBot(player, playerData["factor"], playerData["amount"], playerData["email"], playerData["password"], playerData["waitTime"])

	if commander.numSlaves == 0:
		print("No bots were spawned. Check your arguments or source file.")
	else:
		commander.run()
