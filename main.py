import os, sys
from stat import *
import time
import json
import os.path
import numpy as np
import pandas as pd
from network import *
import re

imports = []
endpoints = []
versions = []

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

    # hard coded endpoint
    for line in file:
        if re.findall(r'(?:\d{1,3}\.)+(?:\d{1,3})', line):
            reg = re.findall(r'(?:\d{1,3}\.)+(?:\d{1,3})', line)
            for item in reg:
                if len(item.split(".")) == 4:
                    endpoints.append([filename[filename.rfind("/")+1:],item])
                elif len(item.split(".")) == 3:
                    versions.append([filename[filename.rfind("/")+1:],item])

        #if "class" in line.split(" ") and "(" in line:
        #    print(line)
        #    #matchObj = re.match( r'(.*) class (.*?) .*', line, re.M|re.I)
        #    obj = line[line.index("class")+6:line.index("(")]
        #    #result.append([filename[filename.rfind("/")+1:],matchObj.group(2)])
        #    result.append([filename[filename.rfind("/")+1:],obj])
        if line.split(" ")[0] == "import":
            import_name = [filename[filename.rfind("/")+1:],line.split(" ")[1].replace(";","").replace('\n','')]
            imports.append(import_name)

def visitfile(file,file_type,dir):
    if not file.startswith('.'):
        if file.endswith(file_type):
            return parsefile(file)	

if __name__ == '__main__':
    walktree(sys.argv[1], visitfile, 'py')
    print("ENDPOINTS")
    for endpoint in endpoints:
        print(endpoint)
    print("VERSIONS")
    for version in versions:
        print(version)
    print("IMPORTS")
    for import in imports:
        print(import)
    #df = pd.DataFrame(data=result, columns=['file_name','import_name'])
    #build_network(df, "file_name", "import_name")
