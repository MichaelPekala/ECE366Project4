def twos_convert(line):
   if (line[16] == '1'):
           return (-1*(0b1111111111111111 - int(line[16:32], 2) + 1))
   else:
           return int(line[16:32], 2)

input_file = open("i_mem.txt", "r")
m_file = open("MulticycleInfo.txt","w")
p_file = open("PipelineInfo.txt","w")
c_file = open("DM4Cache.txt", "w")
dm4_file = open("DM2Cache.txt", "w")
fa_file = open("FACache.txt", "w")
sa_file = open("SACache.txt", "w")
print("Supported instructions: add, sub, xor, addi, beq, bne, slt, lw, sw\n")
instList = []
multi_cycles = 0
multi_3 = 0
multi_4 = 0
multi_5 = 0
count = 0
hazard = [-1,-1]    # initialized to -1, -1 to represent null registers in the beginning of program execution
lw_detector = False
hazard_c = 0
delay = 0

mem_size = 1024
memList = [0 for i in range(mem_size)]
r = [0,0,0,0,0,0,0,0]
pc = 0

# Cache variables
i = 0
j = 0
address = [0 for i in range(mem_size)]
dm2blkindex = [-3 for i in range(mem_size)]
dm2blkindex[-1] = -3
dm2validbit = 0
dm2tag = [-3 for i in range(mem_size)]
dm2hit = 0
dm2miss = 0

address = [0 for i in range(mem_size)]
dm4blkindex = [-3 for i in range(mem_size)]
dm4blkindex[-1] = -3
dm4validbit = 0
dm4tag = [-3 for i in range(mem_size)]
dm4hit = 0
dm4miss = 0

address = [0 for i in range(mem_size)]
fablkindex = [-3 for i in range(mem_size)]
fablkindex[-1] = -3
favalidbit = 0
fatag = [-3 for i in range(mem_size)]
fahit = 0
famiss = 0

address = [0 for i in range(mem_size)]
sablkindex = [-3 for i in range(mem_size)]
sablkindex[-1] = -3
savalidbit = 0
satag = [-3 for i in range(mem_size)]
sahit = 0
samiss = 0


for code in input_file:
   line = code.replace("\t", "")
   line = line.replace(" ","")     # remove spaces anywhere in line
   if (line == "\n"):              # empty lines ignored
       continue
   line = line.replace("\n","")
   line = format(int(line,16),"032b")
   instList.append(line)

input_file.close()

