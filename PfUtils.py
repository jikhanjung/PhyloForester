import sys, os, re
import copy

import numpy as np
#from stl import mesh
import tempfile

COMPANY_NAME = "PaleoBytes"
PROGRAM_NAME = "PhyloForester"
PROGRAM_VERSION = "0.0.1"

DB_LOCATION = ""

#print(os.name)
USER_PROFILE_DIRECTORY = os.path.expanduser('~')

DEFAULT_DB_DIRECTORY = os.path.join( USER_PROFILE_DIRECTORY, COMPANY_NAME, PROGRAM_NAME )
#DEFAULT_STORAGE_DIRECTORY = os.path.join(DEFAULT_DB_DIRECTORY, "data/")

if not os.path.exists(DEFAULT_DB_DIRECTORY):
    os.makedirs(DEFAULT_DB_DIRECTORY)
#if not os.path.exists(DEFAULT_STORAGE_DIRECTORY):
#    os.makedirs(DEFAULT_STORAGE_DIRECTORY)

def get_timestamp():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")

def value_to_bool(value):
    return value.lower() == 'true' if isinstance(value, str) else bool(value)

def get_unique_name(name, name_list):
    if name not in name_list:
        return name
    else:
        i = 1
        # get last index of current name which is in the form of "name (i)" using regular expression
        match = re.match(r"(.+)\s+\((\d+)\)",name)
        if match:
            name = match.group(1)
            i = int(match.group(2))
            i += 1
        while True:
            new_name = name + " ("+str(i)+")"
            if new_name not in name_list:
                return new_name
            i += 1

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def process_dropped_file_name(file_name):
    import os
    from urllib.parse import urlparse, unquote
    #print("file_name:", file_name)
    url = file_name
    parsed_url = urlparse(url)            
    #print("parsed_url:", parsed_url)
    file_path = unquote(parsed_url.path)
    if os.name == 'nt':
        file_path = file_path[1:]
    else:
        file_path = file_path
    return file_path

class PhyloMatrix:
    def __init__(self):
        self.taxa_list = []
        self.char_list = []
        self.data_list = []
        self.data_hash = {}
        self.n_taxa = 0
        self.n_chars = 0
        self.command_hash = {}
        self.dataset_name = ''
        self.formatted_data_hash = {}
        self.formatted_data_list = []

    def taxa_list_as_string(self,separator=","):
        return separator.join(self.taxa_list)

    def char_list_as_string(self,separator=","):
        return separator.join(self.char_list)

