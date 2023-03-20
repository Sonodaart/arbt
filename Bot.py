import discord
from discord.ext import commands
import asyncio
from time import time, sleep
from datetime import datetime, timedelta
import requests
import websocket, json
import threading
# import Trader as TraderLib

class Bot:
	def __init__(self):
		self.client = discord.Client()
		# self.Trader = TraderLib.Trader()
		self.pairs = []
		self.symValJ = {}
		self.positives = []
		self.socket = f"wss://stream.binance.com:9443/ws/!ticker@arr"
		self.name = "arbitrageBot"
		self.SESSION = "run"

		# id canali
		self.room = {'generaleCH':1005242726125678635,
						'attivitaCH':1005245873883713546,
						'transazioniCH':1005968395927293962,
						'azioniCH':1005245915931615393,
						'arbitrage':1087021333403144223}

		self.createPairs()

	async def startConnectionMessage(self):
		greet_message = "Starting Connection."
		await self.client.get_channel(self.room['attivitaCH']).send(greet_message)

	async def crashMessage(self,e):
		allowed_mentions = discord.AllowedMentions(everyone = True)
		await self.client.get_channel(self.room['azioniCH']).send(content=str(e), allowed_mentions=allowed_mentions)

	async def runLoop(self):
		websocket_thread = threading.Thread(target=self.websocket_thread)
		websocket_thread.start()
		while True:
			sleep(1)
			if len(self.positives)>0:
				await self.client.get_channel(self.room['arbitrage']).send(str(self.positives[:10]))

	def websocket_thread(self):
		self.ws = websocket.WebSocketApp(self.socket, on_message=self.onMessage, on_error=self.onError, on_close=self.onClose)
		self.ws.run_forever()

	def createPairs(self):
		N = -1 # number of symbols considered
		start = time()
		symbols = requests.get(f'https://api.binance.com/api/v3/exchangeInfo').json()["symbols"]
		for i in symbols:
			self.symValJ[i["symbol"]] = {"bidPrice": 0, "askPrice": 0}

		values = {}
		for i in symbols:
			if i["status"]=="TRADING":
				values[i["baseAsset"]] = 1
				values[i["quoteAsset"]] = 1
		values = list(values.keys())[:N]
		# print(values)
		s1 = values[:]
		s2 = values[:]
		s3 = values[:]

		for d1 in s1:
			for d2 in s2:
				for d3 in s3:
					if d1==d2 or d2==d3 or d3==d1:
						continue
					lv1 = []
					lv2 = []
					lv3 = []
					l1 = ""
					l2 = ""
					l3 = ""

					# lv1
					if d1+d2 in self.symValJ:
						lv1.append(d1+d2)
						l1 = "num"
					if d2+d1 in self.symValJ:
						lv1.append(d2+d1)
						l1 = "den"

					# lv2
					if d2+d3 in self.symValJ:
						lv2.append(d2+d3)
						l2 = "num"
					if d3+d2 in self.symValJ:
						lv2.append(d3+d2)
						l2 = "den"

					# lv3
					if d3+d1 in self.symValJ:
						lv3.append(d3+d1)
						l3 = "num"
					if d1+d3 in self.symValJ:
						lv3.append(d1+d3)
						l3 = "den"
					# print(d1,d2,d3,len(lv1),len(lv2),len(lv3))
					if len(lv1)>0 and len(lv2)>0 and len(lv3)>0:
						self.pairs.append({"l1":l1, "l2":l2, "l3":l3, "d1": d1, "d2": d2,\
							"d3": d3, "lv1": lv1[0], "lv2": lv2[0], "lv3": lv3[0], "value": -100, "tpath": ""})
		end = time()
		print(f"Built {len(self.pairs)} paths, in {end-start} seconds.")

	def processData(self, data):
		# start = time()
		data = json.loads(data)
		for i in data:
			self.symValJ[i["s"]]["bidPrice"] = float(i["b"])
			self.symValJ[i["s"]]["askPrice"] = float(i["a"])

		for d in self.pairs:
			if self.symValJ[d["lv1"]]["bidPrice"]!=0 and self.symValJ[d["lv2"]]["bidPrice"]!=0 and self.symValJ[d["lv3"]]["bidPrice"]!=0:
				lv_calc = 0
				# level 1
				if d["l1"] == "num":
					lv_calc = float(self.symValJ[d["lv1"]]["bidPrice"])
				else:
					lv_calc = float(1/self.symValJ[d["lv1"]]["askPrice"])

				# level 2
				if d["l2"] == "num":
					lv_calc *= float(self.symValJ[d["lv2"]]["bidPrice"])
				else:
					lv_calc *= float(1/self.symValJ[d["lv2"]]["askPrice"])

				# level 3
				if d["l3"] == "num":
					lv_calc *= float(self.symValJ[d["lv3"]]["bidPrice"])
				else:
					lv_calc *= float(1/self.symValJ[d["lv3"]]["askPrice"])

				d["value"] = round((lv_calc-1)*100,5)

		self.pairs = sorted(self.pairs, key=lambda x: x["value"], reverse=True)
		# if self.pairs[0]["value"]>0.6 or True:
		# 	self.Trader.arbitrage(self.pairs[0])

		self.positives = []
		for i in self.pairs:
			if i["value"]<0.3:
				break
			self.positives.append([i["value"],f'{i["d1"]},{i["d2"]},{i["d3"]}'])
		# end = time()
		# print(f"time: {end-start}")


	def onMessage(self, ws, data):
		self.processData(data)

	def onError(self, ws, data):
		print("a",data)

	def onClose(self, ws, a, b):
		print("Closed ",a,b)

