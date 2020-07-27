#! python
import os
import sys
import csv
import pprint
import urllib.request
import json
import xml.etree
import datetime

FIAT_CURRENCIES = ["EUR","USD"]
CRYPTO_CURRENCIES = {
	'ADA':'ADA',
	'ATOM':'ATOM',
	'BCH':'BCH',
	'DASH':'DASH',
	'EOS':'EOS',
	'XETC':'ETC',
	'XETH':'ETH',
	'XLTC':'LTC',
	'XMLN':'MLN',
	'XXLM':'XLM',
	'XXBT':'BTC',
	'XXRP':'XRP',
	'XREP':'REP',
	'XICN':'ICN'
	}
PAIRS = ['ATOMEUR','BCHEUR','DASHEUR','EOSEUR','XETCZEUR','XETHZEUR','XLTCZEUR', 'XXBTZEUR','XXRPZEUR']

class Txid:
	def __init__(self,txid=None,refid=None,time=None,thetype=None,aclass=None,asset=None,amount=None,fee=None,balance=None):
		self.txid = txid
		self.refid = refid
		self.time = time
		self.type = thetype
		self.aclass = aclass
		self.asset = asset
		self.amount = amount
		self.fee = fee
		self.balance = balance
	def check(self):
		check = True
		# TODO
		return check
	def __str__(self):
		string = "\n"
		for key,value in self.__dict__.items() :
			string = string + f"{key} : {value}\n"
		return string
class Transaction:
	def __init__(self,txid=None,ordertxid=None,pair=None,time=None,thetype=None,order=None,ordertype=None,price=None,cost=None,fee=None,vol=None,margin=None,misc=None,ledgers=None) :
		self.txid = txid
		self.ordertxid = ordertxid
		self.pair = pair
		self.time = time
		self.type = thetype
		self.ordertype = ordertype
		self.price = price
		self.cost = cost
		self.fee = fee
		self.vol = vol
		self.margin = margin
		self.misc = misc
		self.ledgers = ledgers
	def __str__(self):
		string = "\n"
		for key,value in self.__dict__.items() :
			string = string + f"{key} : {value}\n"
		return string
	def copy(self):
		new = Transaction()
		for attrib,value in self.__dict__.items() :
			new.__setattr__(attrib,value)
		return new
	def check(self):
		check = True
		for attrib in ["price","cost","vol"] :
			if not isinstance(getattr(self,attrib),float) :
				check = False
		return check
	@property
	def is_crypto_fiat(self):
		boolean = False
		for crypto in CRYPTO_CURRENCIES :
			for fiat in FIAT_CURRENCIES :
				if crypto in self.pair and fiat in self.pair :
					boolean = True
		return boolean

