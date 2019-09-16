import os, sys
from stat import *
import time
import json
import os.path
import numpy as np
import pandas as pd

result = []

def walktree(top, callback, file_type):
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file'''

    for f in os.listdir(top):
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[ST_MODE]
        if S_ISDIR(mode):
            # It's a directory, recurse into it
            walktree(pathname, callback, file_type)
        elif S_ISREG(mode):
            # It's a file, call the callback function
            output = callback(pathname,file_type,pathname.replace(f,""))
            if output: result.append(output)
        else:
            # Unknown file type, print a message
            print('Skipping %s' % pathname)
#    print([x for x in imports if x != []])
    

def parsefile(filename):
    file = open(filename, 'r') 
    for line in file:
        if line.split(" ")[0] == "import":
            import_name = [filename[filename.rfind("/")+1:],line.split(" ")[1].replace(";","").replace('\n','')]
            result.append(import_name)

def visitfile(file,file_type,dir):
    if not file.startswith('.'):
        if file.endswith(file_type):
            return parsefile(file)	

if __name__ == '__main__':
    walktree(sys.argv[1], visitfile, 'java')
    print(pd.DataFrame(data=result, columns=['file_name','import_name']))
