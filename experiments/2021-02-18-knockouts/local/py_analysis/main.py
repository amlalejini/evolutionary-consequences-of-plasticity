import pygame

pygame.init()
pygame.font.init()

from helpers import *
from avida import *

# Rendering vars
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height))#, flags = pygame.FULLSCREEN)

# Avida vars
# Non-plastic
genome = 'EwqfjjagcxyazmeBalsupABmjicnfBErfoastAmyEfEybrcuuawwybyAudszlliFsiazyyaohquvdkhuEftlwbmfzfFozvvvxglE'
# Non-plastic genome #1
#genome = 'FnyAwjagcvEjyculaucrClyybuCEyrBbCecxjayvemuqBxBBmlsvfsrcroFemCAjwmnfubkymEjscAvqdcoBqfBmpqDzvvvvxgfi'
#genome = 'jnoAwjagcvEfycflaucyClyybuCEyrBbCecxjayvemuqBxBBmlsvfsrcroFemCAjwmnfuskymEjscAvqdcoBqfBmpqDzvvvvxgfi'
# Static
#genome = 'wBjagcsvrfDFycDutcmwdccdApEdvyCooujuyuafrbypFyadjBvubymarajfqxyicicfjBycsacumAkavcrscjFtycyzvvvvxgay'
# Plastic 
#genome = 'aaaBwDfvEovjzawsvCCEspczcztrcyohcldlianDpycubrDdbyububycyupcvecuwfftcjaymcymbvovjbBsyecudyzvvfcaxgab'
# Modified ancestor
#genome = 'wzcagcccczvfcaxgab'
# Modified ancestor (with NOT)
#genome = 'wzcagccybobpcubybcczvfcaxgab'
# Modified ancestor (with NAND)
#genome = 'wzcagccybycubybcczvfcaxgab'
# State vars

org = Organism(genome, False)
#org = Organism(genome, True, False) 
#org = Organism(genome, True, True) 

# Flow control vars
done = False
play = False

# Rendering vars
inst_x = 32
inst_width = 128
arrow_width = inst_x / 2
font_size = 10
large_font_size = 20


#### MAIN LOOP
while not done:

    # Handle input
    evt = pygame.event.poll()
    if evt.type == pygame.QUIT: # Quit
        done = True
        break
    elif evt.type == pygame.KEYDOWN:
        if evt.key == pygame.K_q or evt.key == pygame.K_ESCAPE: # Quit
            done = True
            break
        elif evt.key == pygame.K_RIGHT or evt.key == pygame.K_DOWN or \ 
                evt.key == pygame.K_SPACE or evt.key == pygame.K_RETURN: # Single step 
            org.execute_inst()
        elif evt.key == pygame.K_p: # Play / pause
            play = not play
        elif evt.key == pygame.K_r: # Reset the organism's execution
            org.reset()
            play = False
        elif evt.key == pygame.K_c: # Completely reset organism (including mutations)
            org.clear()
            play = False
    elif evt.type == pygame.MOUSEBUTTONDOWN: # If an instruction is clicked, mutate it
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > inst_x and mouse_pos[0] < inst_x + inst_width:
            idx = mouse_pos[1] // font_size
            if evt.button == 1:
                org.mutate(idx)
            else:
                org.mutate(idx, True)
    # If we're auto-updating, advance a frame
    if play:
        org.execute_inst()

    # Render!
    screen.fill((0,0,0))
    org.render(screen) 
    pygame.display.flip()

pygame.quit()
