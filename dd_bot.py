import os
import sys
import pandas as pd
import numpy as np
import re
from datetime import datetime
from dotenv import load_dotenv
import random
# import psycopg2
import sqlalchemy as sqldb
import traceback

import discord
from discord.ext import commands
from discord import Intents
intents = Intents.default()
intents.members = True

from dice_roller import roll_dice

# Load ENV
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

PG_SERVER = 'postgresql'
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PASSWORD')
PG_HOST = os.getenv('POSTGRES_HOSTNAME')
PG_DB = os.getenv('DATABASE_NAME')

USER_TABLE = 'dd_users'
TIP_TABLE = 'transactions'

# Logging Handler
from loguru import logger
log_path = r'logs'
if not os.path.exists(log_path):
    os.mkdirs(log_path)
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add(os.path.join(log_path, 'dd_bot.log'), rotation="00:00")

# START BOT!
bot = commands.Bot(intents=intents, command_prefix='!')
logger.debug('Bot initialized')

@bot.event
async def on_ready():
    logger.debug(f'{bot.user.name} is connected to Discord!')

# COMMANDS

@bot.command(name='listmembers', help='List server members')
async def list_members(ctx, *args):
    ''' List current server members '''
    logger.debug('Listing members')
    logger.debug(args)

    guild = ctx.guild
    await ctx.send(f'**Server Name: {guild.name}**')
    user_list = f'Server Size: {len(guild.members)} members\n'
    for member in guild.members:
        user_list+=f' - {member.display_name} ({member}, {member.id})\n'

    await ctx.send(user_list)
    return
    
@bot.command(name='tip', help='Don\'t forget to tip your healer! (@user)')
async def tip(ctx, *args):
    ''' Tip server member, adding gold transaction to transaction history '''
    logger.debug('Tipping user')
    logger.debug(args)

    timestamp = datetime.now()
    source_user = ctx.message.author.id
    nickname_lookup = {str(member.id):member.display_name for member in ctx.guild.members}
    users = []
    gp = 5
    
    tag_pattern = r'<@(.*)>'
    gp_pattern = r'(\d*)gp'

    for arg in args:
        tag_results = re.search(tag_pattern, arg.replace('!',''))
        if tag_results:
            user_id = tag_results.group(1)
            logger.debug(f'User: {user_id}')
            users.append(user_id)
            continue

        gp_results = re.search(gp_pattern, arg)
        if gp_results:
            gp = gp_results.group(1)
            gp = int(gp)
            logger.debug(f'{gp} gold')
            continue

    for user_id in users:
        raw_query = f""" insert into {TIP_TABLE} (id, source, gp, timestamp, server) """ \
                    f""" values ('{user_id}','{source_user}',{gp},'{timestamp}','{ctx.guild.name}'); """
        logger.debug(raw_query.strip())
        scribe = Scribe()
        result = scribe.query(raw_query)
        scribe.close()
        logger.debug(result)

        tip_message = f'Tipping {nickname_lookup[user_id]} {gp} gold!'
        logger.debug(tip_message)
        await ctx.send(tip_message)
    return
   
@bot.command(name='balance', help='List users and gold balances')
async def balance(ctx, *args):
    ''' List gold balances '''
    logger.debug('Listing point balances')
    logger.debug(args)
    
    tag_pattern = r'<@(.*)>'
    nickname_lookup = {str(m.id):m.display_name for m in ctx.guild.members}

    scribe = Scribe()
    raw_query = f""" select * from {TIP_TABLE} """ \
                f"""where server like '{ctx.guild.name}' """
    values = scribe.select(raw_query)
    scribe.close()

    columns = ['id', 'source', 'gp', 'timestamp', 'server']
    df = pd.DataFrame(values, columns=columns)

    if len(args) > 0:
        users = []
        for arg in args:
            results = re.search(tag_pattern, arg.replace('!',''))
            if results:
                user = results.group(1)
                users.append(user)

    else:
        users = list(df['id'].unique())

    balance_response = '** Current Gold Balance **\n'
    for user in users:
        try:
            total = int(df['gp'][df['id'] == user].sum())
            display_name = nickname_lookup[user]
            balance_response += f'{display_name.capitalize()} - {total}gp\n'
            logger.debug(f'{user}:{total}')
        except:
            err = f'Could not resolve user {user}'
            logger.debug(err)
            await ctx.send(err)

    await ctx.send(balance_response)
    return

@bot.command(name='roll', help='roll dice! (eg. 2d6+2)')
async def roll(ctx, *args):
    logger.debug('Parsing command')
    logger.debug(args)

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
        f'{author_name}. Good to see you. But if you’re here, who’s guarding Hades?',
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
        (['boom','baby'],'https://media.giphy.com/media/11SkMd003FMgW4/giphy.gif'),
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
    
class Scribe:
    def __init__(self):
        self.engine_pattern = '{}://{}:{}@{}/{}'
        self.engine_name = self.engine_pattern.format(PG_SERVER,
                                                PG_USER, 
                                                PG_PW, 
                                                PG_HOST, 
                                                PG_DB)
        self.connect()

    def connect(self):
        self.engine = sqldb.create_engine(self.engine_name)
        self.connection = self.engine.connect()

    def close(self):
        self.connection.close()
        self.engine.dispose()

    def query(self, query):
        logger.debug('Executing query')
        result = None
        try:
            result = self.connection.execute(query)
        except Exception as e:
            logger.error(f'Error - {e}')
            logger.error(f'Traceback - {traceback.format_exc()}')
        logger.debug('Success')

    def select(self, query):
        logger.debug('Executing query')
        result = None
        try:
            result = self.connection.execute(query).fetchall()
        except Exception as e:
            logger.error(f'Error - {e}')
            logger.error(f'Traceback - {traceback.format_exc()}')
        logger.debug('Success')
        return result

# MAIN

if __name__ == "__main__":
    bot.run(TOKEN)
