from helpers import *
import copy
import pygame
import random

# Render vars
inst_x = 32
inst_width = 128
arrow_width = inst_x / 2
font_size = 10
font = pygame.font.SysFont('ubuntu', size = font_size)
large_font_size = 20
large_font = pygame.font.SysFont('ubuntu', size = large_font_size)

# Basic Avidian class. Handles the bare minimum of execution
class Organism:
    def __init__(self, genome, sensors, in_A = True):
        self.genome = copy.deepcopy(list(genome))
        self.genome_clean = copy.deepcopy(genome)
        self.inst_map = get_inst_map()
        self.inst_color_map = get_inst_color_map()
        self.sensors_work = sensors
        self.in_env_A = in_A
        self.reset()

    # Completely reset organism to it's original state *except* for it's genome (keep mutations)
    def reset(self):
        print('########### RESET ###########')
        self.reg_a = 0 
        self.reg_b = 0
        self.reg_c = 0
        self.reg_a_str = '0'
        self.reg_b_str = '0'
        self.reg_c_str = '0'
        self.mem = []
        self.mem = copy.deepcopy(list(self.genome))
        self.inst_pointer = 0
        self.read_head = 0
        self.write_head = 0
        self.flow_head = 0
        self.stack_a = []
        self.stack_b = []
        self.stack_a_str = []
        self.stack_b_str = []
        self.using_stack_a = True
        self.cur_input = None
        self.copy_history = []
        self.inst_executed = 0
        self.task_map = {
                'NOT' : False,  
                'AND' : False, 
                'OR' : False, 
                'NAND' : False, 
                'ANDNOT' : False, 
                'ORNOT' : False}
        self.input_list = [
                random.randint(0, (1 << 32) - 1), 
                random.randint(0, (1 << 32) - 1),
                random.randint(0, (1 << 32) - 1)]
        # Plastic
        #self.input_list = [252908703, 856220990, 1432502763]
        self.input_idx = 0
        self.output_list = []
        self.output_list_str = []

    # Clear all mutations in genome and reset
    def clear(self):
        print('########### CLEAR ###########')
        self.genome = copy.deepcopy(list(self.genome_clean))
        self.reset()

    # Mutate the given site, to either the next or previous instruction (in order of the a-Z mapping)
    def mutate(self, idx, reverse = False):
        diff = 1
        if reverse:
            diff = -1
        self.genome[idx] = chr(ord(self.genome[idx]) + diff)
        if self.genome[idx] == 'G':
            self.genome[idx] = 'a'
        elif ord(self.genome[idx]) == ord('a') - 1:
            self.genome[idx] = 'F'
        elif ord(self.genome[idx]) == ord('z') + 1:
            self.genome[idx] = 'A'
        elif ord(self.genome[idx]) == ord('A') - 1:
            self.genome[idx] = 'z'
        self.mem[idx] = self.genome[idx]
        print('########### MUTATE ###########')
        self.reset()

    # Add the given value to the active stack. 
    # Optional arg is used to keep track of the var came from
    def stack_push(self, val, s = '???'):
        if self.using_stack_a:
            self.stack_a.append(val)
            self.stack_a_str.append(s)
        else:
            self.stack_b.append(val)
            self.stack_b_str.append(s)

    # Create a list of no-operations instructions following the current instruction
    def get_following_nops(self):
        cur_idx = self.inst_pointer + 1
        L = []
        if cur_idx >= len(self.mem): 
            return L
        while cur_idx != self.inst_pointer:
            inst = self.inst_map[self.mem[cur_idx]]
            if inst == 'nop-A':
                L.append('a')
            elif inst == 'nop-B':
                L.append('b')
            elif inst == 'nop-C':
                L.append('c')
            else:
                break
            cur_idx += 1
            if cur_idx >= len(self.mem):
                cur_idx = 0
        return L
    
    # Given a list of letters in [a,c], return their complements as a list
    def get_complement(self, in_L):
        out_L = []
        for x in in_L:
            if x == 'a':
                out_L.append('b')
            elif x == 'b':
                out_L.append('c')
            elif x == 'c':
                out_L.append('a')
        return out_L

    # Search ahead for the given label (nop pattern). If found return that position in memory
    def find_label(self, label):
        label_size = len(label)
        cur_pos = self.inst_pointer + 1
        start_pos = self.inst_pointer
        while cur_pos != start_pos:
            match = True
            for idx in range(label_size):
                if self.mem[cur_pos + idx] != label[idx]:
                    match = False
                    break
            if match:
                #return cur_pos + label_size - 1
                return cur_pos
            cur_pos += 1
            if cur_pos >= len(self.mem): 
                cur_pos = 0
        return -1


    # Handle the organisms output and check for task performance
    def do_output(self, val, s = '???'):
        print('Output: ', val)
        self.output_list.append(val)
        self.output_list_str.append(s)
        for idx_a in range(len(self.input_list)):
            in_a = self.input_list[idx_a]
            if not self.task_map['NOT']:
                if ~in_a == val:
                    self.task_map['NOT'] = 'True at IP = ' + str(self.inst_pointer)
            for idx_b in range(idx_a + 1, len(self.input_list)):
                in_b = self.input_list[idx_b]
                if not self.task_map['AND']:
                    if in_a & in_b == val:
                        self.task_map['AND'] = 'True at IP = ' + str(self.inst_pointer)
                if not self.task_map['OR']:
                    if in_a | in_b == val:
                        self.task_map['OR'] = True
                        self.task_map['OR'] = 'True at IP = ' + str(self.inst_pointer)
                if not self.task_map['NAND']:
                    if ~(in_a & in_b) == val:
                        self.task_map['NAND'] = 'True at IP = ' + str(self.inst_pointer)
                if not self.task_map['ANDNOT']:
                    if ~in_a & in_b == val or in_a & ~in_b == val:
                        self.task_map['ANDNOT'] = 'True at IP = ' + str(self.inst_pointer)
                if not self.task_map['ORNOT']:
                    if ~in_a | in_b == val or in_a | ~in_b == val:
                        self.task_map['ORNOT'] = 'True at IP = ' + str(self.inst_pointer)

    # Return the next input value
    def get_input(self):
        self.cur_input = self.input_list[self.input_idx]
        self.input_idx = (self.input_idx + 1) % 3
        return self.cur_input

    # Execute the instruction at the current instruction pointer (may also consumer following nops)
    def execute_inst(self):
        char = self.mem[self.inst_pointer]
        inst = self.inst_map[char]
        inst_pointer_inc = 1
        if inst == 'nop-A' or inst == 'nop-B' or inst == 'nop-C' or inst == 'nop-X':
            pass
        elif inst == 'if-n-equ':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                if(nop_list[0] == 'a'):
                    if self.reg_a != self.reg_b:
                        inst_pointer_inc = 2
                    else: 
                        inst_pointer_inc = 3
                elif(nop_list[0] == 'b'):
                    if self.reg_b != self.reg_c:
                        inst_pointer_inc = 2
                    else: 
                        inst_pointer_inc = 3
                elif(nop_list[0] == 'c'):
                    if self.reg_c != self.reg_a:
                        inst_pointer_inc = 2
                    else: 
                        inst_pointer_inc = 3
            else:
                if self.reg_b != self.reg_c:
                    inst_pointer_inc = 1
                else: 
                    inst_pointer_inc = 2
        elif inst == 'if-less':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                if(nop_list[0] == 'a'):
                    if self.reg_a < self.reg_b:
                        inst_pointer_inc = 2
                    else: 
                        inst_pointer_inc = 3
                elif(nop_list[0] == 'b'):
                    if self.reg_b < self.reg_c:
                        inst_pointer_inc = 2
                    else: 
                        inst_pointer_inc = 3
                elif(nop_list[0] == 'c'):
                    if self.reg_c < self.reg_a:
                        inst_pointer_inc = 2
                    else: 
                        inst_pointer_inc = 3
            else:
                if self.reg_b < self.reg_c:
                    inst_pointer_inc = 1
                else: 
                    inst_pointer_inc = 2
        elif inst == 'if-label':
            inst_pointer_inc = 1
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = len(nop_list) + 2
                search_label = self.get_complement(nop_list)
                if len(search_label) > len(self.copy_history):
                    pass
                else:
                    match = True
                    for idx in range(len(search_label)):
                        if search_label[len(search_label) - (idx + 1)] != \
                                self.copy_history[len(self.copy_history) - (idx + 1)]:
                            match = False
                            break
                    if match:
                        inst_pointer_inc = len(nop_list) + 1
        elif inst == 'mov-head':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.inst_pointer = self.flow_head
                    inst_pointer_inc = 0
                elif(nop_list[0] == 'b'):
                    self.read_head = self.flow_head
                elif(nop_list[0] == 'c'):
                    self.write_head = self.flow_head
            else:
                self.inst_pointer = self.flow_head
                inst_pointer_inc = 0
        elif inst == 'jmp-head':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.inst_pointer += 2
                    inst_pointer_int = 0
                    self.inst_pointer += self.reg_c
                elif(nop_list[0] == 'b'):
                    self.read_head += self.reg_c
                elif(nop_list[0] == 'c'):
                    self.write_head += self.reg_c
            else:
                self.inst_pointer += 1
                inst_pointer_int = 0
                self.inst_pointer += self.reg_c
        elif inst == 'get-head':
            val = self.inst_pointer
            val_str = 'IP at ' + str(self.inst_pointer)
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    val = self.inst_pointer 
                    val_str = 'IP at ' + str(self.inst_pointer)
                elif(nop_list[0] == 'b'):
                    val = self.read_head
                    val_str = 'RH at ' + str(self.inst_pointer)
                elif(nop_list[0] == 'c'):
                    val = self.write_head
                    val_str = 'WH at ' + str(self.inst_pointer)
            self.reg_c = val
            self.reg_c_str = val_str
        elif inst == 'set-flow':
            nop_list = self.get_following_nops()
            pos = self.reg_c
            if len(nop_list) > 0:
                print(nop_list)
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    pos = self.reg_a
                elif(nop_list[0] == 'b'):
                    pos = self.reg_b
                elif(nop_list[0] == 'c'):
                    pos = self.reg_c
            if pos < 0: 
                pos = 0
            elif pos > len(self.mem) and pos < 2 * len(self.mem):
                pos -= len(self.mem)
            elif pos > 2 * len(self.mem):
                pos = pos % len(self.mem)
            self.flow_head = pos
        elif inst == 'shift-r':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.reg_a >>= 1
                    self.reg_a_str = '(' + self.reg_a_str + ') >> 1'
                elif(nop_list[0] == 'b'):
                    self.reg_b >>= 1
                    self.reg_b_str = '(' + self.reg_b_str + ') >> 1'
                elif(nop_list[0] == 'c'):
                    self.reg_c >>= 1
                    self.reg_c_str = '(' + self.reg_c_str + ') >> 1'
            else:
                self.reg_b >>= 1
                self.reg_b_str = '(' + self.reg_b_str + ') >> 1'
        elif inst == 'shift-l':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.reg_a <<= 1
                    self.reg_a &= ((1 << 32) - 1) # Truncate to 32 bits
                    self.reg_a_str = '(' + self.reg_a_str + ') << 1'
                elif(nop_list[0] == 'b'):
                    self.reg_b <<= 1
                    self.reg_b &= ((1 << 32) - 1) # Truncate to 32 bits
                    self.reg_b_str = '(' + self.reg_b_str + ') << 1'
                elif(nop_list[0] == 'c'):
                    self.reg_c <<= 1
                    self.reg_c &= ((1 << 32) - 1) # Truncate to 32 bits
                    self.reg_c_str = '(' + self.reg_c_str + ') << 1'
            else:
                self.reg_b <<= 1
                self.reg_b &= ((1 << 32) - 1) # Truncate to 32 bits
                self.reg_b_str = '(' + self.reg_b_str + ') << 1'
        elif inst == 'inc':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.reg_a += 1
                    self.reg_a_str = '(' + self.reg_a_str + ')' + ' + 1'
                elif(nop_list[0] == 'b'):
                    self.reg_b += 1
                    self.reg_b_str = '(' + self.reg_b_str + ')' + ' + 1'
                elif(nop_list[0] == 'c'):
                    self.reg_c += 1
                    self.reg_c_str = '(' + self.reg_c_str + ')' + ' + 1'
            else:
                self.reg_b += 1
                self.reg_b_str = '(' + self.reg_b_str + ')' + ' + 1'
        elif inst == 'dec':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.reg_a -= 1
                    self.reg_a_str = '(' + self.reg_a_str + ')' + ' - 1'
                elif(nop_list[0] == 'b'):
                    self.reg_b -= 1
                    self.reg_b_str = '(' + self.reg_b_str + ')' + ' - 1'
                elif(nop_list[0] == 'c'):
                    self.reg_c -= 1
                    self.reg_c_str = '(' + self.reg_c_str + ')' + ' - 1'
            else:
                self.reg_b -= 1
                self.reg_b_str = '(' + self.reg_b_str + ')' + ' - 1'
        elif inst == 'push':
            nop_list = self.get_following_nops()
            val_str = 'NA'
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    val = self.reg_a
                    val_str = self.reg_a_str
                elif(nop_list[0] == 'b'):
                    val = self.reg_b
                    val_str = self.reg_b_str
                elif(nop_list[0] == 'c'):
                    val = self.reg_c
                    val_str = self.reg_c_str
            else:
                val = self.reg_b
                val_str = self.reg_b_str
            if self.using_stack_a:
                self.stack_a.append(val)
                self.stack_a_str.append(val_str)
            else:
                self.stack_b.append(val)
                self.stack_b_str.append(val_str)
        elif inst == 'pop':
            popped_val = 0
            popped_str = '0'
            if self.using_stack_a:
                if len(self.stack_a) > 0:
                    popped_val = self.stack_a[-1]
                    self.stack_a = self.stack_a[:-1]
                    popped_str = self.stack_a_str[-1]
                    self.stack_a_str = self.stack_a_str[:-1]
            else:
                if len(self.stack_b) > 0:
                    popped_val = self.stack_b[-1]
                    self.stack_b = self.stack_b[:-1]
                    popped_str = self.stack_b_str[-1]
                    self.stack_b_str = self.stack_b_str[:-1]
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.reg_a = popped_val 
                    self.reg_a_str = popped_str
                elif(nop_list[0] == 'b'):
                    self.reg_b = popped_val
                    self.reg_b_str = popped_str
                elif(nop_list[0] == 'c'):
                    self.reg_c = popped_val
                    self.reg_c_str = popped_str
            else:
                self.reg_b = popped_val
                self.reg_b_str = popped_str
        elif inst == 'swap-stk':
            self.using_stack_a = not self.using_stack_a
        elif inst == 'swap':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    tmp = self.reg_a
                    tmp_str = self.reg_a_str
                    self.reg_a = self.reg_b
                    self.reg_a_str = self.reg_b_str
                    self.reg_b = tmp
                    self.reg_b_str = tmp_str
                elif(nop_list[0] == 'b'):
                    tmp = self.reg_b
                    tmp_str = self.reg_b_str
                    self.reg_b = self.reg_c
                    self.reg_b_str = self.reg_c_str
                    self.reg_c = tmp 
                    self.reg_c_str = tmp_str
                elif(nop_list[0] == 'c'):
                    tmp = self.reg_c
                    tmp_str = self.reg_c_str
                    self.reg_c = self.reg_a
                    self.reg_c_str = self.reg_a_str
                    self.reg_a = tmp
                    self.reg_a_str = tmp_str
            else:
                tmp = self.reg_b
                tmp_str = self.reg_b_str
                self.reg_b = self.reg_c
                self.reg_b_str = self.reg_c_str
                self.reg_c = tmp
                self.reg_c_str = tmp_str
        elif inst == 'add':
            res = self.reg_b + self.reg_c
            res_str = '(' + self.reg_b_str + ') + (' + self.reg_c_str + ')'
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.reg_a = res
                    self.reg_a_str = res_str 
                elif(nop_list[0] == 'b'):
                    self.reg_b = res
                    self.reg_b_str = res_str
                elif(nop_list[0] == 'c'):
                    self.reg_c = res
                    self.reg_c_str = res_str
            else:
                self.reg_b = res
                self.reg_b_str = res_str
        elif inst == 'sub':
            res = self.reg_b - self.reg_c
            res_str = '(' + self.reg_b_str + ') - (' + self.reg_c_str + ')'
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.reg_a = res
                    self.reg_a_str = res_str 
                elif(nop_list[0] == 'b'):
                    self.reg_b = res
                    self.reg_b_str = res_str
                elif(nop_list[0] == 'c'):
                    self.reg_c = res
                    self.reg_c_str = res_str
            else:
                self.reg_b = res
                self.reg_b_str = res_str
        elif inst == 'nand':
            res = ~(self.reg_b & self.reg_c)
            res_str = '(' + self.reg_b_str + ') !& (' + self.reg_c_str + ')'
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    self.reg_a = res
                    self.reg_a_str = res_str 
                elif(nop_list[0] == 'b'):
                    self.reg_b = res
                    self.reg_b_str = res_str 
                elif(nop_list[0] == 'c'):
                    self.reg_c = res
                    self.reg_c_str = res_str 
            else:
                self.reg_b = res
                self.reg_b_str = res_str 
        elif inst == 'h-alloc':
            old_len = len(self.mem)
            len_add = len(self.genome)#self.reg_b
            if old_len + len_add >= len(self.genome) * 2:
                len_add = len(self.genome) * 2 - old_len
            print('Allocation an additional', len_add, 'bytes to existing ', old_len)
            #if len_add < 1:
            #    print('Cannot allocate, too short')
            #else:
            if len_add > 0:
                self.mem = self.mem + (['a'] * len_add)
                self.reg_a = old_len
        elif inst == 'h-copy':
            self.mem[self.write_head] = self.mem[self.read_head]
            self.copy_history.append(self.mem[self.read_head])
            self.write_head += 1
            self.read_head += 1
        elif inst == 'h-divide':
            #if self.inst_executed > int(len(self.genome) / 2):
            if len(self.copy_history) >= len(self.genome):
                print('Offspring:')
                print(self.mem[self.read_head:self.write_head])
                self.reset()
                inst_pointer_inc = 0
            else:
                print('Unsuccesful divide: not enough instructions executed')
        elif inst == 'IO':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = 2
                if(nop_list[0] == 'a'):
                    tmp_str = 'in[' + str(self.input_idx) + ',' + str(self.inst_pointer) + ']'
                    self.do_output(self.reg_a, '[' + str(self.inst_pointer) + '] ' + self.reg_a_str) 
                    self.reg_a = self.get_input()
                    self.reg_a_str = tmp_str
                elif(nop_list[0] == 'b'):
                    tmp_str = 'in[' + str(self.input_idx) + ',' + str(self.inst_pointer) + ']'
                    self.do_output(self.reg_b, '[' + str(self.inst_pointer) + '] ' + self.reg_b_str)
                    self.reg_b = self.get_input()
                    self.reg_b_str = tmp_str
                elif(nop_list[0] == 'c'):
                    tmp_str = 'in[' + str(self.input_idx) + ',' + str(self.inst_pointer) + ']'
                    self.do_output(self.reg_c, '[' + str(self.inst_pointer) + '] ' + self.reg_b_str) 
                    self.reg_c = self.get_input()
                    self.reg_c_str = tmp_str 
            else:
                tmp_str = 'in[' + str(self.input_idx) + ',' + str(self.inst_pointer) + ']'
                self.do_output(self.reg_b, '[' + str(self.inst_pointer) + '] ' + self.reg_b_str)
                self.reg_b = self.get_input()
                tmp_str = self.reg_b
        elif inst == 'h-search':
            nop_list = self.get_following_nops()
            if len(nop_list) > 0:
                inst_pointer_inc = len(nop_list) + 1
                pos = self.find_label(self.get_complement(nop_list))
                self.reg_b = pos - self.inst_pointer
                self.reg_c = len(nop_list)
                self.flow_head = pos + len(nop_list)
            else:
                self.reg_b = 0
                self.reg_c = 0
                self.flow_head = self.inst_pointer + 1
        elif inst == 'sense-react-NAND':
            if(not self.sensors_work):
                pass
            else:
                if(not self.in_env_A):
                    self.stack_push(1, 'sense-pos')
                else:
                    self.stack_push(-1, 'sense-neg')
        elif inst == 'sense-react-NOT':
            if(not self.sensors_work):
                pass
            else:
                if(self.in_env_A):
                    self.stack_push(1, 'sense-pos')
                else:
                    self.stack_push(-1, 'sense-neg')
        elif inst == 'sense-react-AND':
            if(not self.sensors_work):
                pass
            else:
                if(self.in_env_A):
                    self.stack_push(1, 'sense-pos')
                else:
                    self.stack_push(-1, 'sense-neg')
        elif inst == 'sense-react-ORN':
            if(not self.sensors_work):
                pass
            else:
                if(not self.in_env_A):
                    self.stack_push(1, 'sense-pos')
                else:
                    self.stack_push(-1, 'sense-neg')
        elif inst == 'sense-react-OR':
            if(not self.sensors_work):
                pass
            else:
                if(self.in_env_A):
                    self.stack_push(1, 'sense-pos')
                else:
                    self.stack_push(-1, 'sense-neg')
        elif inst == 'sense-react-ANDN':
            if(not self.sensors_work):
                pass
            else:
                if(not self.in_env_A):
                    self.stack_push(1, 'sense-pos')
                else:
                    self.stack_push(-1, 'sense-neg')


        self.inst_pointer += inst_pointer_inc
        self.inst_executed += 1

    # Render the execution heads
    def render_heads(self, surf):
        # Instruction pointer
        pygame.draw.polygon(surf, (238,0,0), \
                ((int(inst_x / 2), self.inst_pointer * font_size), \
                (inst_x, int((self.inst_pointer + 0.5) * font_size)), \
                (int(inst_x / 2), (self.inst_pointer + 1) * font_size)))
        # Flow head
        if self.flow_head < len(self.genome):
            if self.inst_pointer == self.flow_head:
                pygame.draw.polygon(surf, (238,238,0), \
                    ((0, self.flow_head * font_size), \
                    (int(inst_x / 2), int((self.flow_head + 0.5) * font_size)), \
                    (0, (self.flow_head + 1) * font_size)))
            else:
                pygame.draw.polygon(surf, (238,238,0), \
                    ((int(inst_x / 2), self.flow_head * font_size), \
                    (inst_x, int((self.flow_head + 0.5) * font_size)), \
                    (int(inst_x / 2), (self.flow_head + 1) * font_size)))
        else:
            x = inst_width +  inst_x * 3
            y_top = (self.flow_head - len(self.genome)) * font_size
            pygame.draw.polygon(surf, (238,238,0), \
                ( (x - arrow_width,  y_top), \
                (x, y_top + int(0.5 * font_size)), \
                (x - arrow_width,y_top + font_size) ) )
        # Read head
        pygame.draw.polygon(surf, (0,238,0), \
                ((inst_x + inst_width + arrow_width, self.read_head * font_size), \
                (inst_x + inst_width, int((self.read_head + 0.5) * font_size)), \
                (inst_x + inst_width + arrow_width, (self.read_head + 1) * font_size)))
        # Write head
        if self.write_head < len(self.genome):
            if self.read_head == self.write_head:
                pygame.draw.polygon(surf, (0,0,238), 
                        ((inst_x + inst_width + arrow_width * 2, self.write_head * font_size), \
                        (inst_x + inst_width + arrow_width, int((self.write_head+0.5)*font_size)), \
                        (inst_x + inst_width + arrow_width * 2, (self.write_head + 1) * font_size)))
            else:
                pygame.draw.polygon(surf, (0,0,238), \
                        ((inst_x + inst_width + arrow_width, self.write_head * font_size), \
                        (inst_x + inst_width, int((self.write_head + 0.5) * font_size)), \
                        (inst_x + inst_width + arrow_width, (self.write_head + 1) * font_size)))
        else:
            x = inst_x * 3 + inst_width * 2
            pygame.draw.polygon(surf, (0,0,238), 
                    ((x + int(inst_x / 2), (self.write_head - len(self.genome)) * font_size), \
                    (x, int((self.write_head - len(self.genome) + 0.5) * font_size)), \
                    (x + int(inst_x / 2), (self.write_head + 1 - len(self.genome)) * font_size)))

                    
    # Render the status of the organism's registers, stacks, etc as text
    def render_states(self, surf):
        # Registers
        surf.blit(large_font.render('Reg A:' + str(self.reg_a) + '; '  + str(self.reg_a_str), \
                0, (255, 255, 255)), (512, 64))
        surf.blit(large_font.render('Reg A:' + \
                format(self.reg_a if self.reg_a >= 0 else self.reg_a + (1 << 32), '032b'),\
                0, (255, 255, 255)), (512 + 32, 64 + large_font_size))
        surf.blit(large_font.render('Reg B:' + str(self.reg_b) + '; ' + str(self.reg_b_str), \
                0, (255, 255, 255)), (512, 64 + large_font_size * 2))
        surf.blit(large_font.render('Reg B:' + \
                format(self.reg_b if self.reg_b >= 0 else self.reg_b + (1 << 32), '032b'),\
                0, (255, 255, 255)), (512 + 32, 64 + large_font_size * 3))
        surf.blit(large_font.render('Reg C:' + str(self.reg_c) + '; ' + str(self.reg_c_str), \
                0, (255, 255, 255)), (512, 64 + large_font_size * 4))
        surf.blit(large_font.render('Reg C:' + format(self.reg_c, '032b'), 0, (255, 255, 255)), \
                (512 + 32, 64 + large_font_size * 5))
        # Heads
        surf.blit(large_font.render('IP:' + str(self.inst_pointer), 0, (238, 0, 0)), \
                (512, 64 + large_font_size * 6))
        surf.blit(large_font.render('RH:' + str(self.read_head), 0, (0, 238, 0)), \
                (512, 64 + large_font_size * 7))
        surf.blit(large_font.render('WH:' + str(self.write_head), 0, (0, 0, 238)), \
                (512, 64 + large_font_size * 8))
        surf.blit(large_font.render('FH:' + str(self.flow_head), 0, (238, 238,0)), \
                (512, 64 + large_font_size * 9))
        # Stacks
        if self.using_stack_a:
            surf.blit(large_font.render('SA:' + str(self.stack_a) + str(self.stack_a_str), \
                    0, (255, 255,255)), (512, 64 + large_font_size * 10))
            surf.blit(large_font.render('SB:' + str(self.stack_b) + str(self.stack_b_str), \
                    0, (150, 150,150)), (512, 64 + large_font_size * 11))
        else:
            surf.blit(large_font.render('SA:' + str(self.stack_a) + str(self.stack_a_str), \
                    0, (150,150,150)), (512, 64 + large_font_size * 10))
            surf.blit(large_font.render('SB:' + str(self.stack_b) + str(self.stack_b_str), \
                0, (255,255,255)), (512, 64 + large_font_size * 11))
        # Tasks
        surf.blit(large_font.render('NOT:' + str(self.task_map['NOT']), 0, (255, 255,255)), \
                (512, 64 + large_font_size * 12))
        surf.blit(large_font.render('AND:' + str(self.task_map['AND']), 0, (255, 255,255)), \
                (512, 64 + large_font_size * 13))
        surf.blit(large_font.render('OR:' + str(self.task_map['OR']), 0, (255, 255,255)), \
                (512, 64 + large_font_size * 14))
        surf.blit(large_font.render('NAND:' + str(self.task_map['NAND']), 0, (255, 255,255)), \
                (512, 64 + large_font_size * 15))
        surf.blit(large_font.render('ANDNOT:' + str(self.task_map['ANDNOT']), 0, (255, 255,255)), \
                (512, 64 + large_font_size * 16))
        surf.blit(large_font.render('ORNOT:' + str(self.task_map['ORNOT']), 0, (255, 255,255)), \
                (512, 64 + large_font_size * 17))
        # IO
        surf.blit(large_font.render('Inputs:' + str(self.input_list), 0, (255, 255,255)), \
                (512, 64 + large_font_size * 18))
        cur_idx = 19
        for i in range(len(self.input_list)):
            val = self.input_list[i]
            surf.blit(large_font.render(format(val if val >= 0 else val + (1 << 32), '032b'),\
                    0, (255, 255, 255)), (512 + 32, 64 + large_font_size * cur_idx))
            cur_idx += 1
        surf.blit(large_font.render('Outputs:' + str(self.output_list), 0, (255, 255,255)), \
                (512, 64 + large_font_size * cur_idx))
        cur_idx += 1
        for i in range(len(self.output_list)):
            val = self.output_list[i]
            surf.blit(large_font.render(format(val if val >= 0 else val + (1 << 32), '032b') + \
                    '; ' + str(self.output_list_str[i]),\
                    0, (255, 255, 255)), (512 + 32, 64 + large_font_size * cur_idx))
            cur_idx += 1
                

    # Render the organism's genome
    def render_genome(self, surf):
        for locus_idx in range(len(self.genome)):
            char = self.mem[locus_idx]
            inst_name = self.inst_map[char]
            surf.blit(font.render(str(locus_idx), 0, (255,255,255)), (0, locus_idx * font_size))
            pygame.draw.rect(surf, self.inst_color_map[char], \
                    (inst_x, locus_idx * font_size, inst_width, font_size))
            surf.blit(font.render(inst_name, 0, (255,255,255)), (inst_x, locus_idx * font_size))
        if len(self.mem) > len(self.genome): # If a h-alloc has executed, draw the offspring memory
            x = inst_width + inst_x * 3
            for locus_idx in range(len(self.genome), len(self.mem)):
                char = self.mem[locus_idx]
                inst_name = self.inst_map[char]
                pygame.draw.rect(surf, self.inst_color_map[char], \
                        (x, (locus_idx - len(self.genome)) * font_size, inst_width, font_size))
                surf.blit(font.render(inst_name, 0, (255,255,255)),\
                        (x, (locus_idx - len(self.genome)) * font_size))

    # Call all render subprocesses
    def render(self, surf):
        self.render_genome(surf)
        self.render_heads(surf)
        self.render_states(surf)
