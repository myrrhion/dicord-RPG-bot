import fateBase
import json

class FateBendyCharacter(fateBase.FateCharacterBase):
	def __init__(self):
		pass

class FateBendy(fateBase.FateBase):
	skills = json.load(open("data/BendySkills.txt"))


class Mode:
	def __init__(self, parent:FateBendyCharacter, name:str, value:int, skills:dict):
		self.name = fateBase.Aspect(name)
		self.value = value
		self.character = parent
		self.skills = {}
		for x in skills:
			self.skill[x] = BendySkill.build_from_name(x, skills[x],self)
	def rename(self,new_name:str):
		self.name = fateBase.Aspect(name, self.name.free_invokes)
		self.character.state_changed()
		return self
	@classmethod
	def modeInkling(cls):
		pass
	

class BendySkill(fateBase.Skill):
	def __init__(self, name, actions:dict,value:int,mode:Mode = None):
		fateBase.Skill.__init__(self,name,actions,value)
		self.mode = mode
	def __len__(self):
		return len(self.actions)
	def __int__(self):
		return self.value + self.mode.value
	@classmethod
	def build_from_name(cls,name:str,value:int,mode:Mode = None):
		return cls(name, FateBendy.skills[name], value, mode)
print(FateBendy.skills)
