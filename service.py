# Service that manage the discord bot
# Sonoda 10/12/2022

import traceback
import os
import asyncio
import Bot as BotLib
import requests
from time import time

print("Starting program...")
bot = BotLib.Bot()
print(bot.name)

@bot.client.event
async def on_ready():
	for guild in bot.client.guilds:
		print(
			f'{bot.client.user} is connected to the following guild:\n'
			f'{guild.name}(id: {guild.id})'
		)

	await bot.startConnectionMessage()
	while True:
		# running mode
		if bot.SESSION=="run":
			try:
				await bot.runLoop()
			except Exception as e:
				print(e)
				print(traceback.format_exc())
				await bot.crashMessage(traceback.format_exc())
		# sleep mode
		elif bot.SESSION=="sleep":
			try:
				await asyncio.sleep(100)
			except Exception as e:
				print(e)
				await bot.crashMessage(e)
		# end program
		elif bot.SESSION=="exit":
			break
	await bot.client.close()


@bot.client.event
async def on_message(message):
	if message.author == bot.client.user:
		return
	if message.content == "kill "+bot.name:
		bot.SESSION = "exit"



#Bottom of Main.py
bot.client.run(os.environ['DISCORD_TOKEN'])
