import discord
import json
import os
import asyncio

client = discord.Client()
class Glob:
	functions = {}
	active_sessions = {}
## Classes



## functions

# A bit of my own api since I like to mix actual bot with client
def command(acname=None,prefix="!"):
	def wrap(func):
		name = acname if acname else func.__name__
		print(name)
		Glob.functions[prefix+name] = func
		return func
	return wrap

# Starting the thing
def add_to_active(channel, game):
	if not channel in Glob.active_sessions:
		Glob.active_sessions[channel] = game
		return True
	return False
@command()
async def start(cont,msg):
	await cont.channel.send("Hello!")

##api implementation.
@client.event
async def on_ready():
	print('Connected!')
	print('Username: ' + client.user.name)
	print('ID: ' + str(client.user.id))

@client.event
async def on_message(message):
	if message.channel in Glob.active_sessions and message.author != client.user:
		await Glob.active_sessions[message.channel].parse(message.content,message.author)
		return
	#this is where the magic happens
	for cname in Glob.functions:
		if message.content.split()[0] == cname:
			cont = message.content
			cont = cont.replace(cname,'')
			cont = cont.strip()
			await Glob.functions[cname](message, cont)
			return