class PhyloDatafile():
    def __init__(self):
        self.dataset_name = ''
        self.file_text = None
        self.file_type = None
        self.line_list = []
        self.block_list = []
        self.block_hash = {}
        self.nexus_command_hash = {}
        self.phylo_matrix = PhyloMatrix()
        self.character_definition_hash = {}

        self.taxa_list = []
        self.data_list = []
        self.data_hash = {}
        self.formatted_data_hash = {}
        self.formatted_data_list = []
        self.n_chars = 0
        self.n_taxa = 0

    def loadfile(self,a_filepath):
        filepath,filename = os.path.split(a_filepath)
        filename, fileext = os.path.splitext(filename.upper())
        self.dataset_name = filename

        # determine by filetype
        if fileext.upper() in ['.NEX','.NEXUS']:
            self.file_type='Nexus'
        elif fileext.upper() in ['.PHY','.PHYLIP']:
            self.file_type='Phylip'
        elif fileext.upper() in ['.TNT']:
            self.file_type='TNT'
        #print("filetype:", self.file_type, filename, fileext)
        
        #read first line
        file = open(a_filepath,mode='r')
        self.file_text = file.read()
        file.close()

        self.line_list = self.file_text.split('\n')
        if not self.file_type:
            upper_file_text = self.file_text.upper()
            #first_line = self.line_list[0].upper()
            if upper_file_text.find('#NEXUS') > -1:
                self.file_type = 'Nexus'
            elif upper_file_text.find('XREAD') > -1:
                self.file_type = 'TNT'
        #print("File type:", self.file_type)
        
        if self.file_type == 'Nexus':
            #print("nexus file")
            self.parse_nexus_file()
            if 'DATA' in self.block_hash.keys():
                self.parse_nexus_block(self.block_hash['DATA'])
            if 'TAXA' in self.block_hash.keys():
                #print('taxa block')
                self.parse_nexus_block(self.block_hash['TAXA'])
                #print('nchar, ntax', self.n_chars, self.n_taxa)
            if 'CHARACTERS' in self.block_hash.keys():
                print('characters block')
                self.parse_nexus_block(self.block_hash['CHARACTERS'])
                #print('nchar, ntax', self.n_chars, self.n_taxa)
            if 'MRBAYES' in self.block_hash.keys():
                #print("mr bayes block exists")
                pass
        elif self.file_type == 'Phylip':
            #print("phylip file")
            self.parse_phylip_file(self.line_list)
        elif self.file_type == 'TNT':
            #print("TNT file")
            self.parse_tnt_file(self.line_list)
            #self.parse_tnt_File()
        
        if self.phylo_matrix.dataset_name != '':
            self.dataset_name = self.phylo_matrix.dataset_name
        #print("file parsing done")
        return True

    def parse_nexus_file(self,line_list=None):
        if not line_list:
            line_list = self.line_list
        curr_block=None
        in_block = False
        for line in line_list:
            #print(line)
            begin_line = re.match(r"\s*begin\s+(\w+)",line,flags=re.IGNORECASE)
            end_line = re.match(r"\s*end\s*;",line,flags=re.IGNORECASE)

            if begin_line:
                #print("begin", begin_line)
                curr_block = {}
                curr_block['name'] = begin_line.group(1).upper()
                curr_block['text'] = []
                in_block = True
            elif end_line:
                #print("end block")
                self.block_list.append(curr_block)
                #if curr_block['name'] == 'DATA':
                self.block_hash[curr_block['name']] = curr_block['text']
                in_block = False
            elif in_block:
                #print(line)
                curr_block['text'].append(line)
        return #block_list
    
    def parse_nexus_block(self,line_list):
        in_matrix = False
        for line in line_list:
            #print(line)
            matrix_begin = re.match(r"\s*matrix\s*",line,flags=re.IGNORECASE)
            if matrix_begin:
                #self.taxa_list = []
                #self.data_list = []
                #self.data_hash = {}
                #self.nexus_command_hash = {}
                in_matrix = True
            elif in_matrix:
                matrix_match = re.match(r"^\s*(\S+)\s+(.+);*",line)
                if matrix_match:
                    #print("matrix:",line)
                    species_name = matrix_match.group(1)
                    data_line = matrix_match.group(2)
                    if species_name not in self.taxa_list:
                        self.taxa_list.append(species_name)
                    self.data_list.append(data_line)
                    self.data_hash[species_name] = data_line
            else:
                #in data block but not in matrix ==> command/variable
                command_match = re.match(r"^\s*(\S+)\s+(.*);",line.upper(),flags=re.IGNORECASE)
                if command_match:
                    #print("command:",line)
                    command = command_match.group(1)
                    variable_string = command_match.group(2)
                    variable_list = re.findall(r"(\w+)\s*=\s*(\S+)",variable_string)
                    #print(command,variable_list)
                    if command not in self.nexus_command_hash.keys():
                        self.nexus_command_hash[command] = {}
                    for variable in variable_list:
                        self.nexus_command_hash[command][variable[0]] = variable[1]
                    #print(self.nexus_command_hash)
                #pass

            matrix_end = re.match(".*;.*",line)
            if matrix_end:
                in_matrix = False
            #print(self.nexus_command_hash)
        if 'DIMENSIONS' in self.nexus_command_hash.keys():
            if 'NTAX' in self.nexus_command_hash['DIMENSIONS']:
                ntax = int(self.nexus_command_hash['DIMENSIONS']['NTAX'])
                self.n_taxa = int(ntax)
            if 'NCHAR' in self.nexus_command_hash['DIMENSIONS']:
                nchar = int(self.nexus_command_hash['DIMENSIONS']['NCHAR'])
                self.n_chars = int(nchar)
        #print("number of taxa", ntax, len(self.taxa_list))
        #print("number of char", nchar)
        self.format_datamatrix()

    def parse_tnt_file(self,line_list):
        in_header = False
        in_body = True
        for line in line_list:
            # check if first line contains dataset name and taxa/chars count
            xread_match = re.match(r"xread",line,flags=re.IGNORECASE)
            datasetname_match = re.match(r"'(.*)'",line)
            count_match = re.match(r"(\d+)\s+(\d+)",line)
            data_match = re.match(r"^(\S+)\s+(.+)$",line)
            if xread_match:
                in_header = True
            if datasetname_match:
                self.dataset_name = datasetname_match.group(1)
            if count_match and in_header:
                self.n_chars = count_match.group(1)
                self.n_taxa = count_match.group(2)
            if not count_match and not datasetname_match and data_match:
                in_header = False
                in_body = True
                taxon_name = data_match.group(1)
                data = data_match.group(2)
                self.taxa_list.append(taxon_name)
                self.data_list.append(data)
                self.data_hash[taxon_name] = data

        self.format_datamatrix()

    def parse_phylip_file(self,line_list):
        total_linenum = len(line_list)
        sequential_format = False
        interleaved_format = False
        taxon_data_count = 0
        for line in line_list:
            # check if first line contains dataset name and taxa/chars count
            count_match = re.match(r"^\s*(\d+)\s+(\d+)\s*$",line)
            data_match = re.match(r"^(\S+)\s+(.+)\s*$",line)
            interleaved_data_match = re.match(r"^\s+(.+)\s*$",line)
            if count_match:
                self.n_chars = count_match.group(2)
                self.n_taxa = count_match.group(1)
                if int(total_linenum) > 2 * int(self.n_taxa):
                    print("interleaved format")
                    interleaved_format = True
                else:
                    print("sequential format")
                    sequential_format = True

            if not count_match and data_match:
                taxon_name = data_match.group(1)
                data = data_match.group(2)
                self.taxa_list.append(taxon_name)
                self.data_list.append(data)
                self.data_hash[taxon_name] = data
                taxon_data_count += 1

            if interleaved_data_match:
                pass
                
        self.format_datamatrix()

    def format_datamatrix(self):
        self.datamatrix = []

        for species in self.taxa_list:
            data = self.data_hash[species]
            array_data = []
            poly_char = ''
            #print(species, data)
            #print(species,len(data),data)
            is_poly = False
            for char in data:
                #print(char,)
                if char in [ '(','{','[']:
                    is_poly = True
                    array_data.append([])
                elif char in [ ')','}',']']:
                    array_data[-1].append(poly_char)
                    poly_char = ''
                    is_poly = False
                else:
                    if is_poly:
                        if char == ' ':
                            array_data[-1].append(poly_char)
                            poly_char = ''
                        else:
                            poly_char += char
                    else:
                        array_data.append(char)

            self.formatted_data_hash[species] = array_data
            formatted_data = [species]
            formatted_data.extend(array_data)
            self.formatted_data_list.append( formatted_data )
            self.datamatrix.append(array_data)
            #print(species, len(array_data),array_data)

            #formatted_data = data.split()
            #print(array_data)
            #if len(data) != nchar:
            #else:

        #print(data_hash)
        #print(self.command_hash)
