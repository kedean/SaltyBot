from SaltyBot import SaltyBot
from getpass import getpass
from argparse import ArgumentParser

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("--player", dest="player", required=True, choices=[1, 2], type=int, help="Player number to place bets on.")
	parser.add_argument("--factor, -f", dest="factor", type=int, default=0, choices=range(1, 100), help="Percent of balance to bet each round, from 1 to 100.")
	parser.add_argument("--amount, -a", dest="amount", type=int, default=0, help="Flat amount to bet each round. Overrides percentage arguments.")
	parser.add_argument("--waitTime", dest="waitTime", type=int, default=5, help="Time to wait between server requests. Be nice to the server!")
	args = parser.parse_args()

	player = "player1" if args.player == 1 else "player2"
	factor = args.factor
	amount = args.amount
	waitTime = args.waitTime

	if waitTime < 0:
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

	email = raw_input("Email Address: ")
	password = getpass("Password: ")
	try:
		bot.login(email=email, password=password)
	except:
		print("Bad login.")
		exit()

	print("")

	while True:
		wagerFunc(player, wager)
		print("")