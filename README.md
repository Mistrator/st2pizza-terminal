# st2pizza-terminal

A terminal client for st2pizza service.

## Prerequisites

1. Python 3
1. requests (Python library)

## Installation

Install Python 3
pip install requests

## Usage

python st2pizza.py <user ID> <order ID>

Starts a prompt which allows you to manage chosen order.

### Commands

* show <order|pizzas|toppings>:
	* show order: show all ordered pizzas in current order
	* show pizzas: list all available pizzas
	* show toppings: list all available toppings
* help|?: print usage information
* quit|exit: exit st2pizza prompt

### Usage example

$ python st2pizza.py 2F4GG6 A97D45
> show pizzas
5 pizzas found
1: Margarita (tomaatti, juusto)
2: Bolognese (jauheliha)
3: Opera (kinkku, tonnikala)
4: Napoli (kinkku, paprika)
5: Francescana (herkkusieni, kinkku)

## Authors

st2pizza-terminal: Miska Kananen
st2pizza service: Otto Otsamo
