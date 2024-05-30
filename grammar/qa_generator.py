import itertools
import json
import os
from typing import List
from grammar.utils import extract_info_for_qa_generation

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

class QADataGenerator:
    def __init__(self, db_tool) -> None:
        self.db_tool = db_tool

    def generate(self, sql_to_text_templates):
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
        extract_info_for_qa_generation
        sql_templates, placeholders, text_template_lists = extract_info_for_qa_generation(sql_to_text_templates)

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
                fill_in = self.db_tool.query(query)
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
                answer = self.db_tool.query(sql_query)
                
                if answer is None or answer == "":
                    continue
                answers_to_text_queries.append( (answer, text_queries) )
                

                # sql_queries[sql_query_template].append(sql_query)
            all_answers_to_text_queries.append(answers_to_text_queries)

        return all_answers_to_text_queries 

    def print_query_stats(self, answers_to_text_queries):
        total_sql_queries = sum([len(i) for i in answers_to_text_queries])
        print(f"The number of generated SQL queries: ", total_sql_queries)
        total_text_queries = sum([len(j[1]) for i in answers_to_text_queries for j in i ])
        print(f"The number of generated text queries: ", total_text_queries)

    def default_save_path(self, root_dir, file_name):
        root_dir = os.path.join(root_dir, self.__class__.__name__)
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        return os.path.join(root_dir, f"{file_name}")


    def save(self, answers_to_text_queries, root_dir, file_name, overwrite=False):
        file_path = self.default_save_path(root_dir, file_name)
        if os.path.exists(file_path):
            if not overwrite:
                raise ValueError(f"File {file_path} already exists.")
            else:
                os.remove(file_path)

        with open(file_path, 'w') as f:
            json.dump(answers_to_text_queries, f, indent=4)
