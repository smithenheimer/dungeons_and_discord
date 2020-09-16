import os
import sys
import re
from datetime import datetime
from dotenv import load_dotenv
import random
from discord.ext import commands
import psycopg2
import traceback
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from dice_roller import roll_dice

# Load ENV
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Logging Handler
log_root = r'logs'
date = datetime.today().strftime('%Y-%m-%d')
log_format = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s | %(levelname)s - %(lineno)s - %(message)s")
if not os.path.exists(log_root):
    os.makedirs(log_root)
log_file = os.path.join(log_root, f'{date}_movie-bot.log')

fh = logging.FileHandler(log_file, mode='a')
fh.setLevel(logging.DEBUG)
fh.setFormatter(log_format)
logger.addHandler(fh)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(log_format)
logger.addHandler(sh)

# START BOT!
bot = commands.Bot(command_prefix='!')
logger.debug('Bot initialized')

@bot.event
async def on_ready():
    logger.debug(f'{bot.user.name} is connected to Discord!')

# COMMANDS

@bot.command(name='add', help='Add a movie to the movie list')
async def add(ctx, *args):
    logger.debug('Parsing command')

@bot.command(name='roll', help='roll dice!')
async def roll(ctx, *args):
    logger.debug('Parsing command')

    input_str = ''.join(args)
    roll_total, roll_list, static_list = roll_dice(input_str)

    user = parse_username(ctx.message.author)

    total_response = f"{user}'s roll: **{roll_total}**"
    roll_data = ''
    
    if len(roll_list) > 0:
        for roll_set in roll_list:

            dice_text = ''
            for roll_val in roll_set:
                dice_text += f'{roll_val}, '
            dice_text = f'({dice_text[:-2]}) + '

            roll_data += dice_text
            
    if len(static_list) > 0:
        for static_val in static_list:
            roll_data += f'({static_val}) + '

    if len(roll_data) > 0:
        roll_response = f"{total_response} ||`{roll_data[:-3]}`||"
    else: 
        roll_response = f"{total_response}"

    await ctx.send(roll_response)

    return

@bot.event
async def on_reaction_add(reaction, user):
    logger.debug('Parsing command')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Query formatted username
    author_name = str(message.author.nick)
    if author_name == 'None':
        author_name = str(message.author).split('#')[0]
    author_name = author_name.capitalize()

    # TODO: Break this into a separate file?
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
        'Noice. Smort.',
        'Toight',
        f'{author_name} is an amazing human / genius',
        'Title of your sextape',
        f'{author_name}, with all due respect, I am gonna completely ignore everything you just said.',
        f'{author_name}. Good to see you. But if you’re here, who’s guarding Hades?'
    ]

    # Call patterns & responses!
    response = None
    message_pattern = message.content.lower()
    easter_egg_list = [
        (['99!'], random.choice(brooklyn_99_quotes)),
        (['difficult','hard','challenging'], 'No no no, super easy, barely an inconvenience'),
        (['inquisition','inquisitor','inquisitive','inquiry','inquire'], 'No one expects the Spanish Inquisition!'),
        (['treasure'], 'Maybe the real treasure was the friends we made along the way'),
        (['pivot'],'https://media.giphy.com/media/3nfqWYzKrDHEI/giphy.gif'),
        (['boom','baby'],'https://media.giphy.com/media/11SkMd003FMgW4/giphy.gif')
    ]

    # Check for easter eggs
    for call, response_str in easter_egg_list:
        if any(x in message_pattern for x in call):
            response = response_str

    if response:
        logger.debug('Easter egg!')
        await message.channel.send(response)

    await bot.process_commands(message)

# ERR HANDLING

@bot.event
async def on_error(event, *args, **kwargs):
    try:
        logger.error(f'{event} - {args[0]}\n')
    except Exception as e:
        logger.error(f'unknown error - {e}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Command Didn\'t Work.')
        
# UTILITIES

def parse_username(author_obj):
    try:
        user = str(author_obj.display_name)
    except:
        user = 'None'

    if user == 'None':
        user = str(author_obj).split('#')[0]
    user = user.capitalize()

    return user

# MAIN

if __name__ == "__main__":
    bot.run(TOKEN)
