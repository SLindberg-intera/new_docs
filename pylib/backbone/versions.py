EXPONENT = 2
DEPTH_LEVEL = 3 # major, minor, sub, etc...
SEP = "."

def strip_prefix(in_str):
    return in_str.strip("v")

def strip_alpha(in_str):
    x = in_str[-1]
    try:
        return int(in_str)
    except ValueError:
        if len(in_str)>1:
            return int(in_str[0:-1])*10+ord(x)
        return ord(x)

def convert_alpha(in_char):
    try:
        return int(in_char)
    except ValueError:
        return ord(in_char)

def parse_version_str(in_str, depth_level=DEPTH_LEVEL, sep=SEP):
    s = strip_prefix(in_str)
    try:
        return int(s)*10**(depth_level+2)
    except ValueError as e:
         if sep in s:
             v = s.split(sep)
             if(len(v)>depth_level):
                 raise ValueError(
                         "Too many levels of versions- Only recognizes {} levels; i.e. {}".format(
                 DEPTH_LEVEL, SEP.join(["10" for i in range(DEPTH_LEVEL)])
                 ))
            
             v = list(map(strip_alpha, v))
             l = depth_level+2
             v = [i*10**(l - ix*EXPONENT) for ix, i in enumerate(v)]
             return sum(v)
         raise e


