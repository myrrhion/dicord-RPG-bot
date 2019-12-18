import fudge

class Aspect:
	def __init__(self,aspect_description,free_invokes=[]):
		self.description = aspect_description
		self.free_invokes = free_invokes
