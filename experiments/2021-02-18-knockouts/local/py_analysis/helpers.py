
# Get a list of characters in the same order used by Avida
def get_char_list():
    L = []
    for i in range(ord('a'), ord('z') + 1):
        L.append(chr(i))
    for i in range(ord('A'), ord('Z') + 1):
        L.append(chr(i))
    return L

# Load an instruction set and create a map from char -> instruction name
def get_inst_map():
    inst_map = {} 
    char_list = get_char_list() 
    with open('instset-heads.cfg') as in_fp:
        idx = 0
        for line in in_fp: 
            if 'INST ' in line:
                line = line.strip()
                inst = line.split(' ')[1]
                print(inst, idx)
                inst_map[char_list[idx]] = inst
                idx += 1
    return inst_map

# Get a map of inst character -> color that groups like instructions
def get_inst_color_map():
    D = {}
    # https://personal.sron.nl/~pault/ (muted)
    for x in range(ord('a'), ord('c') + 1):
        D[chr(x)] = (238, 204, 102) # no-ops = light yellow
    for x in range(ord('d'), ord('j') + 1):
        D[chr(x)] = (153,68,85)     # flow control = dark red
    for x in range(ord('k'), ord('r') + 1):
        D[chr(x)] = (102,153,204)   # single argument math = light blue
    for x in range(ord('s'), ord('u') + 1):
        D[chr(x)] = (0, 68, 136)    # double argument math = dark blue 
    for x in range(ord('v'), ord('x') + 1):
        D[chr(x)] = (153, 119, 0)   # bio operations = dark yellow
    for x in range(ord('y'), ord('z') + 1):
        D[chr(x)] = (238, 153, 170) # io and sensory = light red
    for x in range(ord('A'), ord('F') + 1):
        D[chr(x)] = (0, 0, 0) # sensory = black
    for x in range(ord('G'), ord('Z') + 1):
        D[chr(x)] = (255, 255, 255) # error = white
    return D
    
            
