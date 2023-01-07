import telebot
import requests
import datetime
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

telebot_token = config['API']['telebot_token']
price_precision = config['Price']['price_precision']
days = int(config['Price History']['days'])
max_days = int(config['Price History']['max_days'])

# Replace YOUR_API_KEY with your actual API key
bot = telebot.TeleBot(token=telebot_token)

def get_price(symbol):
    symbol = symbol.lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd&include_24hr_vol=true&include_market_cap=true&include_24hr_change=true&include_last_updated_at=true&precision=3"
    response = requests.get(url)
    data = response.json()

    if symbol in data:
        if 'usd' in data[symbol]:
            # Extract the relevant information from the returned data
            price = data[symbol]["usd"]
            market_cap = data[symbol]["usd_market_cap"]
            volume = data[symbol]["usd_24h_vol"]
            change = data[symbol]["usd_24h_change"]
            name = (symbol.split("-")[0].capitalize() + " " + symbol.split("-")[1].capitalize()) if "-" in symbol else symbol.capitalize()

            # Get the current time and format it as desired
            current_time = datetime.datetime.now().strftime("%m/%d/%y %H:%M")

            # Format the message to include the 24-hour volume and market capitalization
            return f"📊 {name} = ${price:.{price_precision}f}\n💰 Market Cap: ${market_cap:.0f} \n💸 24hr Volume: ${volume:.0f}\n💱 24hr Change: {change: 3f}%\n\n📅 Date updated: {current_time}\n\nCryptocurrency Price Bot Functions: /help \n\n@tothemoonprice_bot"
        else:
            return "Sorry, the price for this cryptocurrency was not found.\n\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot"
    else:
        return "Sorry, this cryptocurrency was not found.\n\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot"

def get_price_history(symbol, days=days):
    days = min(days, max_days)
    symbol = symbol.lower()
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    start_date, end_date = start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days={days}&from={start_date}&to={end_date}"
    response = requests.get(url)
    data = response.json()

    if 'prices' in data:
        name = (symbol.split("-")[0].capitalize() + " " + symbol.split("-")[1].capitalize()) if "-" in symbol else symbol.capitalize()
        message = f"📈 Price history for {name} for the last {days} days:\n\n"
        date_price_dict = {datetime.datetime.fromtimestamp(datapoint[0] / 1000.0).strftime('%d.%m.%Y'): datapoint[1] for datapoint in data["prices"]}
        message += '\n'.join([f"{date}: ${price:.{price_precision}f}" for date, price in date_price_dict.items()])
        message += "\n\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot"
        return message
    else:
        return "Sorry, this cryptocurrency was not found.\n\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Welcome to the Cryptocurrency Price Bot! You can use the following commands:\n\n▪/price <symbol> - get the current price of a cryptocurrency (eg '/price bitcoin' or '/price bitcoin-cash')\n▪️/price_history <symbol> - get the price history of a cryptocurrency for the last 7 days (eg '/price_history bitcoin' or 'price_history bitcoin-cash')\n▪️/price_history <symbol> <number_of_days> - get the price history of a cryptocurrency for the specified number of days (up to 25) (eg '/price bitcoin 7')\n▪️/top - top 25 cryptocurrencies by market price\n▪️/marketcap - top 25 cryptocurrencies by market capitalization\n\n@tothemoonprice_bot")

@bot.message_handler(commands=['price'])
def get_price_command(message):
    chat_id = message.chat.id
    command, *symbol = message.text.split()
    if len(symbol) > 0:
        symbol = symbol[0]
        price = get_price(symbol)
        bot.send_message(chat_id, price)
    else:
        bot.send_message(chat_id, "Please specify a cryptocurrency symbol.\n\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot")

@bot.message_handler(commands=['price_history'])
def get_price_history_command(message):
    chat_id = message.chat.id
    command, *args = message.text.split()
    if len(args) > 0:
        symbol = args[0]
        if len(args) > 1:
            try:
                days = int(args[1])
                price_history = get_price_history(symbol, days)
                bot.send_message(chat_id, price_history)
            except ValueError:
                bot.send_message(chat_id, "Invalid number of days. Please enter a valid number.\n\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot")
        else:
            price_history = get_price_history(symbol)
            bot.send_message(chat_id, price_history)
    else:
        bot.send_message(chat_id, "Please specify a cryptocurrency symbol.\n\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot")

@bot.message_handler(commands=['marketcap'])
def get_top_market_cap(message):
    chat_id = message.chat.id

    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=25&page=1&sparkline=false'
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        bot.send_message(chat_id, 'Sorry, there was an error getting the market capitalization data.\n\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot')
    else:
        message = '📈 Top 25 Cryptocurrencies by Market Capitalization:\n\n'
        for i, currency in enumerate(data):
            name = currency['name']
            symbol = currency['symbol']
            market_cap = currency['market_cap']
            message += f'{i + 1}. {name} ({symbol}) = ${market_cap:,.{price_precision}f}\n'
        message += '\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot'
        bot.send_message(chat_id, message)

@bot.message_handler(commands=['top'])
def get_top_market_price(message):
    chat_id = message.chat.id

    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=25&page=1&sparkline=false'
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        bot.send_message(chat_id, 'Sorry, there was an error getting the market price data.\n\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot')
    else:
        message = '📈 Top 25 Cryptocurrencies by Market Price:\n\n'
        for i, currency in enumerate(data):
            name = currency['name']
            symbol = currency['symbol']
            price = currency['current_price']
            message += f'{i + 1}. {name} ({symbol}) = ${price:,.{price_precision}f}\n'
        message += '\nCryptocurrency Price Bot Functions: /help\n\n@tothemoonprice_bot'
        bot.send_message(chat_id, message)

bot.polling()
