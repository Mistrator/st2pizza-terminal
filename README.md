# st2pizza-terminal

A terminal client for st2pizza service.

## Prerequisites

1. Python 3
1. requests (Python library)

## Installation

1. Install Python 3
1. pip install requests
1. Download st2pizza.py

## Usage

python st2pizza.py &lt;user ID&gt; &lt;order ID&gt;: start st2pizza prompt

### Commands

* show <order | pizzas | toppings>:
	* show order: list all ordered pizzas in current order
	* show pizzas: list all available pizzas
	* show toppings: list all available toppings
* order <pizza ID | pizza name>: add a pizza to current order
* help | ?: print usage information
* quit | exit: exit st2pizza prompt and quit program

### Usage example

```
$ python st2pizza.py 2F4GG6 A97D45
> show pizzas
5 pizzas found
1: Margarita (tomaatti, juusto)
2: Bolognese (jauheliha)
3: Opera (kinkku, tonnikala)
4: Napoli (kinkku, paprika)
5: Francescana (herkkusieni, kinkku)
> order Margarita
Do you want to order Margarita (tomaatti, juusto)? > y
> quit
$
```

## Authors

st2pizza-terminal: Miska Kananen

st2pizza service: Otto Otsamo
