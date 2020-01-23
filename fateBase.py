import fudge
import re
import asyncio
import base
from rpgbot import client
class Aspect:
	def __init__(self,parent,aspect_description,free_invokes=[]):
		self.owner = parent
		parent.add_aspect(self)
		self.description = aspect_description
		self.free_invokes = free_invokes
		self.invoked = []
	def __str__(self):
		return self.description
	def __eq__(self,other):
		if isinstance(other,str) or isinstance(other,Aspect):
			return str(self) == str(other)
		return False
	def invoke(self,invoker):
		if invoker not in self.free_invokes:
			if isinstance(self.owner,FatePlayer) and invoker != self.owner:
				self.owner.invoke_fp += 1
			self.invoked.append(invoker)
			return False
		self.free_invokes.remove(invoker)
		return True
	def refresh(self):
		self.invoked = []
	def __del__(self):
		print(f"deleted {str(self)}")
		self.owner.remove_aspect(self)
	def __repr__(self):
		return f"{self.__class__.__name__}(name: {self.description}, free invokations: {[str(x) for x in self.free_invokes]})"
	

	

class SignatureAspect(Aspect):
	@classmethod
	def upgrade(cls,original):
		return cls(original.owner,original.description,[original.owner])

class HasAspects:
	def add_aspect(self,aspect:Aspect):
		raise NotImplementedError("Not Implemented by default")
	def remove_aspect(self,aspect:Aspect):
		raise NotImplementedError("Not Implemented by default")
	def get_aspect(self,aspect:Aspect):
		raise NotImplementedError("Not Implemented by default")
	def refresh_aspects(self):
		raise NotImplementedError("Not Implemented by default")

class StressBar:
	def __init__(self,parent,name,maximum_stress):
		self.character = parent
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
	def __str__(self):
		return self.name
	def __eq__(self,other):
		return self.name == str(other)

class Skill:
	def __init__(self,parent,name,actions:dict,value:int):
		self.character = parent
		self.name = name
		self.actions = actions
		self.value = int(value)
		parent.skills[name] = self
	def __str__(self):
		return self.name
	def __getkey__(self,key):
		return self.actions[key]
	def __int__(self):
		return self.value
	def __iter__(self):
		return self.actions.__iter__()
	def can_do(self,action):
		for x in self:
			if x.startswith(action):
				return True
		return False
	def __repr__(self):
		return f"Skill(name: {self.name}, value: {self.value}, actions: {repr(self.actions)})"

class Consequence:
	def __init__(self,parent,value,exclusive=False):
		self.character = parent 
		self.name = None
		self.type = None
		self.exclusive = exclusive
		self.value = value
	def take(self,name,con_type,damage=0,who=None):
		if self.name:
			return damage
		self.name = Aspect(self.parent,name,free_invokes=[who])
		self.type = con_type
		return max(damage-self.value,0)
	def __bool__(self):
		return bool(self.name)
	def __str__(self):
		return self.name
	def __int__(self):
		return self.value
	def heal(self,new_name):
		del self.name
		self.name = Aspect(self.parent,new_name)
		self.type = "healing"
	def clear(self):
		del self.name
		self.name = None
		self.type = None
	def __repr__(self):
		return f"Consequence(name: {self.name}, type:{self.type}, value:{self.value})"

def get_aspect_list(text,owner):
	aspects = {}
	for x in re.findall(r"\*\*([^*]*)\*\*",text):
		aspects[x] = Aspect(owner,x)
	return aspects


class Stunt:
	def __init__(self,parent,name,description,**kwargs):
		self.character = parent
		self.description = description
		self.name = name
	def __str__(self):
		return self.name
	def __repr__(self):
		return f"{self.__class__.__name__}(name: {self.name}, description: {self.description})"
class ImproveStunt(Stunt,Skill):
	def __init__(self,parent,name,description,associated_skill,actions:list,**kwargs):
		Stunt.__init__(self,parent,name,description)
		self._skill = parent.skills[associated_skill]
		for a in actions:
			if a not in self._skill.actions:
				raise ValueError("NOPE")
		self.actions = actions
		self._boost = 2 // len(actions)
		parent.skills[str(self)] = self
	def __int__(self):
		return int(self._skill) + self._boost
	def __repr__(self):
		return f"ImproveStunt(name: {self.name}, description: {self.description})"
class ExtendStunt(Stunt):
	def __init__(self,parent,name,description,associated_skill,action,**kwargs):
		Stunt.__init__(self,parent,name,description)
		self._skill = associated_skill
		self.action = action
		parent.skills[str(self)] = self
	def __int__(self):
		return int(self._skill)
	def can_do(self,action):
		return self.action.beginswith(action)
class SignatureAspectStunt(Stunt):
	def __init__(self,parent,name,**kwargs):
		Stunt.__init__(self,parent,name,"Signature Aspect")
		self.character = parent
		self.name = name
		newb = parent.get_aspect(name)
		parent.remove_aspect(newb)
		SignatureAspect.upgrade(newb)