class PhyloTreefile:
    def __init__(self):
        self.line_list = []
        self.block_list = []
        self.block_hash = {}
        self.taxa_list = []
        self.taxa_hash = {}
        self.tree_text_list = []
        self.tree_text_hash = {}
        self.tree_object_hash = {}
        self.file_type = None
        self.tree_list = []

    def readtree(self,a_filepath,filetype):
        filepath,filename = os.path.split(a_filepath)
        filename, fileext = os.path.splitext(filename.upper())
        self.dataset_name = filename

        self.file_type = filetype

        #print("file type 1:", self.file_type, a_filepath)
        # determine by filetype
        if not self.file_type:
            if fileext.upper() in ['.NEX','.NEXUS']:
                self.file_type='Nexus'
            elif fileext.upper() in ['.TRE',]:
                self.file_type='tre'
            # check if file exists
        if not os.path.exists(a_filepath):
            return False

        #print("file type 2:", self.file_type, a_filepath)
        #read first line
        file = open(a_filepath,mode='r')
        self.file_text = file.read()
        file.close()

        self.line_list = self.file_text.split('\n')
        if not self.file_type:
            upper_file_text = self.file_text.upper()
            #first_line = self.line_list[0].upper()
            if upper_file_text.find('#NEXUS') > -1:
                self.file_type = 'Nexus'
        #print("File type 3:", self.file_type)
        
        if self.file_type == 'Nexus':
            #print("nexus file")
            self.parse_nexus_file()
            if self.block_hash['TREES']:
                tree_lines = self.block_hash['TREES']
                taxa_begin = False
                taxa_end = False
                curr_tree_name = ""
                prev_tree_name = ""
                whole_tree = " ".join( tree_lines )
                tree_sections = whole_tree.split(";")
                self.tree_section = {}
                for section in tree_sections:
                    #print(section)
                    section_line = re.search(r"\s*(\w+)\s+(.+)",section,flags=re.IGNORECASE)
                    if section_line:
                        section_name = section_line.group(1)
                        section_contents = section_line.group(2)
                        if section_name not in self.tree_section.keys():
                            self.tree_section[section_name] = []
                        self.tree_section[section_name].append(section_contents)
                            
                if 'translate' in self.tree_section.keys():
                    taxa_list = self.tree_section['translate'][0].split(",")
                    #print(taxa_list)
                    for taxon in taxa_list:
                        taxon = taxon.strip()
                        #print(taxon)
                        taxon_line = re.search(r"(\S+)\s+(\S+)",taxon,flags=re.IGNORECASE)
                        if taxon_line:
                            taxon_index = taxon_line.group(1)
                            taxon_name = taxon_line.group(2)
                            self.taxa_list.append(taxon_name)
                            self.taxa_hash[taxon_index] = taxon_name
                if 'tree' in self.tree_section.keys():
                    #self.tree_hash = {}
                    for tree in self.tree_section['tree']:
                        #print("tree:[",tree,"]")
                        tree = tree.strip()
                        tree_name, tree_text = tree.split("=",1)
                        #tree_line = re.search("(\w+)\s*=(.+)",tree,flags=re.IGNORECASE)
                        tree_name = tree_name.strip()
                        tree_text = tree_text.strip()
                        self.tree_text_hash[tree_name] = tree_text
                        self.tree_list.append(tree_text)
                    #print(self.tree_section['tree'])
                #print(self.taxa_hash)
                return True
                for line in tree_lines:
                    
                    
                    print("[",line,"]")
                    taxa_begin_line = re.search("translate",line,flags=re.IGNORECASE)
                    taxa_end_line = re.search(";",line,flags=re.IGNORECASE)
                    if taxa_begin_line:
                        print("taxa begin")
                        taxa_begin = True
                        continue
                    if taxa_end_line:
                        print("taxa end")
                        taxa_end = True
                        continue
                    if taxa_begin and not taxa_end:
                        taxon_line = re.search(r"^\s*(\d+)\s+(\S+)\s*$",line,flags=re.IGNORECASE)
                        #print(taxon_line)
                        if taxon_line:
                            taxon_idx = taxon_line.group(1)
                            taxon_name = taxon_line.group(2)
                            if taxon_name[-1] == ',':
                                taxon_name = taxon_name[:-1]
                            self.taxa_hash[taxon_idx] = taxon_name
                            self.taxa_list.append(taxon_name)
                    if taxa_end:
                        print("taxa end and now looking for tree")
                        print(line)
                        tree_begin_line = re.search(r"^\s*tree\s+(\S+)\s*=\s*(.*)$",line,flags=re.IGNORECASE)
                        tree_end_line = re.search("(.*);",line)
                        print(tree_begin_line, tree_end_line)
                        if tree_begin_line:
                            curr_tree_name = tree_begin_line.group(1)
                            print("tree name:", curr_tree_name)
                            if tree_end_line:
                                tree_text = tree_begin_line.group(2)
                                self.tree_text_hash[curr_tree_name] = tree_text
                        elif tree_end_line:
                            self.tree_text_hash[curr_tree_name] += tree_text

                if self.tree_text_hash:
                    for tree_key in self.tree_text_hash.keys():
                        tree_text = self.tree_text_hash[tree_key]
                        self.tree_text_hash[tree_key] = self.remove_comment(tree_text)
        elif self.file_type == 'tre':
            self.parse_tre_file(self.line_list)
        elif self.file_type == 'treefile':
            self.parse_IQTree_treefile(self.line_list)
        else:
            return False

        return True

    def parse_IQTree_treefile(self,line_list):
        for line in line_list:
            # find "tread" line
            if re.match(r".*;",line,flags=re.IGNORECASE):
                tree_text = line.replace(";","")
                self.tree_list.append(tree_text)


    def parse_tre_file(self,line_list):
        header_found = False
        for line in line_list:
            # find "tread" line
            if re.match(r"tread.*",line,flags=re.IGNORECASE):
                #self.file_type = 'tread'
                header_found = True
                continue
            elif re.match(r"proc.*",line,flags=re.IGNORECASE):
                #self.file_type = 'proc'
                
                break
            if header_found:
                tree_text = line.replace(";","")
                tree_text = tree_text.replace("*","")
                tree_text = tree_text.replace("(","( ")
                tree_text = tree_text.replace(")"," ) ")
                str_list = []
                raw_list = tree_text.split(" ")
                for item in raw_list:
                    if item != "":
                        if len(str_list) > 0:
                            if item == "(":
                                if str_list[-1] != "(":
                                    str_list.append(",")
                            else:
                                try :
                                    int(item)
                                    try:
                                        int(str_list[-1])
                                        if int(str_list[-1]) > 0 and int(item) > 0:
                                            str_list.append(",")
                                    except:
                                        pass
                                except:
                                    pass#str_list.append(item)
                            
                                #int(str_list[-1]) > 0 and int(item) > 0:
                                #str_list.append(",")
                            
                        str_list.append(item)
                tree_text = "".join(str_list)
                self.tree_list.append(tree_text)
                #print(tree_text)


            

    def remove_comment(self,tree_text):
        #print(tree_text[15],tree_text[20])
        #print(tree_text)
        new_tree_text = ''
        for tree_char in tree_text:
            if tree_char == '[':
                in_comment = True
                continue
            elif tree_char == ']':
                in_comment = False
                continue
            if not in_comment:
                new_tree_text += tree_char
        #print(new_tree_text)
        return new_tree_text
    def parse_tree(self,tree_text):
        tree = []
        idx = 0
        subtree, processed_index = self.parse_subtree(tree_text[1:])
        #print(subtree)

        return subtree
        idx = processed_index
        tree.append(subtree)
        #for idx in range(len(tree_text[]))
        while( processed_index < len(tree_text)):
            subtree, processed_index = self.parse_subtree(remaining_text)
            if(subtree):
                tree.append(subtree)

    def parse_subtree(self,tree_text,depth=0):
        tree = []
        taxon=""
        #print("parse:",tree_text)
        #for idx in range(len(tree_text)):
        idx=0
        while( idx < len(tree_text)):
            char = tree_text[idx]
            print("depth",depth,"idx", idx,"char",char)
            if char == ' ':
                continue
            if char == '(':
                subtree, processed_index = self.parse_subtree(tree_text[idx+1:],depth+1)
                print("returned subtree", subtree, "processed_index", processed_index, "idx", idx, "tree_text[", tree_text,"]","depth",depth)
                idx += processed_index
                print("depth",depth,"idx", idx)
                if(subtree):
                    tree.append(subtree)
            elif char == ')':
                if taxon != "":
                    print("met ')', and add taxon",taxon, "idx=",idx)
                    tree.append(taxon)
                return tree, idx+1
            elif char == ",":
                print("met ',', and add taxon",taxon, "idx=",idx)
                tree.append(taxon)
                taxon = ""
            else:
                taxon += char
            idx+=1
        if taxon != "":
            tree.append(taxon)
        return tree, idx+1

    def parse_nexus_file(self,line_list=None):
        if not line_list:
            line_list = self.line_list
        curr_block=None
        in_block = False
        for line in line_list:
            #print(line)
            begin_line = re.match(r"begin\s+(\S+)\s*;",line,flags=re.IGNORECASE)
            end_line = re.match(r"end\s*;",line,flags=re.IGNORECASE)

            if begin_line:
                #print(begin_line)
                curr_block = {}
                curr_block['name'] = begin_line.group(1).upper()
                curr_block['text'] = []
                in_block = True
            elif end_line:
                #print("end block")
                self.block_list.append(curr_block)
                #if curr_block['name'] == 'DATA':
                self.block_hash[curr_block['name']] = curr_block['text']
                in_block = False
            elif in_block:
                curr_block['text'].append(line)
        return #block_list
            