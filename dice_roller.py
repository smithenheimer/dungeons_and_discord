import os
import re
import logging
import argparse
from random import randint, choices

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s | %(levelname)s - %(lineno)s - %(message)s")
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(log_format)
logger.addHandler(sh)

def roll_dice(input_str):
    ''' DOC STRING!

    input string here

    '''

    logger.debug('Rolling dice')
    input_str = '+'+input_str+'+'

    remove_list = [' ',',','.',':']
    for remove_str in remove_list:
        input_str.replace(remove_str,'')

    dice_pattern = '([+\-])(\d*)d(\d+)'
    static_pattern = '([+\-])(\d+)(?=[+\-])'
    
    logger.debug(f'Inputs: {input_str}')

    dice_results = re.findall(dice_pattern, input_str)
    static_results = re.findall(static_pattern, input_str)

    roll_total = 0
    roll_list = []
    static_list = []

    for expression in dice_results:
        sign = expression[0]

        if expression[1]: qty = int(expression[1])
        else: qty = 1

        sides = int(expression[2])
        rolls = choices(list(range(1, sides+1)), k=qty)

        if sign == '-':
            rolls = [x * (-1) for x in rolls]
            
        total = sum(rolls)
        roll_list.append(rolls)
        roll_total += total

    for expression in static_results:
        sign = expression[0]
        val = int(expression[1])

        if sign == '-':
            val = val * (-1)

        static_list.append(val)
        roll_total += val

    logger.debug(f'Roll total: {roll_total}')

    return roll_total, roll_list, static_list
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_str')
    args = parser.parse_args()
    roll_total, roll_list, static_list = roll_dice(args.input_str)

    print(roll_total)
    print(roll_list)
    print(static_list)
