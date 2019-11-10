"""
    this is a batch processor

"""
import os, sys
import fingerprint
import argparse

def getArgs():
    parser = argparse.ArgumentParser(
            description=("Process a collection of files "
                "and folders by invoking the fingerprinter on each one."
                "This creates one fingerprint file for each item in"
                " the input file and stores the results "
                "in the target directory"
                )
    )
    
    parser.add_argument(
            "inputfile", type=str,
            help=("Path to a file containing the "
                "items that you would like to process.  "
                "Each line should contain at least a path, and "
                "optionally a filename. "
                "Blank lines or those starting with a '#' are ignored."
                " The path specifies the "
                "path to a file or folder to fingerprint.  "
                "The optional filename specifies the name of "
                "the fingerprint file that is generated for the "
                "specified path.")
            )
    parser.add_argument(
            "--outdir", type=str,
            default=".",
            help=("Path to the folder where you want to store the output.  "
                "The defaults to the current directory.")
            )
    parser.add_argument(
            "--sep", 
            type=str,
            default=",",
            help=("The type of character that separates columns "
                "in the input file.  Defaults to a comma; ','.  "
                "Specify a tab or space as 's' ")
            )
    return parser

def parse_file(inputfile, sep):
    """ read the file and extract the things to fingerprint"""
    def split(line, sep):
        if sep=="s":
            return line.split()
        return line.split(sep)

    def itr_lines(lines):
        for line in lines:
            pline = line.strip()
            if pline.startswith("#"):
                continue
            if pline == "":
                continue
            yield split(pline, sep)

    with open(inputfile, 'r') as f:
        lines = f.readlines()
        return list(itr_lines(lines))

def parse_filename(filename):
    """ grab the base part of the path
    
    example returns 'name' for these cases:
     my\\crazy\\path\\name.expy  (Case 1)
     my\\crazy\\path\\name   (case 2) 
     my\\crazy\\path\\name\\  (case 3)

    """
    b = os.path.basename(filename)
    if b != '':
        return os.path.splitext(b)[0] # case 1
    dirbase = b.split()[1] 
    if dirbase == "":
        return b.split()[0]  # case 3
    return dirbase # case 2 

def make_fingerprint_name(fingerprint_path, rename=None):
    """ create the name of the fingerprint file 
    
        if rename, renames it first; else it uses the filename
        in fingerprint_path
    """
    name = parse_filename(fingerprint_path)
    str_template = "fingerprint-{}.txt"
    if rename is None:
        return str_template.format(name)
    return str_template.format(rename)

def apply_fingerprint(fingerprint_path, output_path):
    """ make the fingerprint and write it to file"""
    s = fingerprint.extract_fingerprints(fingerprint_path)
    fingerprint.to_file(output_path, s)

def make_handprint(input_path, output_path, sep):
    inputs = parse_file(input_path, sep)
    for fingerpath, *rename in inputs:
        name = make_fingerprint_name(fingerpath, *rename)
        apply_fingerprint(
                fingerpath,
                os.path.join(output_path, name))

if __name__=="__main__":
    parser = getArgs()
    args = parser.parse_args()
    make_handprint(args.inputfile, args.outdir, args.sep)
