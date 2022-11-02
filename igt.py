import random
from config import *

deck1_number = 0
deck2_number = 0
deck3_number = 0
deck4_number = 0

deck1_temp_losses = []
deck2_temp_losses = []
deck3_temp_losses = []
deck4_temp_losses = []

def gain_loss(decknumber):
    global deck1_number, deck2_number, deck3_number, deck4_number, deck1_temp_losses, deck2_temp_losses, deck3_temp_losses, deck4_temp_losses
    
    if decknumber == 1:
        gain = igt_deck1_gain
        
        if deck1_number % len(igt_deck1_all_losses) == 0:
            deck1_temp_losses = random.sample(igt_deck1_all_losses,len(igt_deck1_all_losses))
        loss = deck1_temp_losses.pop()
        
        deck1_number += 1


    elif decknumber == 2:
        gain = igt_deck2_gain
        
        if deck2_number % len(igt_deck2_all_losses) == 0:
            deck2_temp_losses = random.sample(igt_deck2_all_losses,len(igt_deck2_all_losses))
        loss = deck2_temp_losses.pop()
        
        deck2_number += 1
        
        
    elif decknumber == 3:
        gain = igt_deck3_gain
        
        if deck3_number % len(igt_deck3_all_losses) == 0:
            deck3_temp_losses = random.sample(igt_deck3_all_losses,len(igt_deck3_all_losses))
        loss = deck3_temp_losses.pop()
        
        deck3_number += 1
        
        
    elif decknumber == 4:
        gain = igt_deck4_gain
        
        if deck4_number % len(igt_deck4_all_losses) == 0:
            deck4_temp_losses = random.sample(igt_deck4_all_losses,len(igt_deck4_all_losses))
        loss = deck4_temp_losses.pop()
        
        deck4_number += 1
        
        
    else:
        gain = 'there are only 4 decks'
        loss = 'there are only 4 decks'
        
    return gain, loss
    