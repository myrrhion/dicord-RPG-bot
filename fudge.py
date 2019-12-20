import base
import enum

class FudgeLadder(enum.IntEnum):
	TERRIBLE = -2
	POOR = -1
	MEDIOCRE = 0
	AVERAGE = 1
	FAIR = 2
	GOOD = 3
	GREAT = 4
	SUPERB = 5
	FANTASTIC = 6
	EPIC = 7
	LEGENDARY = 8
fudgeDie = base.Die([-1,-1,0,0,1,1])
fudgeMoji = [u"\u25A1",u"\u229E",u"\u229F"]
def fudge_roll():
	return (fudgeDie(),fudgeDie(),fudgeDie(),fudgeDie())
