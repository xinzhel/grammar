import os
from typing import List
from langchain.prompts.prompt import PromptTemplate
from grammar.db_tool import DBTool

demos = """Demonstrations of acceptable SQL templates:
    1. SELECT Industry FROM Company WHERE Name = '[Company.Name]';
    2. SELECT Location, Address FROM Company WHERE Industry = '[Company.Industry]';

    Please generate similar SQL query templates based on these guidelines."""

# Requirements
one_placeholder = """- Each query must contain at least one parameter placeholder in the WHERE clause. \
    \n\t"""
no_answer_multiplicity = """- Ensure the query yields a specific and singular answer to avoid multiplicity issues. "SELECT Name, StartDate, EndDate FROM Project WHERE StartDate >= '[Project.StartDate]'" is an invalid example since mulitple projects can start after '[Project.StartDate]' \
    \n\t"""
one_perspective = """- Select only one specific column \
    \n\t"""
one_table = """- Each query must involve only one entity (table). \
    \n\t"""
default_requirements = one_perspective+no_answer_multiplicity+one_placeholder

class SQLTemplateGenerator:
    def __init__(self, sql_connection, llm):
        self.system_msg_tpl =  PromptTemplate.from_template(
    template="""You are a SQL query Template Generator: Generate ACCEPTABLE SQL query templates with placeholders according to the give data schema and requirements.
    A simple example of an acceptable SQL query template is: SELECT Industry FROM Company WHERE Name = '[Company.Name]';
    
    You must follow the basic criteria below: 
    ##CRITERIA## \
    \n\t- The placeholder format should be a combination of a table name and a column name, enclosed within square brackets, e.g., '[User.Name]'.\
    \n\t- Use only 'SELECT' queries.\
    \n\t- Select specific column(s) instead of using '*'. Avoid projecting attributes that appear in the predicate.\
    \n\t- The selected and condition columns in the query MUST BE MEANINGFUL and DESCRIPTIVE to ensure the queries are easily understood by non-technical users. \
    \n\t- ONLY use columns that have clear meanings beyond the database context. If the significance of a column to those unfamiliar with the database is ambiguous, NEVER use it. For example, the predicate "WHERE Company_ID = '[company.Company_ID]'" is invalid since Company_ID may not be meaningful beyond the database context. \
    \n\t- Do not create redundant or semantically duplicated queries when translated into natural language. \
    \n\t{requirements}\
    \n\t- If no acceptable SQL template can be generated with the given table and column information, do not generate any text.

    ##RESPONSE FORMAT##
    - Output each SQL template as a single line, without any prefix or suffix.
    - Do not include any other text in your response, even something like ##RESPONSE_END##.
""")
    # \n\t- Avoid using technical columns that don't clearly signify the nature of the entities or objects involved, e.g., column for semantically void record identifiers.\
        self.system_msg = None
        self.instance_msg = PromptTemplate.from_template(
    template=
    """ 
    ##DATA SCHEMA##
    {stringified_schema} 

    ##RESPONSE_START##
    """) # acceptable sql
        self.db_tool = DBTool(sql_connection)
        self.llm = llm
        # self.demos = demos

    def set_system_msg(self, requirements=None):
        if requirements is None:
            requirements = default_requirements
        self.system_msg = self.system_msg_tpl.format(requirements=requirements)

    def get_instance_msg(self, entity_types):
        schema = self.db_tool.infer_schema_from_entity_types(entity_types)
        stringified_schema = self.db_tool.stringify_schema(schema)
        instance_msg = self.instance_msg.format(stringified_schema=stringified_schema)
        return instance_msg

    def generate(self, entity_types:List[str]=None, verbose=False):
        """Generate SQL templates based on the entity types and requirements.
        Args:
            entity_types (List[str]): a list of entity types
        Returns:
            str: the generated SQL templates"""
        assert self.system_msg is not None, "Please set the system message first."
        if entity_types is None:
            entity_types = self.db_tool.infer_entity_types_from_table_names(verbose=verbose)            
        if verbose:
            print('Generate SQL templates for tables:', entity_types)
        instance_msg = self.get_instance_msg(entity_types)
        templates = self.llm(instance_msg, self.system_msg)
        return templates.split('\n')
    
    def default_save_path(self, root_dir):
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        return os.path.join(root_dir, f"{self.__class__.__name__}/sql_templates.txt")
    
    def save(self, sql_templates:List[str], root_dir, overwrite=False):

        # save the sql_templates to a file
        file_name = self.default_save_path(root_dir)
        if os.path.exists(file_name):
            if not overwrite:
                raise ValueError(f"File {file_name} already exists.")
            else:
                os.remove(file_name)
        sql_templates = '\n'.join(sql_templates)
        with open(file_name, 'w') as file:
            file.write(sql_templates)

    @classmethod
    def load(cls, root_dir):
        file_name = os.path.join(root_dir, f"{cls.__name__}/sql_templates.txt")
        # read lines and convert to list
        with open(file_name, 'r') as file:
            sql_templates = file.readlines()
        
        # remove whitespace characters like `\n` at the end of each line
        sql_templates = [x.strip() for x in sql_templates]
        
        return sql_templates