import requests
import numpy as np

N = 50 # number of symbols considered

pairs = []
symValJ = {}

def createPairs():
	global pairs
	global symValJ

	r = requests.get(f'https://api.binance.com/api/v3/exchangeInfo').json()
	symbols = r["symbols"]

	for i in symbols:
		symValJ[i["symbol"]] = {"bidPrice": 0, "askPrice": 0}

	values = {}
	for i in symbols:
		if i["status"]=="TRADING":
			values[i["baseAsset"]] = 1
			values[i["quoteAsset"]] = 1
	values = list(values.keys())[:N]
	print(len(values))
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
				if d1+d2 in symValJ:
					lv1.append(d1+d2)
					l1 = "num"
				if d2+d1 in symValJ:
					lv1.append(d2+d1)
					l1 = "den"

				# lv2
				if d2+d3 in symValJ:
					lv2.append(d2+d3)
					l2 = "num"
				if d3+d2 in symValJ:
					lv2.append(d3+d2)
					l2 = "den"

				# lv3
				if d3+d1 in symValJ:
					lv3.append(d3+d1)
					l3 = "num"
				if d1+d3 in symValJ:
					lv3.append(d1+d3)
					l3 = "den"

				if len(lv1)>0 and len(lv2)>0 and len(lv3)>0:
					pairs.append({"l1":l1, "l2":l2, "l3":l3, "d1": d1, "d2": d2,\
						"d3": d3, "lv1": lv1[0], "lv2": lv2[0], "lv3": lv3[0], "value": -100, "tpath": ""})
	print(len(pairs))

def processData(data):
	global pairs
	global symValJ

	data = json.loads(data)
	for i in data:
		symValJ[i["s"]]["bidPrice"] = float(i["b"])
		symValJ[i["s"]]["askPrice"] = float(i["a"])

	for d in pairs:
		if symValJ[d["lv1"]]["bidPrice"]!=0 and symValJ[d["lv2"]]["bidPrice"]!=0 and symValJ[d["lv3"]]["bidPrice"]!=0:
			lv_calc = 0
			lv_str = ""
			# level 1
			if d["l1"] == "num":
				lv_calc = float(symValJ[d["lv1"]]["bidPrice"])
				lv_str = f'{d["d1"]}->{d["lv1"]}[bidP][{symValJ[d["lv1"]]["bidPrice"]}]->{d["d2"]}\n'
			else:
				lv_calc = float(1/symValJ[d["lv1"]]["askPrice"])
				lv_str = f'{d["d1"]}->{d["lv1"]}[askP][{symValJ[d["lv1"]]["askPrice"]}]->{d["d2"]}\n'

			# level 2
			if d["l2"] == "num":
				lv_calc *= float(symValJ[d["lv2"]]["bidPrice"])
				lv_str += f'{d["d2"]}->{d["lv2"]}[bidP][{symValJ[d["lv2"]]["bidPrice"]}]->{d["d3"]}\n'
			else:
				lv_calc *= float(1/symValJ[d["lv2"]]["askPrice"])
				lv_str += f'{d["d2"]}->{d["lv2"]}[askP][{symValJ[d["lv2"]]["askPrice"]}]->{d["d3"]}\n'

			# level 3
			if d["l3"] == "num":
				lv_calc *= float(symValJ[d["lv3"]]["bidPrice"])
				lv_str += f'{d["d3"]}->{d["lv3"]}[bidP][{symValJ[d["lv3"]]["bidPrice"]}]->{d["d1"]}\n'
			else:
				lv_calc *= float(1/symValJ[d["lv3"]]["askPrice"])
				lv_str += f'{d["d3"]}->{d["lv3"]}[askP][{symValJ[d["lv3"]]["askPrice"]}]->{d["d1"]}\n'

			d["tpath"] = lv_str
			d["value"] = round((lv_calc-1)*100,5)

	pairs = sorted(pairs, key=lambda x: x["value"], reverse=True)
	positives = []
	for i in pairs:
		if i["value"]<0:
			break
		positives.append(i)
	r = [i["value"] for i in positives]
	print(r)

import websocket, json

pair = "btcusdt"
socket = f"wss://stream.binance.com:9443/ws/!ticker@arr"

def onMessage(ws, data):
	processData(data)

def onError(ws, data):
	print(data)

def onClose(ws):
	print("closed")



ws = websocket.WebSocketApp(socket, on_message=onMessage, on_error=onError, on_close=onClose)
createPairs()
ws.run_forever()
