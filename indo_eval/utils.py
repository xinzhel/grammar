# read all the 'txt' files in templates/
import os
import json
import glob
import re
from typing import List, Dict, Tuple


def read_sql_templates_from_txt_files(directory="templates/sql/") -> Dict[str, List[str]]:
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

def print_length_of_outermost_lists(str_to_list: Dict[str, List[str]]):
   
    print("Number of SQL templates for each table:")
    for key, value in str_to_list.items():
        print(key, len(value))

    print("Total number of templates: ", sum([len(str_to_list[k]) for k in str_to_list]))

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

def read_templates(file="templates/text/long_for_each_table.json"):
    """ Read the templates from a json file.
    Args:
        file (str, optional): Path to the json file. Defaults to "templates/text/long_for_each_table.json".
    
    Returns:
        templates_all_entities (Dict[str, Dict[str, List[str]]]): Dictionary of dictionaries where the key is the table name and the value is a dictionary of templates, 
            , i.e.,
            { 
                table1: 
                    {
                        "sql_template1": [text1, text2], 
                        "sql_template2": [text1, text2]
                    }, 
                table2: 
                    {
                        "sql_template1": [text1, text2], 
                        "sql_template2": [text1, text2]
                    }, 
                ...
            }

        sql_templates_all_entities (Dict[str, List[str]]): Dictionary of lists where the key is the table name and the value is a list of templates.
            , i.e., 
            {
                table1: 
                    [
                        sql_template1, 
                        ...
                    ], 
                ...
            }

        placeholders_all_entities ( Dict[str, List[List[str]]]): Dictionary where the key is the table name and the value is a two-level list
            , i.e., 
            {
                table1: 
                    [
                        [placeholder1_for_sql_template1, placeholder2_for_sql_template1], 
                        [placeholder1_for_sql_template2, placeholder2_for_sql_template2]
                        ...
                    ], 
                ...
            }

        text_templates_all_entities (Dict[str, List[str]]): Dictionary of lists where the key is the table name and the value is a list of texts.
            , i.e., 
            {
                table1: 
                    [
                        [text_template1_for_sql_template1, text_template2_for_sql_template1],
                        [text_template1_for_sql_template2, text_template2_for_sql_template2],
                        ...
                    ],
                ...
            }        
    """
    with open(file, "r", encoding="utf-8") as f:
        templates_all_entities = json.load(f)

    # sql_templates 
    sql_templates_all_entities = { table: list(templates_all_entities[table].keys()) for table in templates_all_entities}
    print_length_of_outermost_lists(sql_templates_all_entities) # Print statistics about the templates

    # placeholders
    placeholders_all_entities = {}
    for table_name, templates in sql_templates_all_entities.items():
        # Extract placeholders
        placeholders = extract_placeholders(templates)
        placeholders_all_entities[table_name] = placeholders

    # text_templates
    text_templates_all_entities = {}
    for table_name, sql_to_text_templates in templates_all_entities.items():
        # Extract text_templates
        text_templates = [sql_to_text_templates[sql_template] for sql_template in sql_to_text_templates]
        text_templates_all_entities[table_name] = text_templates
    # print_length_of_outermost_lists(text_templates_all_entities)

    return templates_all_entities, sql_templates_all_entities, placeholders_all_entities, text_templates_all_entities