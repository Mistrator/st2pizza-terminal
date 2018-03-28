import sys
import requests
import os
import platform
from enum import Enum
from operator import itemgetter

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


API_URL = "http://st2.pizza/api/"
PIZZA_COLOR = LinuxColor.YELLOW
USER_COLOR = LinuxColor.WHITE


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


def request(relative_url, type, body=None):
	url = API_URL + relative_url
	try:
		if type == RequestType.GET:
			response = requests.get(url)
		elif type == RequestType.POST:
			if body == None:
				log("Tried to make a POST request with empty body", Severity.WARN)
			else:
				response = requests.post(url, json=body)
		else:
			log("Invalid request type", Severity.ERROR, terminate=True)
	except ConnectionError:
		log("Can't reach server (no internet connection or server down?)", Severity.ERROR, terminate=True)
	return response.ok, (response.json() if response.ok else "")

# Try to parse integer from string
# Must be between low and high, inclusive
def try_parse_int(to_parse, low, high):
	try:
		parsed = int(to_parse)
		return (low <= parsed and parsed <= high), parsed
	except ValueError:
		return False, low


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


def print_single_pizza(cur_pizza, print_toppings, newline=False):
	print_color(print_encode(cur_pizza["name"]), PIZZA_COLOR, (newline and not print_toppings))

	if print_toppings:
		log(" (", Severity.INFO, False)

		for i, cur_topping in enumerate(cur_pizza["toppings"]):
			log(print_encode(cur_topping["name"]), Severity.INFO, False)
			if i != len(cur_pizza["toppings"])-1:
				log(", ", Severity.INFO, False)

		log(")", Severity.INFO, newline)


def print_pizzas():
	req_ok, pizza_data = request("pizzas", RequestType.GET)
	if not req_ok:
		log("Failed to fetch pizza list", Severity.ERROR, terminate=True)

	log(str(len(pizza_data)) + " pizzas found", Severity.INFO)

	for cur_pizza in pizza_data:
		log(str(cur_pizza["id"]) + ": ", Severity.INFO, False)
		print_single_pizza(cur_pizza, True, True)


def print_toppings():
	req_ok, topping_data = request("toppings", RequestType.GET)
	if not req_ok:
		log("Failed to fetch topping list", Severity.ERROR, terminate=True)

	log(str(len(topping_data)) + " toppings found", Severity.INFO)

	for cur_topping in topping_data:
		log(str(cur_topping["id"]) + ": ", Severity.INFO, False)
		print_color(print_encode(cur_topping["name"]), LinuxColor.NONE)	


# print all pizzas in current order by owner
def print_order(order_id):
	req_ok, order_data = request("orders/" + order_id + "/entries/", RequestType.GET)

	if not req_ok:
		log("Failed to fetch order data", Severity.ERROR, terminate=True)


	log(str(len(order_data)) + " pizzas in total", Severity.INFO)

	pizzas_by_owner = {}

	for cur_pizza in order_data:
		owner = print_encode(cur_pizza["user"]["name"])
		if owner in pizzas_by_owner:
			pizzas_by_owner[owner].append(cur_pizza["pizza"])
		else:
			pizzas_by_owner[owner] = [cur_pizza["pizza"]]

	for owner, pizzas in pizzas_by_owner.items():
		print_color(owner + ": ", USER_COLOR, False)

		for i, cur_pizza in enumerate(pizzas):
			print_single_pizza(cur_pizza, True, False)

			if i != len(pizzas)-1:
				log(", ", Severity.INFO, False)
			else:
				log("", Severity.INFO)


# return edit distance (Levenshtein distance) between strings a and b
def edit_distance(str_a, str_b):
	str_a = " " + str_a
	str_b = " " + str_b
	n = len(str_a)
	m = len(str_b)

	INF = 1000000005
	dp = []

	for i in range(0, n):
		narr = []
		for j in range(0, m):
			narr.append(INF)
		dp.append(narr)

	for i in range(0, n):
		dp[i][0] = i

	for j in range(0, m):
		dp[0][j] = j

	for i in range(1, n):
		for j in range(1, m):
			cost = (0 if str_a[i] == str_b[j] else 1)
			dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)

	return dp[n-1][m-1]


