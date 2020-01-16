from random import Random
import asyncio
r = Random()
class RollSystem:
	def __init__(self, dm,channel):
		self.dm = dm
		self.channel = channel
		self.players = {}
		self.nicks = {}
	async def send(self,text):
		return await self.channel.send(text)
	async def parse(self, command, playern):
		raise NotImplementedError("Can't use the base system, sucker")
	async def join(self,playern):
		raise NotImplementedError("Can't use the base system, sucker")
	async def remove(self,playern):
		raise NotImplementedError("Can't use the base system, sucker")
	async def set_nickname(self, command, playern):
                self.nicks[command] = playern
                await self.send("Successfully set Nickname")
                
class CancelError(Exception):
	def __init__(self, arg):
		self.strerror = arg
		self.args = {arg}

class Die:
	def __init__(self,potential_results):
		"""create the dice set you want to roll"""
		self.pot_results = potential_results
	def __call__(self):
		"""Returns a random roll of the dice"""
		return r.choice(self.pot_results)
