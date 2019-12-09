#!/usr/bin/env -S python3 -u

# /dev/random is a random number generator. It works by watching user input and hardware drive access.
# It records the milliseconds and nanoseconds when such activities occurs and mixes the timestamps in 
# an entropy pool. By mixing low entropy numbers the entropy of the overall pool increases.
# When user askes for random number it performs a SHA-1 hash and returns the result.
# /dev/random will block because it takes some time to increase entropy. /dev/random maintains 
# an entropy pool of a maximum of 4096 bits.

# For the purpose of this exercise the entropy pool will use the milliseconds it takes the system to 
# ping google.com. 
# The program starts with a pool of 0 entropy. Every time 'get_entropy' is run 5 binary values of 
# the delay it takes to ping google.com are concatenated and XOR'd with the existing entropy 
# left-shifted by 32. Pool increases by ~32 bits everytime, unless it has less than 512 bits.
# When a sequence of bits is removed from the pool, the pool shrinks by the same number of bits.

# Usage:

# python -u random.py will have a similar output as '> cat /dev/random'
# May need to hit CTRL-C multiple times to kill. Use the -u option otherwise may take a while
# to flush buffer

# If running in a python shell directly use 'random()' function instead.
# It will return ascii string value representation of the hash.


import subprocess as subp
import sys
import hashlib
import time

CMD = "ping -c 1 google.com | tail +2 | sed '2,$d' | cut -d '=' -f 4 | cut -d ' ' -f 1"
MAX_ENTROPY = 4096
MIN_ENTROPY = 512
entropy = 0

# binary string representation of an int.
get_bin = lambda x: format(x, 'b')

# Function to increase the entropy pool.
def get_entropy(entropy):
    output = ''
    if entropy_available() >= MAX_ENTROPY:
        return(entropy)

    for i in range(0,5):
        # send command to stdout
        ps = subp.Popen(CMD, shell=True, stdout=subp.PIPE, stderr=subp.STDOUT)
        try:
            # read command result
            # milli-second value represented as a float. 
            # multiplied by 10 to get whole value and cast to int.
            output += get_bin(int(float(ps.communicate()[0]) * 10))
        except ValueError: 
            pass
    entropy = (entropy << 32 ) ^ int(output,2) # add new bits to pool.

    if(len(get_bin(entropy)) < MIN_ENTROPY):
        entropy = get_entropy(entropy)

    return(entropy)

# Print available entropy. Useful when running in Python Shell.          
def entropy_available():
    return len(get_bin(entropy))

def hash_sequence(random_sequence):
    hash = hashlib.sha1(str(random_sequence).encode())
    return(hash.digest())

# Get random sequence of length num_bits from entropy pool.
def get_random_sequence(num_bits = None):
    global entropy
    
    if num_bits:
        while(entropy_available() < num_bits): # check if enough entropy
            entropy = get_entropy(entropy)
        random_sequence = entropy & ((1 << num_bits) - 1)
        entropy = entropy >> num_bits
    else: #if num_bits not specified, entire pool is emptied.
        entropy = get_entropy(entropy)
        random_sequence = entropy
        entropy = 0
    return(random_sequence)

#return SHA-1 of a random sequence of desired bits. 
#returned value will have 160-bit size
def random(num_bits = None):
    random_sequence = get_random_sequence(num_bits)
    return(hash_sequence(random_sequence))
    
# run random infinite times
def random_inf():
    while(True):
        # Prints binary SHA-1 hash of a random 160-bit sequence
        sys.stdout.buffer.write(random(160)) 
        time.sleep(.5) #Added to allow for ^C to exit program. May require spamming.

if __name__ == "__main__":
    random_inf()