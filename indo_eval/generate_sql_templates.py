from langchain.prompts.prompt import PromptTemplate
import json
import os
from indo_eval.db_tool import db_tool
from indo_eval.llm import gpt4_llm as llm

system_msg_tpl = PromptTemplate.from_template(
    template="""You are a SQL query Template Generator: Generate ACCEPTABLE SQL query templates with placeholders according to the give data schema and requirements.
    A simple example of an acceptable SQL query template is: SELECT Industry FROM Company WHERE Name = '[Company.Name]';
    
    You must follow the basic criteria below: 
    ##CRITERIA## \
    \n\t- The placeholder format should be a combination of a table name and a column name, enclosed within square brackets, e.g., '[User.Name]'.\
    \n\t- Use only 'SELECT' queries.\
    \n\t- Select specific column(s) instead of using '*'. Avoid projecting attributes that appear in the predicate.\
    \n\t- The selected and condition columns in the query MUST BE MEANINGFUL and DESCRIPTIVE to ensure the queries are easily understood by non-technical users. \
    \n\t- Avoid using technical column names that don't clearly signify the nature of the entities or objects involved, e.g., column for semantically void record identifiers.\
    \n\t- Do not create redundant or semantically duplicated queries when translated into natural language. \
    \n\t{requirements}\
    \n\t- If no acceptable SQL template can be generated with the given table and column information, do not generate any text.

    ##RESPONSE FORMAT##
    - Output each SQL template as a single line, without any prefix or suffix.
    - Do not include any other text in your response, even something like ##RESPONSE_END##.
""")

acceptable_sql_tpl = PromptTemplate.from_template(
    template=
    """ 
    ##DATA SCHEMA##
    {stringified_schema} 

    ##RESPONSE_START##
    """)

examples = """Examples of acceptable SQL templates:
    1. SELECT Industry FROM Company WHERE Name = '[Company.Name]';
    2. SELECT Location, Address FROM Company WHERE Industry = '[Company.Industry]';

    Please generate similar SQL query templates based on these guidelines."""

def generate_prompt(entity_types, requirements):

    # generate templates
    schema = db_tool.infer_schema_from_entity_types(entity_types)
    stringified_schema = db_tool.stringify_schema(schema)
    # stringified_schema = f"Table: {table_name}. Here is the information of columns: {json.dumps(columns)}"
    # print(stringified_schema)
    acceptable_sql = acceptable_sql_tpl.format(stringified_schema=stringified_schema)
    system_msg = system_msg_tpl.format(requirements=requirements)
    return acceptable_sql, system_msg

def generate_sql_templates(entity_types, requirements):
    acceptable_sql, system_msg = generate_prompt(entity_types, requirements)
    return llm(acceptable_sql, system_msg )

def save_sql_templates_to_text(templates, file_name=None, directory="./templates/sql/"):
    filename = file_name or f"temp.txt"
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as file:
        file.write(templates)