def send_order(pizza_id, user_id, order_id):
	post_body = {"orderID": order_id, "userID": user_id, "pizzaID": pizza_id}

	req_ok, response = request("entries", RequestType.POST, post_body)
	if not req_ok:
		log("Order failed", Severity.ERROR, terminate=True)

	return response


# parse user input (pizza name/id) and return closest matching pizza
def parse_order(raw_order):
	req_ok, pizza_data = request("pizzas", RequestType.GET)
	if not req_ok:
		log("Failed to fetch pizza list", Severity.ERROR, terminate=True)

	enc_order = print_encode(raw_order)
	matching_pizzas = []

	# rank pizzas by edit distance from name
	for cur_pizza in pizza_data:
		# only exact matches for ID
		id_dist = (0 if str(cur_pizza["id"]) == enc_order else 1000000005)
		name_dist = edit_distance(str(cur_pizza["name"]), enc_order)
		matching_pizzas.append([min(id_dist, name_dist), cur_pizza])

	matching_pizzas = sorted(matching_pizzas, key=itemgetter(0))

	best_dist = matching_pizzas[0][0]
	best_matches = [] 

	# select pizzas with smallest edit distance
	for cur_match in matching_pizzas:
		cur_dist = cur_match[0]
		if cur_dist > best_dist:
			break
		best_matches.append(cur_match[1])

	# ask which pizza user meant if there are several possibilities
	if len(best_matches) > 1:
		log("Did you mean ", Severity.INFO, False)

		for i, cur_pizza in enumerate(best_matches):
			log("(" + str(i+1) + ") ", Severity.INFO, False)

			print_single_pizza(cur_pizza, True, False)

			if i < len(best_matches)-2:
				log(", ", Severity.INFO, False)
			elif i == len(best_matches)-2:
				log(" or ", Severity.INFO, False)
			elif i == len(best_matches)-1:
				log("?", Severity.INFO)

		inp_ok = False

		while not inp_ok:
			log("Enter selection [1.." + str(len(best_matches)) + "] > ", Severity.INFO, False)
			usr_input = input()
			inp_ok, selection = try_parse_int(usr_input, 1, len(best_matches))

		return best_matches[selection-1]

	return best_matches[0]


# add pizza to current order
# raw_order: unprocessed user selection
def order_pizza(raw_order, user_id, order_id):
	selected_pizza = parse_order(raw_order)

	inp_ok = False
	while not inp_ok:
		log("Do you want to order ", Severity.INFO, False)
		print_single_pizza(selected_pizza, True, False)
		log("? (y/n) > ", Severity.INFO, False)

		usr_inp = input().lower()
		if len(usr_inp) == 1:
			if usr_inp[0] == "y":
				inp_ok = True
			elif usr_inp[0] == "n":
				return


	response = send_order(selected_pizza["id"], user_id, order_id)


def send_new_pizza(name, toppings):
	topping_ids = []
	for cur_topping in toppings:
		topping_ids.append(cur_topping["id"])

	post_body = { "name": name, "toppings": topping_ids }
	req_ok, response = request("pizzas", RequestType.POST, post_body)

	if not req_ok:
		log("Failed to create new pizza", Severity.ERROR, terminate=True)

	return response

