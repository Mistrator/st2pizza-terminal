import sys
import requests
import os
import platform
from enum import Enum

API_URL = "http://st2.pizza/api/"

class Severity(Enum):
	INFO = 1
	WARN = 2
	ERROR = 3

class RequestType(Enum):
	GET = 1
	POST = 2

class LinuxColor(Enum):
	NONE = "\033[0m"
	BLACK = "\033[0;30m"
	RED = "\033[0;31m"
	GREEN = "\033[0;32m"
	ORANGE = "\033[0;33m"
	BLUE = "\033[0;34m"
	PURPLE = "\033[0;35m"
	CYAN = "\033[0;36m"
	LIGHT_GRAY = "\033[0;37m"
	DARK_GRAY = "\033[1;30m"
	LIGHT_RED = "\033[1;31m"
	LIGHT_GREEN = "\033[1;32m"
	YELLOW = "\033[1;33m"
	LIGHT_BLUE = "\033[1;34m"
	LIGHT_PURPLE = "\033[1;35m"
	LIGHT_CYAN = "\033[1;36m"
	WHITE = "\033[1;37m"

def print_color(msg, col, newline=True):
	if platform.system() == "Linux":
		if newline:
			print(col.value + msg + LinuxColor.NONE.value)
		else:
			print(col.value + msg + LinuxColor.NONE.value, end="")
	else:
		if newline:
			print(msg)
		else:
			print(msg, end="")


def log(msg, type, newline=True, terminate=False):
	if type == Severity.WARN:
		print_color("warning: ", LinuxColor.YELLOW, False)
	elif type == Severity.ERROR:
		print_color("error: ", LinuxColor.LIGHT_RED, False)
	elif type != Severity.INFO:
		log("Invalid log severity", Severity.ERROR, terminate=True)

	if newline:
		print(msg)
	else:
		print(msg, end="")

	if terminate:
		if type == Severity.ERROR:
			sys.exit(1)
		else:
			sys.exit(0)


def request(relative_url, type):
	url = API_URL + relative_url
	try:
		if type == RequestType.GET:
			response = requests.get(url)
		elif type == RequestType.POST:
			response = requests.post(url)
		else:
			log("Invalid request type", Severity.ERROR, terminate=True)
	except ConnectionError:
		log("Can't reach server (no internet connection or server is down?)", Severity.ERROR, terminate=True)
	return response.ok, (response.json() if response.ok else "")

# replace non-ASCII characters with ASCII ones
def print_encode(enc_str):
	cres = ""
	for cchar in enc_str:
		if 32 <= ord(cchar) and ord(cchar) <= 126:
			cres += cchar
		elif ord(cchar) == 228:
			cres += "a"
		elif ord(cchar) == 196:
			cres += "A"
		elif ord(cchar) == 246:
			cres += "o"
		elif ord(cchar) == 214:
			cres += "O"
		else:
			cres += "?"
	return cres


def print_pizzas():
	req_ok, pizza_data = request("pizzas", RequestType.GET)
	if not req_ok:
		log("Failed to fetch pizza list", Severity.ERROR, terminate=True)

	log(str(len(pizza_data)) + " pizzas found", Severity.INFO)

	for cur_pizza in pizza_data:
		log(str(cur_pizza["id"]) + ": ", Severity.INFO, False)
		print_color(print_encode(cur_pizza["name"]), LinuxColor.YELLOW, False)
		log(" (", Severity.INFO, False)

		for i, cur_topping in enumerate(cur_pizza["toppings"]):
			log(print_encode(cur_topping["name"]), Severity.INFO, False)
			if i != len(cur_pizza["toppings"])-1:
				log(", ", Severity.INFO, False)

		log(")", Severity.INFO)


def print_toppings():
	req_ok, topping_data = request("toppings", RequestType.GET)
	if not req_ok:
		log("Failed to fetch topping list", Severity.ERROR, terminate=True)

	log(str(len(topping_data)) + " toppings found", Severity.INFO)

	for cur_topping in topping_data:
		log(str(cur_topping["id"]) + ": ", Severity.INFO, False)
		print_color(print_encode(cur_topping["name"]), LinuxColor.NONE)	


# print all pizzas in current order by owner
def print_order(order_data):
	log(str(len(order_data)) + " pizzas in total", Severity.INFO)

	pizzas_by_owner = {}

	for cur_pizza in order_data:
		owner = print_encode(cur_pizza["user"]["name"])
		if owner in pizzas_by_owner:
			pizzas_by_owner[owner].append(cur_pizza["pizza"])
		else:
			pizzas_by_owner[owner] = [cur_pizza["pizza"]]

	for owner, pizzas in pizzas_by_owner.items():
		print_color(owner + ": ", LinuxColor.WHITE, False)

		for i, cur_pizza in enumerate(pizzas):
			print_color(print_encode(cur_pizza["name"]), LinuxColor.YELLOW, False)
			log(" (", Severity.INFO, False)

			for j, cur_topping in enumerate(cur_pizza["toppings"]):
				log(print_encode(cur_topping["name"]), Severity.INFO, False)
				if j != len(cur_pizza["toppings"])-1:
					log(", ", Severity.INFO, False)

			if i != len(pizzas)-1:
				log("), ", Severity.INFO, False)
			else:
				log(")", Severity.INFO)


# --- PROGRAM ENTRY POINT ---

if len(sys.argv) != 3:
	log("Usage: " + sys.argv[0] + " <user ID> <order ID>", Severity.INFO, terminate=True)

user_id = sys.argv[1]
order_id = sys.argv[2]

req_ok, user_data = request("users/" + user_id + "/", RequestType.GET)
if not req_ok:
	log("User doesn't exist", Severity.ERROR, terminate=True)

req_ok, order_data = request("orders/" + order_id + "/entries/", RequestType.GET)
if not req_ok:
	log("Order doesn't exist", Severity.ERROR, terminate=True)

# --- MAIN LOOP ---
while True:
	print("> ", end="")
	usr_input = input().split(" ")

	if len(usr_input) == 0:
		continue

	if usr_input[0] == "quit" or usr_input[0] == "exit":
		break
	elif usr_input[0] == "help" or usr_input[0] == "?":
		log("show <order|pizzas|toppings>: show current order or existing pizzas/toppings", Severity.INFO)
		log("create: create new pizza", Severity.INFO)
		log("order: add pizza to current order", Severity.INFO)
		log("help|?: show command usage", Severity.INFO)
		log("quit|exit: exit " + sys.argv[0], Severity.INFO)
	elif usr_input[0] == "show":
		if len(usr_input) != 2:
			log("Usage: show <order|pizzas|toppings>", Severity.INFO)
		else:
			if usr_input[1] == "order":
				print_order(order_data)
			elif usr_input[1] == "pizzas":
				print_pizzas()
			elif usr_input[1] == "toppings":
				print_toppings()
			else:
				log("Usage: show <order|pizzas|toppings>", Severity.INFO)
	elif usr_input[0] == "create":
		pass
	elif usr_input[0] == "order":
		pass
	else:
		log("Unknown command, enter \"help\" for usage information", Severity.INFO)