# read all the 'txt' files in templates/
import os
import json
import glob
import re
from typing import List, Dict, Tuple


def read_sql_templates_from_txt(directory="templates/sql/") -> Dict[str, List[str]]:
    """ Read all the txt files in the directory and return a dictionary of lists
    where the key is the table name and the value is a list of templates.

    Args:
        directory (str, optional): Path to the directory. Defaults to "templates/sql/".
    
    Returns:
        sql_templates_all_entities (Dict[str, List[str]]): Dictionary of lists where the key is the table name and the value is a list of templates.
         , i.e., {table1: [sql_template1, ...], ...}
    """
    # Path to the directory
    directory_path = directory

    # List to hold the contents of each txt file
    sql_templates_all_entities = {}

    # Loop through all txt files in the directory
    for filepath in glob.glob(os.path.join(directory_path, '*.txt')):
        # file name
        filename = filepath.split('/')[-1][:-4]
        with open(filepath, 'r') as file:
            # read a list of lines
            content = file.readlines()
            # remove whitespace characters like `\n` at the end of each line
            content = [x.strip() for x in content]
            sql_templates_all_entities[filename] = content
    return sql_templates_all_entities

def extract_placeholders(sql_templates):
    """
    Extracts placeholders from a list of SQL query templates.
    
    Args:
    sql_templates (List[str]): A list of SQL query templates.

    Returns:
    placeholders (List[List[str]]): A list of lists, each containing placeholders from a corresponding SQL template.
    """
    placeholders = []
    pattern = r"\[([^\]]+)\]"  # Pattern to match placeholders like [Some.Placeholder]

    for template in sql_templates:
        found = re.findall(pattern, template)
        placeholders.append(found)

    return placeholders

def extract_info_for_qa_generation(sql_to_text_templates):
    """ 
    Args:
        sql_to_text_templates ( Dict[str, List[str]]): Dictionaries where the key is the table name and the value is a dictionary of templates, 
        , i.e., {
                "sql_template1": [text_template1, text_template2], 
                "sql_template2": [text_template1, text_template2]
            }, 


    Returns:

        sql_templates ( List[str]): a list of SQL templates.
            , i.e., [sql_template1, ... ], 
 

        placeholders (  List[List[str]]): a list of lists, each containing placeholders from a corresponding SQL template.
            , i.e., 
            [
                [placeholder1_for_sql_template1, placeholder2_for_sql_template1], 
                [placeholder1_for_sql_template2, placeholder2_for_sql_template2]
                ...
            ]
          

        text_templates (List[List[str]]): a list of lists, each containing text templates for a corresponding SQL template.
            , i.e., 
   
                    [
                        [text_template1_for_sql_template1, text_template2_for_sql_template1],
                        [text_template1_for_sql_template2, text_template2_for_sql_template2],
                        ...
                    ],
  
    """
    sql_templates = list(sql_to_text_templates.keys())
    text_templates = list(sql_to_text_templates.values())
    placeholders = extract_placeholders(sql_templates)

    return sql_templates, placeholders, text_templates
