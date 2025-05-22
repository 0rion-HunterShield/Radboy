from itertools import combinations_with_replacement
from datetime import datetime
import sys,os

def get_bill_combinations(amount, denominations):
    """
    Generates all possible bill combinations for a given amount using specified denominations.

    Args:
        amount (float): The target amount.
        denominations (list): A list of bill denominations (integers or floats).

    Returns:
        list: A list of tuples, where each tuple represents a bill combination.
              Returns an empty list if no combination is found or if the input is invalid.
    """
    if not isinstance(amount, (int, float)) or amount <= 0:
        return []
    if not all(isinstance(d, (int, float)) and d > 0 for d in denominations):
        return []

    amount_cents = int(amount * 100)
    denominations_cents = [int(d * 100) for d in denominations]

    valid_combinations = []
    counter=0
    for r in range(0, amount_cents // min(denominations_cents) + 1):
      last=os.get_terminal_size().columns
      for combination_tuple in combinations_with_replacement(denominations_cents, r):
        
        if counter%100000==0:
            msg=f"{'\b'*last}"+f"Processing {counter}"
            #last=len(msg)
            sys.stdout.write(msg)
            sys.stdout.flush()
        counter+=1
        if sum(combination_tuple) == amount_cents:
          #valid_combinations.append()
          '''
          msg=f"{'\b'*last}processing... {datetime.now().ctime()}"
          last=len(msg)
          sys.stdout.write(msg)
          sys.stdout.flush()
          '''
          yield tuple(x / 100 for x in combination_tuple)
    