class Ledger(object):
	def __init__(self,transactions = None,txids = None) :
		self.transactions = transactions if transactions else []
		self.txids = txids if txids else []
	def load_trades_csv(self,filepath) :
		with open (filepath,newline='') as csvfile :
			content = csv.reader(csvfile, delimiter=',', quotechar='|')
			firstline = True
			for line in content :
				if firstline :
					list_attrib = list(map(lambda x: x.strip("\""),line))
					firstline = False
				else :
					transaction = Transaction()
					for attrib,element in zip(list_attrib,line):
						if hasattr(transaction,attrib) :
							if attrib in ["price","cost","fee","vol"] :
								element = float(element)
							elif attrib == "time" :
								date,time = element.strip("\"").split(" ")
								year,month,day = date.split("-")
								hour,minute,second = time.split(":")
								second,microsecond = second.split(".")
								element = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(second),int(microsecond))
							else :
								element = element.strip('\"')
							setattr(transaction,attrib,element)
					self.add_transaction(transaction)
		return True
	def load_ledgers_csv(self,filepath) :
		with open (filepath,newline='') as csvfile :
			content = csv.reader(csvfile, delimiter=',', quotechar='|')
			firstline = True
			for line in content :
				if firstline :
					list_attrib = list(map(lambda x: x.strip("\""),line))
					firstline = False
				else :
					txid = Txid()
					for attrib,element in zip(list_attrib,line):
						element = element.strip('\"')
						if hasattr(txid,attrib) :
							if attrib in ["amount","fee","balance"] :
								if element :
									element = float(element)
								else :
									element = None
							elif attrib == "time" :
								date,time = element.strip("\"").split(" ")
								year,month,day = date.split("-")
								hour,minute,second = time.split(":")
								element = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute))
							setattr(txid,attrib,element)
					self.add_txid(txid)
	def order_transactions(self):
		pendingTransactions = []
		for t in self.transactions :
			added = False
			for ind,pending in enumerate(pendingTransactions) :
				if t.time < pending.time :
					pendingTransactions.insert(ind,t)
					added = True
			if not added :
				pendingTransactions.append(t)
		return pendingTransactions
	def add_transaction(self,transaction) :
		if not self.get_transaction_by_txid(transaction.txid) :
			self.transactions.append(transaction)
		else :
			raise PermissionError
	def add_txid(self,txid) :
		self.txids.append(txid)
	def get_transaction_by_txid(self,txid) :
		for transaction in self.transactions :
			if transaction.txid == txid :
				return transaction
		return None
	def get_prior_to(self,dtime):
		ledger = Ledger()
		for transaction in self.transactions :
			if transaction.time < dtime :
				ledger.add_transaction(transaction)
		return ledger
	def get_transactions_by_pair(self,pair) :
		ledger = Ledger()
		for transaction in self.transactions :
			if transaction.pair == pair :
				ledger.add_transaction(transaction)
		return ledger
	def get_transactions_by_ordertype(self,ordertype) :
		ledger = Ledger()
		for transaction in self.transactions :
			if transaction.ordertype == order :
				ledger.add_transaction(transaction)
		return ledger
	def get_transactions_by_year(self,year) :
		ledger = Ledger()
		for transaction in self.transactions :
			if transaction.time.year == int(year) :
				ledger.add_transaction(transaction)
		return ledger
	def get_transactions_by_ordertxid(self,ordertxid) :
		ledger = Ledger()
		for transaction in self.transactions :
			if transaction.ordertxid == ordertxid :
				ledger.add_transaction(transaction)
		return ledger
	def get_transactions_by_type(self,thetype) :
		ledger = Ledger()
		for transaction in self.transactions :
			if transaction.type == thetype :
				ledger.add_transaction(transaction)
		return ledger
	def get_transactions_in_fiat(self) :
		ledger = Ledger()
		for transaction in self.transactions :
			if transaction.pair.endswith("EUR") or transaction.pair.endswith("USD") :
				ledger.add_transaction(transaction)
		return ledger
	def get_txid_by_type(self,thetype):
		ledger = Ledger()
		for tx in self.txids :
			if tx.type == thetype :
				ledger.add_txid(tx)
		return ledger
	def get_txid_by_asset(self,asset):
		ledger = Ledger()
		for tx in self.txids :
			if tx.asset == asset :
				ledger.add_txid(tx)
		return ledger
	def get_txids_by_refid(self,refid):
		txids = []
		for tx in self.txids :
			if tx.refid == refid and tx.amount != 0.0 :
				txids.append(tx)
		return txids
	def toxlm(self):
		# TODO
		pass
	def get_ledgers_by_pair(self):
		pairs = {}
		for transaction in self.transactions :
			pair = transaction.pair
			if not pair in pairs :
				pairs[pair] = Ledger()
			pairs[pair].add_transaction(transaction)
		return pairs

		ledger.transactions.append()
	def remove(self,transaction):
		for index,element in enumerate(self.transactions) :
			if element.txid == transaction.txid :
				self.transactions.pop(index)
				return True
		return False
	def copy(self) :
		new = Ledger()
		for transaction in self.transactions :
			new.add_transaction(transaction.copy())
		return new
	def check(self):
		check = True
		for transaction in self.transactions :
			if not transaction.check() :
				check = False
		for txid in self.txids :
			if not txid.check():
				check = False
		return check
	@property
	def lenght(self):
		lenght = len(self.transactions)
		return lenght
	@property
	def keys(self):
		return list(map(lambda x:x.txid,self.transactions))
	@property
	def values(self):
		return self.transactions
	@property
	def cost(self):
		tot = sum(list(map(lambda x:float(x.cost),self.transactions)))
		return tot
	@property
	def is_empty(self):
		return True if self.transactions else False
	def show(self):
		for transaction in self.transactions :
			print(transaction)

