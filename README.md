# Fung Go's Telegram Bot

### Setup Bot

#### Install pyTelegramBotAPI Dependencies

Please ensure that you have installed `Python 3.x` and `pip` in system.

Then, run this command:

```
pip install pyTelegramBotAPI
```

#### Configure Bot Token

Contact [@BotFather](https://t.me/BotFather) in Telegram and create your own bot.

Copy token and write `token_config.py` like this:

```Python
### Enter your own bot token plz
TELEBOT_TOKEN = '303421XXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
```

#### Configure Other Config

For Search By Image functions:

Write `other_config.py`:

```Python
LINUX_HOST_IMAGE_PATH = '/var/www/html/public/images/'
PUBLIC_IMAGE_PATH = 'https://example.com/images/'
```

### Start

```
python ./bot_main.py
```

### License

```
GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Copyright (C) 2017 Fung Go

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions.
```
