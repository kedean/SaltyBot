SaltyBot
========

A bot that consistently bets on the fake gambling website saltybet.com

Usage
========

usage: main.py [-h] [--sourceFile SOURCE] [--player {1,2}]
               [--factor, -f {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99}]
               [--amount, -a AMOUNT] [--waitTime WAITTIME]

optional arguments:
  -h, --help            show this help message and exit
  --sourceFile SOURCE   JSON file containing player data. This will be used in
                        addition to any command line parameters specifying
                        another player.
  --player {1,2}        Player number to place bets on. If none is given,
                        sourceFile is assumed to be used.
  --factor, -f {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99}
                        Percent of balance to bet each round, from 1 to 100.
  --amount, -a AMOUNT   Flat amount to bet each round. Overrides percentage
                        arguments.
  --waitTime WAITTIME   Time to wait between server requests. Be nice to the
                        server!

Dependencies
========

Python 2.7+, BeautifulSoup, mechanize

Source Files
========

A source file can be passed with all the information to spawn players. The source is specificed as a JSON array of objects with the required features.

Example:

[
{
  "player":1,
  "factor":25,
  "email":"address@email.com",
  "password":"hunter2"
}
]

This will create one bot, which always bets on player 1 with 25% of their current cash. Usable attributes are:

- player
- factor
- amount
- email
- password
- waitTime
