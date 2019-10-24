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
classes = []
class_calls = []

def walktree(top, callback, file_type, pre_pro):
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file'''

    for f in os.listdir(top):
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[ST_MODE]
        if S_ISDIR(mode):
            # It's a directory, recurse into it
            walktree(pathname, callback, file_type, pre_pro)
        elif S_ISREG(mode):
            # It's a file, call the callback function
            callback(pathname,file_type,pathname.replace(f,""), pre_pro)
            #if output: result.append(output)
        else:
            # Unknown file type, print a message
            print('Skipping %s' % pathname)
#    print([x for x in imports if x != []])
    

def parsefile(filename, pre_pro):
    file = open(filename, 'r')

    for line in file:
        if re.findall(r'(?:\d{1,3}\.)+(?:\d{1,3})', line):
            reg = re.findall(r'(?:\d{1,3}\.)+(?:\d{1,3})', line)
            for item in reg:
                # ENDPOINTS
                if len(item.split(".")) == 4:
                    endpoints.append([filename[filename.rfind("/")+1:],item])
                # VERSION
                elif len(item.split(".")) == 3:
                    versions.append([filename[filename.rfind("/")+1:],item])

        # CLASS
        if line.split(" ")[0] == "class" and pre_pro:
            class_name = line.split(" ")[1][:line.lstrip().split(" ")[1].index("(")]
            #classes.append([filename[filename.rfind("/")+1:],class_name])
            classes.append(class_name)
        if not pre_pro:
            if all(item in classes for item in line.replace("("," ").replace(")"," ").split(" ")):
                print(classes)
                print(line)
                input()
                classes_calls.append([filename[filename.rfind("/")+1:],class_name])


        # IMPORTS
        if line.split(" ")[0] == "import":
            import_name = [filename[filename.rfind("/")+1:],line.split(" ")[1].replace(";","").replace('\n','')]
            imports.append(import_name)

def visitfile(file,file_type,dir, pre_pro):
    if not file.startswith('.'):
        if file.endswith(file_type):
            return parsefile(file, pre_pro)	

if __name__ == '__main__':
    walktree(sys.argv[1], visitfile, 'py', True)
    print(classes)
    input()
    walktree(sys.argv[1], visitfile, 'py', False)
    print("ENDPOINTS")
    for endpoint in endpoints:
        print(endpoint)
    print("VERSIONS")
    for version in versions:
        print(version)
    #print("IMPORTS")
    #for importi in imports:
    #    print(importi)
    df = pd.DataFrame(data=imports, columns=['file_name','import_name'])
    build_network(df, "file_name", "import_name")