class HasFatePoints(HasAspects):
	def __init__(self,fp=0):
		self.fate_points = fp
		self.invoke_fp = 0
		self.consequence_fp = 0

class FatePlayer(HasFatePoints):
	def __init__(self,player,**kwargs):
		HasFatePoints.__init__(self,kwargs.get("refresh",0))
		self.player = player

class FateCharacterBase(HasAspects):
	def __init__(self,player,**kwarg):
		self.name = kwarg.get("name")
		self.player = player
		self.char_aspects = []
		self.skills = {}
		self.consequences = [Consequence(**x) for x in kwarg.get("consequences",[])]
		self.stress_tracks = [StressBar(**x) for x in kwarg.get("stress bars",[])]
	def add_aspect(self,aspect:Aspect):
		self.char_aspects.append(aspect)
	def remove_aspect(self,aspect):
		self.char_aspects.remove(aspect)
	def get_aspect(self,aspect_name:str):
		if aspect_name in self.char_aspects:
			return self.char_aspects[self.char_aspects.index(aspect_name)]
		else:
			return None
class StoredRoll:
	def __init__(self, who, roll=0, bonus=0):
		self.who = who
		self.roll = roll
		self.bonus = bonus
		self.invokes = 0
		self.final = False
	def __iadd__(self,other):
		self.invokes += int(other)
		return self
	def __int__(self):
		return int(self.bonus) + sum(list(self.roll)) + self.invokes
	def reroll(self):
		self.roll =fudge.fudge_roll()
	def readable(self):
		out = ""
		if self.roll:
			out += " ".join(fudge.fudgeMoji[x] for x in self.roll)
		return out
	@property
	def passive(self):
		return bool(self.roll)
class DummySkill:
	def __init__(self, name):
		self.name = name
	def __int__(self):
		return 0
	def __str__(self):
		return self.name
