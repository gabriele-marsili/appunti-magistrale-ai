S = [
    "aaa",
    "aab",
    "aba",
    "abb",
    "bba",    
]

def map_char(char):
    if char == "a" : 
        return 2
    if char == "b" : 
        return 3

    raise Exception(f"Invalid char {char}")


def h_1(s):
    if len(s) != 3:
        raise Exception (f"Invalid len h1 -> s: {s}")
    
    return (map_char(s[0]) + 2*map_char(s[1]) + map_char(s[2])) % 11

def h_2(s):
    if len(s) != 3:
        raise Exception (f"Invalid len h2 -> s: {s}")
    
    return ((map_char(s[0]) + map_char(s[1]))*2 + map_char(s[2])) % 11

        
        
for s in S:
    print(f"{s} -> h1: {h_1(s)} ;  h2: {h_2(s)}")