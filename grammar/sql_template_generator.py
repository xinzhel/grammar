import os
from typing import List, Set, Iterable
from langchain.prompts.prompt import PromptTemplate
from grammar.db_tool import DBTool
from grammar.generator import Generator

demos = """Demonstrations of acceptable SQL templates:
    1. SELECT Industry FROM Company WHERE Name = '[Company.Name]';
    2. SELECT Location, Address FROM Company WHERE Industry = '[Company.Industry]';

    Please generate similar SQL query templates based on these guidelines."""

class SQLTemplateGenerator(Generator):
    verbalizer = {
        "one_placeholder": """- Each query must contain at least one parameter placeholder in the WHERE clause. \
        \n\t""",
        "no_answer_multiplicity": """- Ensure the query yields a specific and singular answer to avoid multiplicity issues. "SELECT Name, StartDate, EndDate FROM Project WHERE StartDate >= '[Project.StartDate]'" is an invalid example since mulitple projects can start after '[Project.StartDate]' \
        \n\t""",
        "one_perspective":  """- Select only one specific column \
        \n\t""",
        "one_table": """- Each query must involve only one entity (table). \
        \n\t"""
        # \n\t- Avoid using technical columns that don't clearly signify the nature of the entities or objects involved, e.g., column for semantically void record identifiers.\
    }
    
    system_msg_tpl =  PromptTemplate.from_template(
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
        \n\t{constraints}\
        \n\t- If no acceptable SQL template can be generated with the given table and column information, do not generate any text.

        ##RESPONSE FORMAT##
        - Output each SQL template as a single line, without any prefix or suffix.
        - Do not include any other text in your response, even something like ##RESPONSE_END##.
    """)

    instance_msg_tpl = PromptTemplate.from_template(
        template= """ 
        ##DATA SCHEMA##
        {stringified_schema} 

        ##RESPONSE_START##
        """) 

    def __init__(self, sql_connection:str, llm=None, verbalize_attrs=['one_perspective', 'no_answer_multiplicity', 'one_placeholder'], requirements=None):
        super().__init__(verbalize_attrs, llm)
        self.system_msg = self.system_msg_tpl.format(constraints=''.join([self.verbalizer[attr] for attr in verbalize_attrs]) )
        self.db_tool = DBTool(sql_connection)
        
    def _generate(self, entity_types:Iterable[str]=None, verbose=False):
        """Generate SQL templates based on the entity types and requirements.
        Args:
            entity_types (Set[str]): a list of entity types
        Returns:
            List[str]: the generated SQL templates"""
        
        if entity_types is None:
            entity_types = self.db_tool.infer_entity_types_from_table_names(verbose=verbose)            
        if verbose:
            print('Generate SQL templates for tables:', entity_types)

        # instantiate the instance message
        schema = self.db_tool.infer_schema_from_entity_types(entity_types)
        stringified_schema = self.db_tool.stringify_schema(schema)
        instance_msg = self.instance_msg_tpl.format(stringified_schema=stringified_schema)

        # generate SQL templates
        return self.llm(instance_msg, self.system_msg).split('\n')
    
    def explain_cache(self):
        pass
    
