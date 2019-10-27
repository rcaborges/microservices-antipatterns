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
methods = []
method_calls = []

forb_words = ['labels','run','name','delete','build','now','set','bom','service','options',
              'main','fetch','value','error','write','read','filename','execute','passed',
              'calls','git','new','next','registry','family','smc','origin','factory','ObjectType'
              'load','failed','issues','data','deploy','repos','get','count','git_dir','metrics'
              'compare','upstream','gradle']

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

#        # FUNCTION CALL
#        if re.findall(r'[a-zA-Z]+\([^\)]*\)(\.[^\)]*\))?', line):
#            print(line)
#            print(re.findall(r'(?:\d{1,3}\.)+(?:\d{1,3})', line))
#            input()

#        # METHODS
#        if line.lstrip().split(" ")[0] == "def" and pre_pro:
#            method_name = line.lstrip().split(" ")[1][:line.lstrip().split(" ")[1].index("(")]
#            #classes.append([filename[filename.rfind("/")+1:],class_name])
#            methods.append(method_name)
#        if line.lstrip().split(" ")[0] != "def" and not pre_pro and "(" in line:
#            if [e for e in methods if e in line.replace("("," ").replace(")"," ").replace("["," ").split(" ")]:
#                intersect = [e for e in methods if e in line.replace("("," ").replace(")"," ").replace("["," ").split(" ")]
#                method_calls.append([filename[filename.rfind("/")+1:],intersect[0]])

        # CLASS
        if line.split(" ")[0] == "class" and pre_pro:
            class_name = line.split(" ")[1][:line.lstrip().split(" ")[1].index("(")]
            #classes.append([filename[filename.rfind("/")+1:],class_name])
            classes.append(class_name)
        if line.lstrip().split(" ")[0] != "class" and not pre_pro and "(" in line:
            if [e for e in classes if e in line.replace("("," ").replace(")"," ").replace("["," ").split(" ")]:
                intersect = [e for e in classes if e in line.replace("("," ").replace(")"," ").replace("["," ").split(" ")]
                class_calls.append([filename[filename.rfind("/")+1:],intersect[0]])


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

    methods = list(set(methods))
    methods = [x for x in methods if x not in forb_words]

    classes = list(set(classes))
    print(len(classes))
    classes = [x for x in classes if x not in forb_words]
    print(len(classes))

    walktree(sys.argv[1], visitfile, 'py', False)
    
    print("ENDPOINTS")
    for endpoint in endpoints:
        print(endpoint)
#    print("VERSIONS")
#    for version in versions:
#        print(version)
#    print("IMPORTS")
#    for importi in imports:
#        print(importi)

    df = pd.DataFrame(data=class_calls, columns=['file_name','class_name'])
    build_network(df, "file_name", "class_name")