class FateBase(fudge.base.RollSystem,HasFatePoints):
	def __init__(self,dm,channel):
		fudge.base.RollSystem.__init__(self,dm,channel)
		HasFatePoints.__init__(self)
		self.scene_aspects = []
		self.enemy_templates={}
		self.troop = [] #Includes all characters currently in combat.
		self.active = None # For combat
		self.targets = [] # Also for combat, if you are in there, you can use !defend
		self.scene = None # to make it look better
		self.stored_att = None
		self.stored_def = None
		self.players = {}
		self.skills = {}
	async def parse(self,command,playern):
		if playern == self.dm:
			if command.lower().startswith("!scene "):
				self.make_scene(command.replace("!scene ","",1))
				self.scene = await self.send("Aspects: **" + "**, **".join([str(x) for x in self.scene_aspects]) +"**" if len(self.scene_aspects) else 'No aspects were declared')
				return True
			if command.lower().startswith("!new aspect "):
				self.extend_scene(command.replace("!new aspect ","",1))
			if command.lower().startswith("!enemy "):
				self.spawn_enemy(command.replace("!enemy ","",1))
			if command.lower().startswith("!boost "):
				self.grant_boost(commnad.replace("!boost ","",1))
		#active skills, used to initiate
		if not self.stored_att:
			if command.startswith("!create advantage "):
				await self.parse_create_advantage(command.replace("!create advantage ","",1),playern)
			if command.startswith("!attack "):
				await self.parse_attack(command.replace("!attack ","",1))
		#reactive skills, only used in response to either an obstacle or an active skill
		if not self.stored_def:
			if command.startswith("!defend "):
				pass
			if command.startswith("!overcome "):
				pass
		if command.startswith("!concede "):
			pass
		if command.startswith("!invoke "):
			await self.parse_invoke(command.replace("!invoke ","",1))
	def make_scene(self, command):
		self.scene_aspects.clear()
		get_aspect_list(command,self)
	def extend_scene(self,command):
		get_aspect_list(command,self)
	##Gets the skill value, 0 if you don't possess it, error if it doesn't exist or cover that action.
	def get_skill(self,command,actor,cando):
		true_skill = None
		for skill in actor.skills:
			if command.startswith(skill):
				if actor.skills[skill].can_do(cando):
					return actor.skills[skill]
				else:
					raise ValueError("Skill can't do that action")
		for skill in self.skills:
			if command.startswith(skill):
				for action in self.skills[skill]:
					if action.startswith(cando):
						return DummySkill(skill)
				raise ValueError("Skill can't do that")
		raise KeyError("That skill doesn't exist, please be carefull with capitalisation")
	##Used when waiting for the DM to approve something
	async def wait_dm_approve(self,what):
		def check(m):
			if m.author == self.dm and m.channel == self.channel:
				if m.content == f"!approve {what}":
					return True
				else:
					return False
		await client.wait_for('message',check=self.cancellable(check))

	##Wrapper to allow for cancellation
	def cancellable(self,inner):
		def check(m):
			if m.author == self.dm and m.channel == self.channel:
				if m.content == "!cancel":
					raise base.CancelError("This wasn't supposed to happen!")
			return inner(m)
		return check
	##Used when waiting for a player to send an okay
	async def wait_player_okay(self,player):
		def check(m):
			if m.author == player and m.channel == self.channel:
				if m.content == "!done":
					return True
		await client.wait_for('message',check=self.cancellable(check))
	##Waiting for defending player
	def wait_for_def(self):
		def check(m):
			return self.stored_def
		return check
	## Set opponents, returns an empty list if nothing fits the criteria
	def parse_targets(self, text):
		return []
	## Create advantage
	async def parse_create_advantage(self, command , playern):
		if self.active and not self.active.player == playern:
			await self.send("Not the active player, wait your turn.")
			return False
		elif not self.active and playern == self.dm and False:
			await self.send("DM is not supposed to use create advantage outside of conflicts.")
			return False
		actor = self.players.get(playern)
		if not actor:
			await self.send("You are not an active player here")
			return False
		true_skill = None
		try:
			true_skill = self.get_skill(command,actor,"Create Advantage")
		except KeyError:
			await self.send("Unknown skill, remember capitalisation.")
			return False
		except ValueError:
			await self.send("Skill can't create advantage, remember to type the name of the stunt, if you want to use that.")
			return False
		self.stored_att = True
		await self.send(f"the value of the skill is {int(true_skill)}")
		if not self.active:
			await self.send(f"DM, what will be the opposition? (acvtive/passive) [value]")
			pact = None
			def pas_or_act(m):
					return (m.channel == self.channel and m.author == self.dm and 
						(m.content.startswith("active") or m.content.startswith("passive"))
						and len(m.content.split(" "))>1)
			try:
				pact = await client.wait_for('message',check=self.cancellable(pas_or_act))
			except base.CancelError:
				await self.send("Cancelled by dm")
				self.stored_att = None
				return
			
			self.stored_att = StoredRoll(actor,roll=fudge.fudge_roll(),bonus=true_skill)
			dm_response = pact.content.split(" ")
			if pact.content.startswith("active"):
				if dm_response[1].isnumeric():
					opposition = int(dm_response[1])
					self.stored_def = StoredRoll(self, fudge.fudge_roll(),opposition)
				else:
					try:
						await self.send(f"Waiting for {dm_response[1]} to defend.")
						await client.wait_for('message',check=self.cancellable(self.wait_for_def()))
					except base.CancelError:
						await self.send("Cancelled by dm")
						self.stored_att = None
						return
			else:
				if dm_response[1].isnumeric():
					opposition = int(dm_response[1])
					self.stored_def = StoredRoll(self.dm, 0,opposition)
				else:
					await self.send("Not a number, try again later")
					self.stored_att = None
					return
			await self.send(f"{str(actor)} has rolled {self.stored_att.readable()} with a skill level of {int(self.stored_att.bonus)} for a total of {int(self.stored_att)}")
			try:
				await self.wait_player_okay(playern)
			except base.CancelError:
				
				self.stored_att = None
			self.stored_def = None

	## Parse the invokes
	async def parse_invoke(self, command, playern):
		actor = self.players.get(playern)
		if not actor:
			await self.send("You are not an active player here")
			return False
		target = None
		data = command.split(" ",2)
		if data[0] == "offense":
			target = self.stored_att
		elif data[0] == "defense":
			target = self.stored_def
		if not isinstance(target,StoredRoll):
			await self.send("sorry, can't invoke that for one of several reasons.")
			return False
		if data[1] == "reroll" and target.who != playern:
			return
		what = list(re.findall(r"\*\*([^*]*)\*\*",data[2]))[0]
		asp = self.get_aspect(what)
		try:
			await self.wait_dm_approve()
		except base.CancelError:
			return
		
	## Aspects
	def add_aspect(self, aspect:Aspect):
		self.scene_aspects.append(aspect)
	def get_aspect(self, aspect_name:str):
		if aspect_name in self.scene_aspects:
			return self.scene_aspects[self.scene_aspects.index(aspect_name)]
		elif len(self.troop):
			for trooper in self.troop:
				asp = trooper.get_aspect(aspect_name)
				if asp:
					return asp
		elif not self.active:
			for x in self.players:
				asp = self.players[x].get_aspect(aspect_name)
				if asp:
					return asp
		else:
			return None
	def remove_aspect(self, aspect):
		pass
	def refresh_aspects(self):
		for asp in self.scene_apects:
			asp.refresh()
		for trooper in self.troop:
			trooper.refresh_aspects()
		for x in self.players:
			self.players[x].refresh_aspects()
	def next_player(self):
		after = (self.troop.index(self.active)+1)%len(self.troop)
		self.active = self.troop[after]
		return self.active

