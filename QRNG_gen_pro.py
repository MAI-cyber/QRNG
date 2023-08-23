# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 12:26:41 2023

@author: mai
"""

from serial import *
from time import sleep
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as wgt
import os

def FindHeader(s):
    # Connecting with the FPGA
    for i in range(1000):
        try_head = s.read(1)
        if try_head[0] == 47:
            print("Header found, ready to proceed.")
            sleep(1)
            return True
    print("Header not found. Exiting.")
    return False

def GetCounts(s, length = 1000):
    # Recieveing data of size (set to 40 million) form the FPGA
    
    data = s.read(10)
    temp= []
           
    text_file = open("bin_string.txt", "wt")
    counter = 0
    
    while len(temp) <length:
        
        # When the counter reaches 400, data collection will stop
        if counter % 100000 == 0:
            print(counter/100000)
        
        # The FPGA sends 10 data points for single counts and coincidences
        data = s.read(10) 
        
        # Taking the data from the designated detector and doing parity checks
        if data[0] % 2:
            temp.append(1)
        else:
            temp.append(0)
            
        counter += 1
            
            
    return np.array(temp)



def Saving_data(name, temp):
    # POst processing and saving the data
    
    print("Saving data for " + name)
    
    text_file = open(name + ".txt", "wt")
  

    # dealing with the bias
    if len(temp) % 2 == 1:
        temp.pop()
        

    for i in range(len(temp)):
        
        
        if i % 2: # If index is even
            continue
        
        if temp[i] == temp[i+1]: # If the pair have the same digit
            continue
        if temp[i] > 0.5:        # If for different digits, the first digit is 1
            text_file.write('1') 
        else:                    # If for different digits, the first digit is 0
            text_file.write('0') 
    text_file.close()
    


# Define the size of data to be collected 
size = 4*1000*10

temp = np.zeros(int(size*1000))
    
    # Connecting wiht the FPGA
s = Serial("COM5", 4000000)
s.set_buffer_size(10000000)
for i in range(1):
    FindHeader(s)
    temp = GetCounts(s, 1000*size)
    print(i, s.inWaiting())
    s.flushInput()
    
print(temp.shape)
print("Data =", temp)

# Rough appoximate of biase in data
print("Ones = ", sum(temp))

# Disconnecting the FPGA
s.close()

# Ensuring that binary digits can be paired
if len(temp) % 2 == 1:
    temp.pop()

file = ["QRNG_"+ str(i) for i in range(0,11)]

set_size = int(len(temp)/10)

for i in range(10):
    Saving_data(file[i],  temp[i*set_size: (i+1)*set_size ])


