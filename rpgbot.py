import discord

import json
import os
import asyncio

client = discord.Client()
class Glob:
	functions = {}
## Classes



## functions

# A bit of my own api since I like to mix actual bot with client
def command(acname=None):
	def wrap(func):
		name = acname if acname else func.__name__
		print(name)
		Glob.functions["!"+name] = func
		return func
	return wrap



##api implementation.
@client.event
async def on_ready():
	print('Connected!')
	print('Username: ' + client.user.name)
	print('ID: ' + str(client.user.id))

@client.event
async def on_message(message):
	#this is where the magic happens
	for cname in Glob.functions:
		if message.content.split()[0] == cname:
			cont = message.content
			cont = cont.replace(cname,'')
			cont = cont.strip()
			await Glob.functions[cname](message, cont)
			return


token = open("login.token").readline().strip()
client.run(token)
