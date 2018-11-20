def twos_convert(line):
    if (line[16] == '1'):
            return (-1*(0b1111111111111111 - int(line[16:32], 2) + 1))
    else:
            return int(line[16:32], 2)
    
input_file = open("i_mem.txt", "r")
print("add, sub, xor, addi, beq, bne, slt, lw, sw")
instList = []
multi_cycles = 0
multic_3 = 0
multic_4 = 0
multic_5 = 0
count = 0
for code in input_file:
    line = code.replace("\t", "")
    line = line.replace(" ","")     # remove spaces anywhere in line
    if (line == "\n"):              # empty lines ignored
        continue
    line = line.replace("\n","")
    line = format(int(line,16), "032b")
    instList.append(line)
    
input_file.close()
mem_size = 1024
memList = [0 for i in range(mem_size)]
r = [0,0,0,0,0,0,0,0]
pc = 0

while(pc < len(instList)):
    line = instList[pc]
        
    #r-type
    if(line[0:6] == '000000'):
        multi_cycles += 4 #rtype have 4 cycles
        #add
        if(line[26:32] == '100000'):
            #rd = rs + rt
            r[int(line[16:21],2)] = r[int(line[6:11],2)] + r[int(line[11:16],2)]
            pc = pc + 1
           
        #sub
        elif(line[26:32] == '100010'):
            #rd = rs - rt
            r[int(line[16:21],2)] = r[int(line[6:11],2)] - r[int(line[11:16],2)]
            pc = pc + 1
        #xor
        elif(line[26:32] == '100110'):
            #rd = rs ^ rt
            r[int(line[16:21],2)] = r[int(line[6:11],2)] ^ r[int(line[11:16],2)]
            pc = pc + 1
        #slt
        elif(line[26:32] == '101010'):
            #rd = 1 if(rs < rt)
            if (r[int(line[6:11],2)] < r[int(line[11:16],2)]):
                r[int(line[16:21],2)] = 1
            else:
                r[int(line[16:21],2)] = 0
            pc = pc + 1
            
    #addi
    elif(line[0:6] == '001000'):
        multi_cycles += 4
        #rt = rs + imm
        imm = twos_convert(line)
        r[int(line[11:16],2)] = r[int(line[6:11],2)] + imm
        pc = pc + 1
    #beq
    elif(line[0:6] == '000100'):
        multi_cycles += 3
        #if(rs == rt) then pc = imm + pc
        temp_pc = pc
        imm = twos_convert(line)
        if(r[int(line[6:11],2)] is r[int(line[11:16],2)]):
            pc = pc + imm + 1
        else:
            pc = pc + 1
        if pc is temp_pc:
            count = count + 1
            break
    #bne
    elif(line[0:6] == '000101'):
        multi_cycles += 3
        #if(rs != rt) then pc = imm + pc
        temp_pc = pc
        imm = twos_convert(line)
        if(r[int(line[6:11],2)] != r[int(line[11:16],2)]):
            pc = pc + imm + 1
        else:
            pc = pc + 1
        if pc is temp_pc:
            break
    #lw
    elif(line[0:6] == '100011'):
        multi_cycles += 5
        #rt = MEM[rs + imm]
        offset = int((r[int(line[6:11],2)] + int(line[16:32],2) - 8192)/4)
        r[int(line[11:16],2)] = memList[offset]
        pc = pc + 1
    #sw
    elif(line[0:6] == '101011'):
        multi_cycles += 4
        #MEM[rs + imm] = rt
        offset = int((r[int(line[6:11],2)] + int(line[16:32],2) - 8192)/4)
        memList[offset] = r[int(line[11:16],2)]
        pc = pc + 1  
    else:
        print("Unknown instruction:"+ line)
        break;
    count = count + 1


print("Final DIC count is: {}".format(count))