def create_pizza():
	req_ok, pizza_data = request("pizzas", RequestType.GET)
	if not req_ok:
		log("Failed to fetch pizza list", Severity.ERROR, terminate=True)

	req_ok, topping_data = request("toppings", RequestType.GET)
	if not req_ok:
		log("Failed to fetch topping list", Severity.ERROR, terminate=True)

	name_ok = False
	while not name_ok:
		log("Name the pizza > ", Severity.INFO, False)
		pizza_name = print_encode(input())
		if len(pizza_name) > 0:
			name_ok = True
		for cur_pizza in pizza_data:
			if print_encode(cur_pizza["name"]) == pizza_name:
				log("A pizza called " + pizza_name + " already exists", Severity.WARN, terminate=False)
				name_ok = False
				break
	
	usr_toppings = []

	print_toppings()

	while True:
		log("Add new topping (empty line finishes) > ", Severity.INFO, False)
		usr_input = print_encode(input())

		if len(usr_input) == 0 and len(usr_toppings) > 0:
			break

		topping_dists = []
		for cur_topping in topping_data:
			id_dist = (0 if str(cur_topping["id"]) == usr_input else 1000000005)
			name_dist = edit_distance(str(cur_topping["name"]), usr_input)
			topping_dists.append([min(id_dist, name_dist), cur_topping])

		topping_dists = sorted(topping_dists, key=itemgetter(0))

		best_dist = topping_dists[0][0]
		best_matches = []

		for cur_match in topping_dists:
			cur_dist = cur_match[0]
			if cur_dist > best_dist:
				break
			best_matches.append(cur_match[1])

		if len(best_matches) > 1:
			log("Did you mean ", Severity.INFO, False)
	
			for i, cur_topping in enumerate(best_matches):
				log("(" + str(i+1) + ") ", Severity.INFO, False)
	
				log(print_encode(cur_topping["name"]), Severity.INFO, False)
	
				if i < len(best_matches)-2:
					log(", ", Severity.INFO, False)
				elif i == len(best_matches)-2:
					log(" or ", Severity.INFO, False)
				elif i == len(best_matches)-1:
					log("?", Severity.INFO)
	
			inp_ok = False
			while not inp_ok:
				log("Enter selection [1.." + str(len(best_matches)) + "] > ", Severity.INFO	, False)
				usr_input = input()
				inp_ok, selection = try_parse_int(usr_input, 1, len(best_matches))
	
			usr_toppings.append(best_matches[selection-1])

		else:
			usr_toppings.append(best_matches[0])

	pizza_prt = { "name": pizza_name, "toppings": usr_toppings }

	while True:
		log("Do you want to create ", Severity.INFO, False)
		print_single_pizza(pizza_prt, True)
		log("? (y/n) > ", Severity.INFO, False)

		usr_sel = input().lower()
		if usr_sel == "y":
			break
		elif usr_sel == "n":
			return

	send_new_pizza(pizza_name, usr_toppings)


# --- PROGRAM ENTRY POINT ---

if len(sys.argv) != 3:
	log("Usage: " + sys.argv[0] + " <user ID> <order ID>", Severity.INFO, terminate=True)

user_id = sys.argv[1]
order_id = sys.argv[2]

req_ok, user_data = request("users/" + user_id + "/", RequestType.GET)
if not req_ok:
	log("User doesn't exist", Severity.ERROR, terminate=True)

req_ok, order_data = request("orders/" + order_id + "/", RequestType.GET)
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
		log("show <order|pizzas|toppings>: show current order or lists of existing pizzas/toppings", Severity.INFO)
		log("create pizza: create new pizza", Severity.INFO)
		log("order <pizza ID|name>: add pizza to current order", Severity.INFO)
		log("help|?: show command usage", Severity.INFO)
		log("quit|exit: exit " + sys.argv[0], Severity.INFO)
	elif usr_input[0] == "show":
		if len(usr_input) != 2:
			log("Usage: show <order|pizzas|toppings>", Severity.INFO)
		else:
			if usr_input[1] == "order":
				print_order(order_id)
			elif usr_input[1] == "pizzas":
				print_pizzas()
			elif usr_input[1] == "toppings":
				print_toppings()
			else:
				log("Usage: show <order|pizzas|toppings>", Severity.INFO)
	elif usr_input[0] == "create":
		if len(usr_input) < 2:
			log("Usage: create pizza", Severity.INFO)
		else:
			create_pizza()
	elif usr_input[0] == "order":
		if len(usr_input) < 2:
			log("Usage: order <pizza ID|name>", Severity.INFO)
			log("Hint: \"show pizzas\" - show all available pizzas", Severity.INFO)
		else:
			# support pizza names with spaces
			order_query = ""
			for i in range(1, len(usr_input)):
				order_query += usr_input[i]
				if i != len(usr_input)-1:
					order_query += " "
			order_pizza(order_query, user_id, order_id)
	else:
		log("Unknown command, enter \"help\" for usage information", Severity.INFO)
