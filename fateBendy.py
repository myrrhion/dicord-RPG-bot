from fateBase import *
import json

class FateBendyCharacter(FateCharacterBase):
	def __init__(self,player,**kwargs):
		fateBase.FateCharacterBase.__init__(self,player,**kwargs)


class FatePlayerBendy(FatePlayerBase):
	def __init__(self,player,**kwargs):
		FatePlayerBase.__init__(self,player,**kwargs)
		self.core_aspect = Aspect(self,kwargs.get("core aspect"))
		self.omega_aspect = Aspect(self,kwargs.get("omega aspect"))
		self.skills = {}
		self.char_aspects = [self.core_aspect,self.omega_aspect]
		self.average_mode_two = Mode(self, value = 1, **kwargs.get("average mode two"))
		self.average_mode_one = Mode(self, value =1, **kwargs.get("average mode one"))
		self.fair_mode = Mode(self,value=2,**kwargs.get("fair mode"))
		self.good_mode = Mode(self,value=3,**kwargs.get("good mode"))
		self.stunts = []
		for x in kwargs.get("stunts",[]):
			exec(f"self.stunts.append({x['type']}(self,**x))")
	def __str__(self):
		return str(self.player)
	def __repr__(self):
		return f"FatePlayerBendy(name: {self.player}, core_aspect: {self.core_aspect}, aspects:{self.char_aspects}, skills:{list(self.skills[x] for x in self.skills)}, stunts: {self.stunts})"

class FateBendy(FateBase):
	skills = json.load(open("data/BendySkills.txt"))


class Mode:
	def __init__(self, parent:FateBendyCharacter, name:str, value:int, skills:dict):
		self.name = Aspect(parent,name)
		parent.char_aspects.append(self.name)
		self.value = int(value)
		self.character = parent
		self.skills = {}
		for x in skills:
			self.skills[x] = BendySkill.build_from_name(x, skills[x],self)
	def rename(self,new_name:str):
		self.name = Aspect(self,name, self.name.free_invokes)
		self.character.state_changed()
		return self
	def __str__(self):
		return str(self.name)
	@classmethod
	def modeInkling(cls,character):
		return cls(character,"")
	

class BendySkill(Skill):
	def __init__(self, name, mode, actions:dict,value:int):
		Skill.__init__(self,mode.character,name,actions,value)
		self.mode = mode
	def __len__(self):
		return len(self.actions)
	def __int__(self):
		return self.value + self.mode.value
	def __repr__(self):
		return f"Skill(name: {self.name}, mode: {str(self.mode)}, value: {int(self)}, actions: {repr(self.actions)})"
	@classmethod
	def build_from_name(cls,name:str,value:int,mode:Mode = None):
		return cls(name,mode, FateBendy.skills[name], value)
print(repr(FatePlayerBendy("Dingus",**json.load(open("data/Bendy/Players/Testymcface.json")))))
