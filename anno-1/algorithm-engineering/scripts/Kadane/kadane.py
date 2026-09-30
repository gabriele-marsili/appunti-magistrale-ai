from math import inf
sequence = [4,-6,3,1,3,-2,3,-4,1,-9,6]

def kadane(seq):
    max_sum = -inf
    temp_sum = 0
    b = 0
    b0 = 0
    s0 = 0

    for s in range(0,len(seq)):
        temp_sum += seq[s]

        if max_sum < temp_sum: 
            max_sum = temp_sum 
            b0 = b
            s0 = s

        if temp_sum < 0:
            temp_sum = 0
            b += s+1

    return [max_sum, b0, s0]


res = kadane(sequence)
print(f"Res for seq {sequence}:\n\nMax sum {res[0]} -> from {res[1]} to {res[2]}")