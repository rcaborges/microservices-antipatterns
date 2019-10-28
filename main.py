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
single_methods = []
single_method_calls = []
class_methods = []
class_method_calls = []
curr_class = ""

#forb_words = ['labels','run','name','delete','build','now','set','bom','service','options',
#              'main','fetch','value','error','write','read','filename','execute','passed',
#              'calls','git','new','next','registry','family','smc','origin','factory','ObjectType'
#              'load','failed','issues','data','deploy','repos','get','count','git_dir','metrics'
#              'compare','upstream','gradle']

forb_words = ['run','name','delete','build','now','set','service']

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

        if re.findall(r'(?:\d{1,3}\.)+(?:\d{1,3})', line) and not pre_pro:
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
            classes.append(class_name)
            #curr_class = class_name
        # CLASS OCCURRENCE
        if line.lstrip().split(" ")[0] != "class" and not pre_pro and "(" in line:
            if [e for e in classes if e in line.replace("("," ").replace(")"," ").replace("["," ").split(" ")]:
                intersect = [e for e in classes if e in line.replace("("," ").replace(")"," ").replace("["," ").split(" ")]
                for entry in intersect:
                    class_calls.append({"file_name": filename[filename.rfind("/")+1:], "class_name": entry})

        # SINGLE METHODS
        if line.split(" ")[0] == "def" and pre_pro and re.findall(r'[a-zA-Z]+\([^\)]*\)(\.[^\)]*\))?', line):
            method_name = line.lstrip().split(" ")[1][:line.lstrip().split(" ")[1].index("(")]
            single_methods.append(method_name)
        # CLASS METHODS
        elif "def" in line.split(" ")  and pre_pro and re.findall(r'[a-zA-Z]+\([^\)]*\)(\.[^\)]*\))?', line):
            method_name = line.lstrip().split(" ")[1][:line.lstrip().split(" ")[1].index("(")]
            class_methods.append(method_name)

        # SINGLE METHODS OCCURRENCE
        if line.lstrip().split(" ")[0] != "def" and not pre_pro and "(" in line and re.findall(r'[a-zA-Z]+\([^\)]*\)(\.[^\)]*\))?', line):
            if [e for e in single_methods if e in line.replace("("," ").replace(")"," ").replace("["," ").split(" ")]:
                intersect = [e for e in single_methods if e in line.replace("("," ").replace(")"," ").replace("["," ").split(" ")]
                for entry in intersect:
                    single_method_calls.append({"file_name" : filename[filename.rfind("/")+1:], "method_name": entry})

        # IMPORTS
        if line.split(" ")[0] == "import" and not pre_pro:
            import_name = line.split(" ")[1].replace(";","").replace('\n','')
            imports.append({"file_name":filename[filename.rfind("/")+1:],"import_name": import_name})

def visitfile(file,file_type,dir, pre_pro):
    if not file.startswith('.'):
        if file.endswith(file_type):
            return parsefile(file, pre_pro)	

if __name__ == '__main__':

    # filling class and method names 
    walktree(sys.argv[1], visitfile, 'py', True)

    # removing elected forbidden terms
    smethods = list(set(single_methods))
    print(len(smethods))
    filt_smethods = [x for x in smethods if x not in forb_words]
    print(len(filt_smethods))
    print(list(set(smethods)-set(filt_smethods)))

    # removing elected forbidden terms
    classes = list(set(classes))
    print(len(classes))
    filt_classes = [x for x in classes if x not in forb_words]
    print(len(classes))
    print(list(set(classes)-set(filt_classes)))

    # filling methods and classes calls
    walktree(sys.argv[1], visitfile, 'py', False)
    
    print("ENDPOINTS")
    print(len(endpoints))
    print("VERSIONS")
    print(len(versions))

    df_class = pd.DataFrame(data=class_calls)
    df_smethod = pd.DataFrame(data=single_method_calls)
    df_import = pd.DataFrame(data=imports)

    #TODO
    # check methods and classes with big names
    # check services that have repeated entries in the df
    # associate each class_method to its class, and check a general profile for classes

    print("IMPORTS")
    print(len(set(df_import['import_name'].values)))

    #build_network(df, "file_name", "class_name")
