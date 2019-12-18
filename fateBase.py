import fudge
import re
import asyncio

class Aspect:
	def __init__(self,aspect_description,free_invokes=[]):
		self.description = aspect_description
		self.free_invokes = free_invokes
	def __str__(self):
		return self.description
	def __eq__(self,other):
		if isinstance(other,str) or isinstance(other,Aspect):
			return str(self) == str(other)
		return False
	def invoke(self,invoker):
		self.invoked = True
		if invoker not in self.free_invokes:
			return False
		self.free_invokes.remove(invoker)
		return True
	def refresh(self):
		self.invoked = False
	def __repr__(self):
		return f"Aspect(name: {self.description}, free invokations: {self.free_invokes})"

class StressBar:
	def __init__(self,name,maximum_stress):
		self.name = name
		self.stress_boxes = [False for x in range(maximum_stress)]
	def check(self,value,damage=0):
		if self.stress_boxes[value-1]:
			return damage
		self.stress_boxes[value-1] = True
		return max(0,damage-value)
	def refresh(self):
		for z in range(len(self.stress_boxes)):
			self.stress_boxes[z] = False
	def __repr__(self):
		return f"StressBar(name:{self.name},boxes:{self.stress_boxes})"

class Consequence:
	def __init__(self,value):
		self.name = None
		self.type = None
		self.value = value
	def take(self,name,con_type,damage=0):
		if self.name:
			return damage
		self.name = name
		self.type = con_type
		return max(damage-self.value,0)
	def heal(self,new_name):
		self.name = new_name
		self.type = "healing"
	def clear(self):
		self.name = None
		self.type = None

def get_aspect_list(text):
	aspects = {}
	for x in re.findall(r"\*\*([^*]*)\*\*",text):
		aspects[x] = Aspect(x)
	return aspects

class FateCharacterBase:
	def __init__(self,name,aspects:dict):
		self.name = name
		self.aspects = {}
		for x in aspects:
			self.aspects[x] = Aspect(x)

class FateBase(fudge.base.RollSystem):
	def __init__(self,dm,channel):
		fudge.base.RollSystem.__init__(self,dm)
		self.scene_aspects = {}
		self.channel = channel
		self.enemy_templates={}
		self.enemies = []
	async def send(self,text):
		return await self.channel.send(text)
	async def parse(self,command,playern):
		if playern == self.dm:
			if command.beginswith("!scene "):
				self.make_scene(command.replace("!scene ",1))
			if command.beginswith("!enemy "):
				self.spawn_enemy(command.replace("!enemy ",1))
		if command.beginswith("!overcome "):
			pass