while(pc < len(instList)):
   line = instList[pc]
   #r-type
   if(line[0:6] == '000000'):
       multi_cycles += 4 #rtype have 4 cycles
       #add
       if(line[26:32] == '100000'):
           #rd = rs + rt
           if((hazard[1] is (int(line[6:11],2)) and lw_detector is True)):
             delay += 1
           lw_detector = False

           if ((hazard[0] is (int(line[6:11],2) or int(line[11:16],2))) or hazard[1] is (int(line[6:11],2) or int(line[11:16],2))):
             p_file.write("Instruction "+repr(count)+" hazard detected with add\n")

           r[int(line[16:21],2)] = r[int(line[6:11],2)] + r[int(line[11:16],2)]
           m_file.write("Instruction "+repr(count)+": add - 4 cycles \n")
           multi_4 += 1
           pc = pc + 1
           hazard.append(int(line[16:21],2))
           hazard.pop(0)

       #sub
       elif(line[26:32] == '100010'):
           #rd = rs - rt
           if((hazard[1] is (int(line[6:11],2)) and lw_detector is True)):
             delay += 1
           lw_detector = False

           if ((hazard[0] is (int(line[6:11],2) or int(line[11:16],2))) or hazard[1] is (int(line[6:11],2) or int(line[11:16],2))):
             p_file.write("Instruction "+repr(count)+" hazard detected with sub\n")
           r[int(line[16:21],2)] = r[int(line[6:11],2)] - r[int(line[11:16],2)]
           m_file.write("Instruction "+repr(count)+": sub - 4 cycles \n")
           multi_4 += 1
           pc = pc + 1
           hazard.append(int(line[16:21],2))
           hazard.pop(0)
       #xor
       elif(line[26:32] == '100110'):
           #rd = rs ^ rt
           if((hazard[1] is (int(line[6:11],2)) and lw_detector is True)):
             delay += 1
           lw_detector = False

           if ((hazard[0] is (int(line[6:11],2) or int(line[11:16],2))) or hazard[1] is (int(line[6:11],2) or int(line[11:16],2))):
             p_file.write("Instruction "+repr(count)+" hazard detected with xor\n")
           r[int(line[16:21],2)] = r[int(line[6:11],2)] ^ r[int(line[11:16],2)]
           m_file.write("Instruction "+repr(count)+": xor - 4 cycles \n")
           multi_4 += 1
           pc = pc + 1
           hazard.append(int(line[16:21],2))
           hazard.pop(0)
       #slt
       elif(line[26:32] == '101010'):
           #rd = 1 if(rs < rt)
           if((hazard[1] is (int(line[6:11],2)) and lw_detector is True)):
             delay += 1
           lw_detector = False

           if ((hazard[0] is (int(line[6:11],2) or int(line[11:16],2))) or hazard[1] is (int(line[6:11],2) or int(line[11:16],2))):
             p_file.write("Instruction "+repr(count)+" with slt\n")
           if (r[int(line[6:11],2)] < r[int(line[11:16],2)]):
             r[int(line[16:21],2)] = 1
           else:
             r[int(line[16:21],2)] = 0
           m_file.write("Instruction "+repr(count)+": slt - 4 cycles \n")
           multi_4 += 1
           pc = pc + 1
           hazard.append(int(line[16:21],2))
           hazard.pop(0)

   #addi
   elif(line[0:6] == '001000'):
       multi_cycles += 4
       #rt = rs + imm
       if((hazard[1] is (int(line[6:11],2)) and lw_detector is True)):
           delay += 1
       lw_detector = False

       if ((hazard[0] is int(line[6:11],2)) or (hazard[1] is (int(line[6:11],2)))):
             p_file.write("Instruction "+repr(count)+" hazard detected with addi\n")
       imm = twos_convert(line)
       r[int(line[11:16],2)] = r[int(line[6:11],2)] + imm
       m_file.write("Instruction "+repr(count)+": addi - 4 cycles \n")
       multi_4 += 1
       pc = pc + 1
       hazard.append(int(line[11:16],2))
       hazard.pop(0)
   #beq
   elif(line[0:6] == '000100'):
       multi_cycles += 3
       multi_3 += 1
       if ((hazard[0] is (int(line[6:11],2) or int(line[11:16],2))) or (hazard[1] is (int(line[6:11],2) or int(line[11:16],2)))):
             p_file.write("Instruction "+repr(count)+" hazard detected with beq\n")

       if((hazard[1] is (int(line[6:11],2))) and (lw_detector is True)):
           delay += 2
       if(hazard[1] is (int(line[6:11],2)) and (lw_detector is False)):
           delay += 1

       lw_detector = False
       #if(rs == rt) then pc = imm + pc
       temp_pc = pc
       imm = twos_convert(line)
       m_file.write("Instruction "+repr(count)+": beq - 3 cycles \n")
       if(r[int(line[6:11],2)] is r[int(line[11:16],2)]):
           pc = pc + imm + 1
           delay += 1
       else:
           pc = pc + 1
       if pc is temp_pc:
           count = count + 1
           delay -= 1
           break
       hazard.append(-1)
       hazard.pop(0)
   #bne
   elif(line[0:6] == '000101'):
       multi_cycles += 3
       multi_3 += 1
       if ((hazard[0] is (int(line[6:11],2) or int(line[11:16],2))) or hazard[1] is (int(line[6:11],2) or int(line[11:16],2))):
             p_file.write("Instruction "+repr(count)+" hazard detected with bne\n")

       if((hazard[1] is (int(line[6:11],2))) and (lw_detector is True)):
           delay += 2
       if(hazard[1] is (int(line[6:11],2)) and (lw_detector is False)):
           delay += 1
       lw_detector = False
       #if(rs != rt) then pc = imm + pc
       temp_pc = pc
       imm = twos_convert(line)
       m_file.write("Instruction "+repr(count)+": bne - 3 cycles \n")
       if(r[int(line[6:11],2)] != r[int(line[11:16],2)]):
           pc = pc + imm + 1
           delay += 1
           hazard_c += 1
       else:
           pc = pc + 1
       if pc is temp_pc:
           break
       hazard.append(-1)
       hazard.pop(0)
   #lw
   elif(line[0:6] == '100011'):
       multi_cycles += 5
       multi_5 += 1
       #rt = MEM[rs + imm]
        
       if((hazard[1] is (int(line[6:11],2)) and lw_detector is True)):
           delay += 1

       if ((hazard[0] is int(line[6:11],2)) or (hazard[1] is (int(line[6:11],2)))):
            p_file.write("Instruction "+repr(count)+" hazard detected with lw\n")
       offset = int((r[int(line[6:11],2)] + int(line[16:32],2) - 8192)/4)
       r[int(line[11:16],2)] = memList[offset]

       #cache behavior
       #DM Cache (4 blocks)
       j= i-1
       c_file.write("\nAccessing memory address using DM Cache (4 blocks): " + repr(hex(offset * 4 + 0x2000)))
       address[i] = offset * 4 + 0x2000
       dm2blkindex[i]  = int(format(address[i], '#018b')[13:14],2)
       dm2tag[i] = int(format(address[i], '#018b')[2:13],2)
       c_file.write("\n     Block " +repr(dm2blkindex[i])+ " is being accessed.")
       while (dm2blkindex[i] != dm2blkindex[j]):
           j-=1
           if j == -2:
               break
       if (dm2tag[i] == dm2tag[j]):
           dm2hit+=1
           c_file.write("\n     Hit!")
           c_file.write("\n     Valid bit for block " +repr(dm2blkindex[i])+ " has been updated to 0.")
           c_file.write("\n     No block has been updated.")
       else:
           dm2miss+=1
           c_file.write("\n     Miss!")
           c_file.write("\n     Valid bit for block " +repr(dm2blkindex[i])+ " has been updated to 1.")
           c_file.write("\n     Block " +repr(dm2blkindex[i])+ " has been updated.")
       c_file.write("\n     Block Index: " + repr(dm2blkindex[i]))
       c_file.write("\n     Tag: " + repr(dm2tag[i])+ "\n")

       #DM Cache (2 blocks)
       j= i-1
       dm4_file.write("\nAccessing memory address using DM Cache (2 blocks): " + repr(hex(offset * 4 + 0x2000)))
       address[i] = offset * 4 + 0x2000
       dm4blkindex[i]  = int(format(address[i], '#018b')[13:15],2)
       dm4tag[i] = int(format(address[i], '#018b')[2:13],2)
       dm4_file.write("\n     Block " +repr(dm4blkindex[i])+ " is being accessed.")
       while (dm4blkindex[i] != dm4blkindex[j]):
           j-=1
           if j == -2:
               break
       if (dm4tag[i] == dm4tag[j]):
           dm4hit+=1
           dm4_file.write("\n     Hit!")
           dm4_file.write("\n     Valid bit for block " +repr(dm4blkindex[i])+ " has been updated to 0.")
           dm4_file.write("\n     No block has been updated.")
       else:
           dm4miss+=1
           dm4_file.write("\n     Miss!")
           dm4_file.write("\n     Valid bit for block " +repr(dm4blkindex[i])+ " has been updated to 1.")
           dm4_file.write("\n     Block " +repr(dm4blkindex[i])+ " has been updated.")
       dm4_file.write("\n     Block Index: " + repr(dm4blkindex[i]))
       dm4_file.write("\n     Tag: " + repr(dm4tag[i])+ "\n")
       
       #FA Cache
       j= i-1
       fa_file.write("\nAccessing memory address using FA Cache: " + repr(hex(offset * 4 + 0x2000)))
       address[i] = offset * 4 + 0x2000
       fablkindex[i]  = int(format(address[i], '#018b')[13:15],2)
       fatag[i] = int(format(address[i], '#018b')[2:13],2)
       if (fatag[i] == fatag[j]):
           fahit+=1
           fa_file.write("\n     Hit!")
           fa_file.write("\n     Valid bit has been updated to 0.")
       else:
           famiss+=1
           fa_file.write("\n     Miss!")
           fa_file.write("\n     Valid bit has been updated to 1.")
       fa_file.write("\n     Tag: " + repr(fatag[i])+ "\n")
       
       #SA Cache
       j= i-1
       sa_file.write("\nAccessing memory address using SA Cache: " + repr(hex(offset * 4 + 0x2000)))
       address[i] = offset * 4 + 0x2000
       sablkindex[i]  = int(format(address[i], '#018b')[13:15],2)
       satag[i] = int(format(address[i], '#018b')[2:13],2)
       sa_file.write("\n     Block " +repr(sablkindex[i])+ " is being accessed.")
       while (sablkindex[i] != sablkindex[j]):
           j-=1
           if j == -2:
               break
       if (satag[i] == satag[j]):
           sahit+=1
           sa_file.write("\n     Hit!")
           sa_file.write("\n     Valid bit for block " +repr(sablkindex[i])+ " has been updated to 0.")
           sa_file.write("\n     No block has been updated.")
       else:
           samiss+=1
           sa_file.write("\n     Miss!")
           sa_file.write("\n     Valid bit for block " +repr(sablkindex[i])+ " has been updated to 1.")
           sa_file.write("\n     Block " +repr(sablkindex[i])+ " has been updated.")
       sa_file.write("\n     Block Index: " + repr(sablkindex[i]))
       sa_file.write("\n     Tag: " + repr(satag[i])+ "\n")
       
       m_file.write("Instruction " +repr(count)+ ": lw - 5 cycles \n")
       pc = pc + 1
       i+=1
       lw_detector = True
       hazard.append(int(line[11:16],2))
       hazard.pop(0)
   #sw
   elif(line[0:6] == '101011'):
       multi_cycles += 4
       if((hazard[1] is (int(line[6:11],2)) and lw_detector is True)):
           delay += 1
       lw_detector = False

       #MEM[rs + imm] = rt
       if ((hazard[0] is int(line[6:11],2)) or (hazard[1] is (int(line[6:11],2)))):
         p_file.write("Instruction "+repr(count)+" hazard detected with sw\n")
       offset = int((r[int(line[6:11],2)] + int(line[16:32],2) - 8192)/4)
       memList[offset] = r[int(line[11:16],2)]
       m_file.write("Instruction "+repr(count)+": sw - 4 cycles \n")
       multi_4 += 1
       pc = pc + 1
       hazard.append(-1)
       hazard.pop(0)
   else:
       print("Unknown instruction:"+ line)
       break;
   count = count + 1


