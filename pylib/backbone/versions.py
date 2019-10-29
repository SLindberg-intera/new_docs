EXPONENT = 3
DEPTH_LEVEL = 3 # major, minor, sub, etc...
SEP = "."
PREFIX = 'v'

def strip_prefix(in_str, prefix):
    return in_str.strip(prefix)

def strip_alpha(in_str):
    x = in_str[-1]
    try:
        return int(in_str)
    except ValueError:
        if len(in_str)>1:
            return int(in_str[0:-1])+ord(x)/(10**EXPONENT)
        return ord(x)/(10**EXPONENT)

def parse_version_str(in_str, depth_level=DEPTH_LEVEL, 
        sep=SEP, prefix=PREFIX):
    s = strip_prefix(in_str, prefix)
    v = s.split(sep)
    if(len(v)>depth_level):
        raise ValueError(
                 "Too many levels of "
                 "versions- Only"
                 " recognizes {} levels; i.e. {}".format(
         DEPTH_LEVEL, SEP.join(["10" for i in range(DEPTH_LEVEL)])
         )
        )
    v = list(map(strip_alpha, v))
    l = depth_level
    v = [i*10**((l - ix)*EXPONENT) for ix, i in enumerate(v)]
    return int(sum(v))


