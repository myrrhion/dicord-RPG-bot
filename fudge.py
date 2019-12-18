import base
import enum

class FudgeLadder(enum.IntEnum):
	MEDIOCRE = 0
	AVERAGE = 1
	FAIR = 2
	GOOD = 3
	GREAT = 4
fudgeDie = base.Die([-1,-1,0,0,1,1])
fudgeMoji = [u"\u25A1",u"\u229E",u"\u229F"]
def fudge_roll():
	return (fudgeDie(),fudgeDie(),fudgeDie(),fudgeDie())
