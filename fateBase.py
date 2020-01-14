import fudge
import re
import asyncio

class Aspect:
	def __init__(self,parent,aspect_description,free_invokes=[]):
		self.owner = parent
		parent.add_aspect(self)
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
	def __del__(self):
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
		return self.actions
	def can_do(self,action):
		for x in self:
			if x.beginswith(action):
				return True
		return False
	def __repr__(self):
		return f"Skill(name: {self.name}, value: {self.value}, actions: {repr(self.actions)})"

class Consequence:
	def __init__(self,parent,value):
		self.character = parent 
		self.name = None
		self.type = None
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
	def __init__(self,parent,name,description,associated_skill,actions:list,boost=2,**kwargs):
		Stunt.__init__(self,parent,name,description)
		self._skill = parent.skills[associated_skill]
		for a in actions:
			if a not in self._skill.actions:
				raise ValueError("NOPE")
		self.actions = actions
		self._boost = boost
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
		newb = None
		for aspect in parent.char_aspects:
			if name == aspect:
				newb = aspect
		parent.remove_aspect(newb)
		SignatureAspect.upgrade(newb)

class FateCharacterBase(HasAspects):
	def __init__(self,player,**kwarg):
		self.name = kwarg.get("name")
		self.player = player
		self.char_aspects = []
	def add_aspect(self,aspect:Aspect):
		self.char_aspects.append(aspect)
	def remove_aspect(self,aspect):
		self.char_aspects.remove(aspect)
class FateBase(fudge.base.RollSystem,HasAspects):
	def __init__(self,dm,channel):
		fudge.base.RollSystem.__init__(self,dm,channel)
		self.scene_aspects = []
		self.enemy_templates={}
		self.troop = [] #Includes all characters.
	async def parse(self,command,playern):
		if playern == self.dm:
			if command.lower().startswith("!scene "):
				self.make_scene(command.replace("!scene ","",1))
				await self.send("Aspects: **" + "**, **".join(list(self.scene_aspects)) +"**" if len(self.scene_aspects) else 'No aspects were declared')
				return True
			if command.lower().startswith("!new aspect "):
				self.extend_scene(command.replace("!new aspect ","",1))
			if command.lower().startswith("!enemy "):
				self.spawn_enemy(command.replace("!enemy ","",1))
		if command.startswith("!overcome "):
			pass
		if cammand.startswith("!create advantage "):
			pass
	def make_scene(self, command):
		self.scene_aspects.clear()
		get_aspect_list(command,self)
	def extend_scene(self,command):
		get_aspect_list(command,self)
	def add_aspect(self, aspect:Aspect):
		self.scene_aspects.append(aspect)



