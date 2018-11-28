def twos_convert(line):
   if (line[16] == '1'):
           return (-1*(0b1111111111111111 - int(line[16:32], 2) + 1))
   else:
           return int(line[16:32], 2)
  
input_file = open("i_mem.txt", "r")
m_file = open("MulticycleInfo.txt","w")
p_file = open("PipelineInfo.txt","w")
c_file = open("CacheInfo.txt", "w")
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

# Cache variables
dm2 = [0, 0, 0, 0], [0, 0, 0, 0]
dm4 = [0, 0], [0, 0], [0, 0], [0, 0]
fa4 = [0, 0], [0, 0], [0, 0], [0, 0]
fa8 = [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]
dm2blkindex = 0
dm2validbit = 0
dm2tag = 0

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
       c_file.write("\nAccessing memory address: " + repr(hex(offset * 4 + 0x2000)))
       dm2blkindex = offset * 4 + 0x2000
       c_file.write("\nBlock Index: " + repr(format(dm2blkindex, '#018b')[13:14]))
       c_file.write("\nTag: " + repr(format(dm2blkindex, '#018b')[2:13]))

       m_file.write("Instruction " +repr(count)+ ": lw - 5 cycles \n")
       pc = pc + 1
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


