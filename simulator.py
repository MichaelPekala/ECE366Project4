def twos_convert(line):
    if (line[16] == '1'):
            return (-1*(0b1111111111111111 - int(line[16:32], 2) + 1))
    else:
            return int(line[16:32], 2)
    
input_file = open("i_mem.txt", "r")
file = open("MulticycleInfo.txt","w")
print("Supported instructions: add, sub, xor, addi, beq, bne, slt, lw, sw\n")
instList = []
multi_cycles = 0
multi_3 = 0
multi_4 = 0
multi_5 = 0
count = 0
hazard = [-1,-1]
hazard_c = 0
for code in input_file:
    line = code.replace("\t", "")
    line = line.replace(" ","")     # remove spaces anywhere in line
    if (line == "\n"):              # empty lines ignored
        continue
    line = line.replace("\n","")
    line = format(int(line,16),"032b")
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
            if ((hazard[0] is (int(line[6:11],2) or int(line[11:16],2))) or 
            hazard[1] is (int(line[6:11],2) or int(line[11:16],2))):
              print("HAZARD")
              hazard_c += 1
            r[int(line[16:21],2)] = r[int(line[6:11],2)] + r[int(line[11:16],2)]
            file.write("Instruction "+repr(count)+": add - 4 cycles \n")
            multi_4 += 1
            pc = pc + 1
            hazard.append(int(line[16:21],2))
            hazard.pop(0)
           
        #sub
        elif(line[26:32] == '100010'):
            #rd = rs - rt
            r[int(line[16:21],2)] = r[int(line[6:11],2)] - r[int(line[11:16],2)]
            file.write("Instruction "+repr(count)+": sub - 4 cycles \n")
            multi_4 += 1
            pc = pc + 1
        #xor
        elif(line[26:32] == '100110'):
            #rd = rs ^ rt
            r[int(line[16:21],2)] = r[int(line[6:11],2)] ^ r[int(line[11:16],2)]
            file.write("Instruction "+repr(count)+": xor - 4 cycles \n")
            multi_4 += 1
            pc = pc + 1
        #slt
        elif(line[26:32] == '101010'):
            #rd = 1 if(rs < rt)
            if (r[int(line[6:11],2)] < r[int(line[11:16],2)]):
                r[int(line[16:21],2)] = 1
            else:
                r[int(line[16:21],2)] = 0
            file.write("Instruction "+repr(count)+": slt - 4 cycles \n")
            multi_4 += 1
            pc = pc + 1
            
    #addi
    elif(line[0:6] == '001000'):
        multi_cycles += 4
        #rt = rs + imm
        imm = twos_convert(line)
        r[int(line[11:16],2)] = r[int(line[6:11],2)] + imm
        file.write("Instruction "+repr(count)+": addi - 4 cycles \n")
        multi_4 += 1
        pc = pc + 1
    #beq
    elif(line[0:6] == '000100'):
        multi_cycles += 3
        multi_3 += 1
        #if(rs == rt) then pc = imm + pc
        temp_pc = pc
        imm = twos_convert(line)
        file.write("Instruction "+repr(count)+": beq - 3 cycles \n")
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
        multi_3 += 1
        #if(rs != rt) then pc = imm + pc
        temp_pc = pc
        imm = twos_convert(line)
        file.write("Instruction "+repr(count)+": bne - 3 cycles \n")
        if(r[int(line[6:11],2)] != r[int(line[11:16],2)]):
            pc = pc + imm + 1
        else:
            pc = pc + 1
        if pc is temp_pc:
            break
    #lw
    elif(line[0:6] == '100011'):
        multi_cycles += 5
        multi_5 += 1
        #rt = MEM[rs + imm]
        offset = int((r[int(line[6:11],2)] + int(line[16:32],2) - 8192)/4)
        r[int(line[11:16],2)] = memList[offset]
        file.write("Instruction "+repr(count)+": lw - 5 cycles \n")
        pc = pc + 1
    #sw
    elif(line[0:6] == '101011'):
        multi_cycles += 4
        #MEM[rs + imm] = rt
        offset = int((r[int(line[6:11],2)] + int(line[16:32],2) - 8192)/4)
        memList[offset] = r[int(line[11:16],2)]
        file.write("Instruction "+repr(count)+": sw - 4 cycles \n")
        multi_4 += 1
        pc = pc + 1  
    else:
        print("Unknown instruction:"+ line)
        break;
    count = count + 1


print("PC:                   " +repr(pc * 4))
print("Registers 0-7:        " + repr(r))
print("DIC count:            {}".format(count))

print("\nMulticycle CPU Information ")
print("Total number of cycles:         " + repr(multi_cycles))
print("Number of 3 cycle instructions: " + repr(multi_3))
print("Number of 4 cycle instructions: " + repr(multi_4))
print("Number of 5 cycle instructions: " + repr(multi_5))
file.write("\n" + "Total cycles in Multicycle: " + repr(multi_cycles))

print("\nPipelined CPU Information ")
print("Number of hazards: " + repr(hazard_c))
print("Total number of cycles: " + repr(count + 4 + hazard_c))

file.close()