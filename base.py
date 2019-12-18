from random import Random
import asyncio
r = Random()
class RollSystem:
	def __init__(self, dm):
		self.dm = dm
		self.players = {}
		self.nicks = {}
	async def parse(self, command, playern):
		raise NotImplementedError("Can't use the base system, sucker")
	async def join(self,playern):
		raise NotImplementedError("Can't use the base system, sucker")
	async def remove(self,playern):
		raise NotImplementedError("Can't use the base system, sucker")


class Die:
	def __init__(self,potential_results):
		"""create the dice set you want to roll"""
		self.pot_results = potential_results
	def __call__(self):
		"""Returns a random roll of the dice"""
		return r.choice(self.pot_results)