if __name__ == "__main__":

	API_KEY = "7b23beae5421aed1737a38d51540cb404db0bf0bf76394326d0e75b3aafe1b60"
	ledger = Ledger()

	trades_filepath = os.path.join(os.getcwd(),"ressources","trades_09052020.csv")
	ledgers_filepath = os.path.join(os.getcwd(),"ressources","ledgers_09052020.csv")

	ledger.load_trades_csv(trades_filepath)
	ledger.load_ledgers_csv(ledgers_filepath)

	cash_in = 0.0
	cash_out = 0.0
	plusvalue_totale = 0.0

	dico = {}
	dico["ZEUR"] = 0.0
	dico["time"] = {}

	plusvalue_2020 = 0.0
	plusvalue_2019 = 0.0
	plusvalue_2018 = 0.0
	plusvalue_2017 = 0.0
	reqs_file = os.path.join("ressources","reqs.json")
	reqs = {}
	with open(reqs_file, 'r') as json_file:
		reqs = json.load(json_file)
	print("DEBUT de calcul ...")

	the_year = 0

	for tx in ledger.txids :

		# si le cash_in doit être mis à 0 au debut d'année
		# NE SEMBLE PAS ETRE LE CAS
		# if the_year != tx.time.year :
		#	the_year = tx.time.year
		#	cash_in = 0.0

		if tx.type == "deposit" and tx.asset == "ZEUR" and tx.txid :
			dico["ZEUR"] += tx.amount

		elif tx.type == "trade" :
			if not tx.asset in dico :
				dico[tx.asset] = 0.0
			dico[tx.asset] += tx.amount

			transaction = ledger.get_transaction_by_txid(tx.refid)

			if not hasattr(transaction,"done") or not transaction.done :
				transaction.done = True
				year = transaction.time.year

				month = transaction.time.month
				day = transaction.time.day
				hour = transaction.time.hour
				dtime = datetime.datetime(year,month,day,hour)
				timestamp = int(datetime.datetime.timestamp(dtime))

				if transaction.type == "buy" and "EUR" in transaction.pair :
					print(f"@@ trade {dtime} - achat {transaction.pair} : \n\t vol :{transaction.vol} * price : {transaction.price} = cost : {transaction.cost}")
					print(f"\t cash_in = {cash_in} + {transaction.cost}")
					cash_in += transaction.cost
					print(f"\t cash_in = {cash_in}")
				if transaction.type == "sell" and "EUR" in transaction.pair :
					print(f"@@ trade vente {transaction.pair} : {transaction.vol}*{transaction.price}={transaction.cost}")

					cash_out = transaction.cost
					print(f"\t cash_in = {cash_in} \n\t cash_out = {cash_out}")
					if not timestamp in dico["time"] :
						dico["time"][timestamp] = 0.0

					for asset in dico :
						if asset in CRYPTO_CURRENCIES :
							symbol = CRYPTO_CURRENCIES[asset]
							req = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={symbol}&tsym=EUR&limit=1&toTs={timestamp}&e=Kraken&api_key={API_KEY}"
							if not req in reqs :
								res = urllib.request.urlopen(req).read()
								page = res.decode("utf8")
								rep = json.loads(page)
								reqs[req]=rep
							else :
								rep = reqs[req]
							symbol_price_at_timestamp = None
							if rep["Response"] == "Success" :
								data = rep["Data"]["Data"]
								for candel in data :
									if candel["time"] == timestamp :
										avg_price = (candel["high"]+candel["low"]+candel["close"]+candel["open"]) / 4
										symbol_price_at_timestamp = avg_price
							if symbol_price_at_timestamp :
								print(f"\t\t && detail wallet:{dico['time'][timestamp]} + qté_{asset}:{dico[asset]} * {symbol}_price_at_{timestamp}:{symbol_price_at_timestamp}")
								dico["time"][timestamp] += (dico[asset] * symbol_price_at_timestamp)
								print(f"\t\t && wallet = {dico['time'][timestamp]}")
							else :
								print(f"ERROR {tx.txid} {symbol}_price_at_{timestamp} n'a pas ete trouve dans le resultat de la requete.")
					wallet_value = dico["time"][timestamp]
					t_plusvalue = cash_out - (cash_in*(cash_out/wallet_value))
					print(f"\t ########{tx.refid}\n\t# cash_in : {cash_in}\n\t# cash_out : {cash_out}\n\t# wallet : {wallet_value}\n\t ########")
					print(f"\t plus_value transaction : {t_plusvalue}")
					plusvalue_totale += t_plusvalue
					if transaction.time.year == 2020 :
						plusvalue_2020 += t_plusvalue
					if transaction.time.year == 2019 :
						plusvalue_2019 += t_plusvalue
					if transaction.time.year == 2018 :
						plusvalue_2018 += t_plusvalue
					if transaction.time.year == 2017 :
						plusvalue_2017 += t_plusvalue
					print(f"\t plus_value 2019 lattente : {plusvalue_2019}")
					cash_in -= cash_in*(cash_out/wallet_value)
					print(f"\t calcul new cash_in = {cash_in}")
	print("ecriture reqs")
	with open(reqs_file, 'w') as outfile:
		json.dump(reqs, outfile)
	taxe_2019 = 30*plusvalue_2019 / 100
	print(f"taxe_2019 = {taxe_2019}")
	print(f"FIN :\n\tplusvalue_2020 = {plusvalue_2020}\n\tplusvalue_2019 = {plusvalue_2019}\n\tplusvalue_2018 = {plusvalue_2018}\n\tplusvalue_2017 = {plusvalue_2017}\n\tplusvalue_totale = {plusvalue_totale}")