c_file.write("\nTotal hits = " +repr(dm2hit))
c_file.write("\nTotal misses = " +repr(dm2miss))
c_file.write("\nHit rate = " +repr(dm2hit/(dm2hit+dm2miss)))

dm4_file.write("\nTotal hits = " +repr(dm4hit))
dm4_file.write("\nTotal misses = " +repr(dm4miss))
dm4_file.write("\nHit rate = " +repr(dm4hit/(dm4hit+dm4miss)))

fa_file.write("\nTotal hits = " +repr(fahit))
fa_file.write("\nTotal misses = " +repr(famiss))
fa_file.write("\nHit rate = " +repr(fahit/(fahit+famiss)))

sa_file.write("\nTotal hits = " +repr(sahit))
sa_file.write("\nTotal misses = " +repr(samiss))
sa_file.write("\nHit rate = " +repr(sahit/(sahit+samiss)))


print("PC:                   " +repr(pc * 4))
print("Registers 0-7:        " + repr(r))
print("DIC count:            {}".format(count))

print("\nMulticycle CPU Information ")
print("Total number of cycles:         " + repr(multi_cycles))
print("Number of 3 cycle instructions: " + repr(multi_3))
print("Number of 4 cycle instructions: " + repr(multi_4))
print("Number of 5 cycle instructions: " + repr(multi_5))
m_file.write("\n" + "Total cycles in Multicycle: " + repr(multi_cycles))

print("\nPipelined CPU Information ")
print("Number of delays: " + repr(delay))
print("Total number of cycles: " + repr(count + 4 + delay))
c_file.close()
p_file.close()
m_file.close()
dm4_file.close()
fa_file.close()
sa_file.close()
