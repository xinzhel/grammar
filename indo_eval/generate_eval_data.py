import re
import json

from langchain import SQLDatabase
from langchain.tools.sql_database.tool import QuerySQLDataBaseTool
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql.sqltypes import Date, DateTime, Time
import itertools
import json
import datetime
from typing import List
from indo_eval.db_tool import db_tool

def add_quote(s):
    # Check if the string is already enclosed in quotes (either single or double)
    if (not s.startswith('"') and not s.endswith('"')) and (not s.startswith("'") and not s.endswith("'")):
        # Add double quotes if they don't exist
        return f'"{s}"'
    else:
        # Return the string as is if it already has quotes
        return s
    
def fillin_template(sql_template, text_templates, placeholders, combination):
    """
    Returns:
        sql_template: a SQL query with fill-in values.

        text_templates: a list of text queries with fill-in values.
    """
    # print("Placeholders: ", placeholders)
    # print("Combination: ", combination)

    for placeholder, value in zip(placeholders, combination):
       
        assert value is not None
        
        sql_template = sql_template.replace('[' + placeholder + ']', str(value))
        # TODO: decouple the check the existence of placeholders in text_templates
        text_templates = [text_tpl.replace('[' + placeholder + ']', str(value)) for text_tpl in text_templates if '[' + placeholder + ']' in text_tpl]
    return sql_template, text_templates

def generate_answers_to_text_queries(sql_templates, text_template_lists, placeholders):
    """ Generate answers to text queries.
    Args:
        None
    
    Returns:
        all_answers_to_text_queries List[Dict[str, List]]: a list of dictionaries.
          each element (dict) in the list contains answers-to-queries for a specific SQL template.
          i.e.,
            [
                [(answer_for_fillin1, [fillin1_for_text_template1, fillin1_for_text_template2, ...]), (answer_for_fillin2, [...])], # _for_sql_template1   
                {answer_for_fillin1: [fillin1_for_text_template1, fillin1_for_text_template2, ...], answer_for_fillin2: [...]}, # _for_sql_template2
            ],       
    """
    
    # sql_queries = {template: [] for template in sql_templates}
    all_answers_to_text_queries = []
    
    for placeholders, sql_query_template, text_templates in zip(placeholders, sql_templates, text_template_lists):

        # Get all possible fill-in values for each placeholder
        fill_in_for_placeholders: List[List] = []
        for placeholder in placeholders:
            # Extract table and column name
            table_name = placeholder.split(".")[0]
            column_name = placeholder.split(".")[1]

            # Select unique values from the column
            query = f"SELECT DISTINCT {column_name} FROM {table_name};"
            fill_in = db_tool.query(query)
            fill_in_for_placeholders.append([t[0] for t in eval(fill_in)])
        # print(fill_in_for_placeholders)
        all_combinations = itertools.product(*fill_in_for_placeholders) # Generate all combinations of fill-in values (Cartesian product)
        

        # Generate SQL queries, their answers, corresponding text queries
        answers_to_text_queries = []
        num_fill_in = 0
        for combination in all_combinations:
            if None in combination:
                continue
            assert len(placeholders) == len(combination)
            num_fill_in += 1
            sql_query, text_queries = fillin_template(sql_query_template, text_templates, placeholders, combination)
            answer = db_tool.query(sql_query)
            
            answers_to_text_queries.append( (answer, text_queries) )
            

            # sql_queries[sql_query_template].append(sql_query)
        all_answers_to_text_queries.append(answers_to_text_queries)

    return all_answers_to_text_queries 

def print_query_stats(answers_to_text_queries_all_templates):
    """ 
    Args:
        answers_to_text_queries_all_templates: a dictionary of answers-to-text-queries for all tables.
        i.e.,
        {
            table1: [
                {answer_for_fillin1: [fillin1_for_text_template1, fillin1_for_text_template2, ...], answer_for_fillin2: [...]}, # _for_sql_template1   
                {answer_for_fillin1: [fillin1_for_text_template1, fillin1_for_text_template2, ...], answer_for_fillin2: [...]}, # _for_sql_template2
            ],    
            ...
        }
    """
    for table_name, answers_to_text_queries in answers_to_text_queries_all_templates.items():
        print('Table name: ', table_name)
        total_sql_queries = sum([len(i) for i in answers_to_text_queries])
        print(f"The number of generated SQL queries for the table {table_name}: ", total_sql_queries)
        total_text_queries = sum([len(j[1]) for i in answers_to_text_queries for j in i ])
        print(f"The number of generated text queries for the table {table_name}: ", total_text_queries)

def generate_eval_data(sql_templates_all_entities, text_templates_all_entities, placeholders_all_entities):
    answers_to_text_queries_all_templates = {}

    for table_name in sql_templates_all_entities:
        # print('Date-type columns: ', db_tool.get_date_columns(table_name))
        
        answers_to_text_queries_all_templates[table_name] = generate_answers_to_text_queries(sql_templates_all_entities[table_name], \
                                        text_templates_all_entities[table_name], \
                                            placeholders_all_entities[table_name])
    print_query_stats(answers_to_text_queries_all_templates)
    return answers_to_text_queries_all_templates
