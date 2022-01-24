import os

function = None

types = {
    'pl': '<Type type="Player"/>',
    'tbl': '<Type type="Table"/>',
    'num': '<Type type="Number"/>',
    'str': '<Type type="String"/>',
    'vec': '<Type type="Vector"/>',
    'ent': '<Type type="Entity"/>',
    'bool': '<Type type="boolean">',
    'func': '<Type type="function">',
    'any': '<Type type="Any>',
    'tr': '<Type type="Trace">',
}

global_index = {}

class Func:
    def __init__( self, line ):
        self.line = line
        self.con_func = False
        self.name = ""
        self.args = []

    def is_func( self ):
        if self.line.split() == []: return
        if self.line.split()[0] == "\t": return
        if "local function" in self.line: return

        if "..." in self.line: return
 
        return self.line.split()[0] == "function"
    
    def is_hook( self ):
        if self.line.split() == []: return

        if "return" in self.line: return

        if not "(" in self.line: return

        if "..." in self.line: return

        return "hook.Run" in self.line

    def get_arg( self, i ):
        if "pl" in i:
            return f"{types['pl']} {i}" 
        elif "tbl" in i:
            return f"{types['tbl']} {i}"
        elif "id" in i or "bone" in i:
            return f"{types['num']} {i}"
        elif "path" in i:
            return f"{types['str']} {i}"
        elif "url" in i:
            return f"{types['str']} {i}"
        elif "dir" in i:
            return f"{types['str']} {i}"
        elif "tag" in i:
            return f"{types['str']} {i}"
        elif "info" in i:
            return f"{types['str']} {i}"
        elif "folder" in i:
            return f"{types['str']} {i}"
        elif "data" in i:
            return f"{types['str']} {i}"
        elif "pos" in i:
            return f"{types['vec']} {i}"
        elif "target" in i:
            return f"{types['vec']} {i}"
        elif "dec" in i:
            return f"{types['vec']} {i}"
        elif "frac" in i:
            return f"{types['vec']} {i}"
        elif "isLoad" in i:
            return f"{types['bool']} {i}"
        elif "func" in i:
            return f"{types['func']} {i}"
        elif "callback" in i:
            return f"{types['func']} {i}"
        elif "ent" in i:
            return f"{types['ent']} {i}"
        elif "tr" in i:
            return f"{types['tr']} {i}"
        else:
            return f"{types['num']} {i}"

    def get_func( self ):
        if self.line.split() == []: return

        out = {}
        
        function = self.line.split(' ')

        function = " ".join(function[1:])
        
        name = function.split( "(" )[0]
        
        namefunc = ""

        folder = ""

        filename = ""

        if ":" in name:
            folder = name.split( ':' )[0]
            namefunc = name.split( ':' )[1]
        elif "." in name:
            folder = name.split( '.' )[0]
            namefunc = name.split( '.' )[1]
        else:
            namefunc = name
            filename = name

        if folder == "PLib":
            folder = "sh"
        elif folder == "":
            folder = "Global"
        
        if not folder in global_index.keys():
            global_index[folder] = 0
        else:
            global_index[folder] += 1
        
        filename = f"{global_index[folder]}-{namefunc}"

        args = []

        for i in function.split( "(" )[1][:-1][:-1].split(", "):
            if (i == ""): continue
            args.append( self.get_arg( str(i) ) )

        return ( name, args, folder, namefunc, filename )
    
    def get_hook( self ):
        line = ""

        if "=" in self.line:
            line = self.line.replace(" ", "").split("=")[1]
            line = line.strip('\n\t')
        else:
            line = self.line.replace(" ", "")
            line = line.strip('\n\t')

        name = line.split('"')[1]
        
        namefunc = ""

        folder = ""

        filename = ""
        
        if ":" in name:
            folder = name.split( ':' )[0]
            namefunc = name.split( ':' )[1]
        elif "." in name:
            folder = name.split( '.' )[0]
            namefunc = name.split( '.' )[1]
        else:
            namefunc = name
            filename = name

        args = []

        if folder == "PLib":
            folder = "sh"
        elif folder == "":
            folder = "GM"
        
        if not folder in global_index.keys():
            global_index[folder] = 0
        else:
            global_index[folder] += 1

        filename = f"{global_index[folder]}-{namefunc}"

        # hook.Run("PLib:PlayerInitialized", ply)

        for i in line.split('"')[2][1:-1].split(','):
            if i == "": continue
            args.append( self.get_arg(i) )

        return ( name, args, folder, namefunc, filename )

def create_doc( function ):
    text = ""

    argument = ""
    
    for i in function[1]:
        argument += i + ', '

    argument = argument[:-2]

    if function[ 1 ] == []:
        arguments = ""
    else:
        arguments = "## Arguments\n"

    for i in range( len( function[ 1 ] ) ):
        arguments += f"{i + 1}. {function[1][i]}" + "\n"

    import_str = "import { Function, Realm, Type } from '../../../src/components/Function'"
    
    realm = "realm={Realm.Client | Realm.Server}"


    doc = f"""---
title: {function[0]}
sidebar_label: {function[3]}
---

{import_str}

<Function {realm}>
    {function[0]}({argument})
</Function>

{arguments}
"""
    if os.path.isdir(f"doc/{function[2]}"):
        f = open( f'doc/{function[2]}/{ function[4] }.mdx', 'w' )
        f.write( doc )
        f.close()
    else:
        
        path = 'doc'
        path = os.path.join(path, function[2])
        
        os.makedirs(path)
        f = open( f'doc/{function[2]}/{ function[4] }.mdx', 'w' )
        f.write( doc )
        f.close()

def read_file(_file):    
    for line in _file:
        func = Func( line )
        
        if func.is_func():
            function = func.get_func()
            create_doc( function )
        if func.is_hook():
            function = func.get_hook()
            create_doc( function )


def append_list( list_1, list_2 ):
    for _object in list_2:
        list_1.append( _object )
    
    return list_1

def search_files(path):
    out = []
    files = os.listdir(path)

    for _file in files:
        path_file = f"{path}/{_file}"
        if os.path.isdir( path_file ): 
            files_dir = search_files( path_file )
            out = append_list(out, files_dir)
        else:
            out.append( path_file )
    
    return tuple(out)

def main(): 
    path = "plib"

    files = search_files( path )

    for _file in files:
        with open( _file, 'r', encoding='utf-8' ) as f:
            data = f.readlines()
        
        read_file( data )

        f.close()

if __name__ == '__main__':
    main()