import json
import os
from typing import List
from langchain.prompts import PromptTemplate
from grammar.prompt import list_item_suffix



class TextTemplateGenerator:

    def __init__(self, llm=None) -> None:
        if llm is None:
            from grammar.llm import gpt4_llm
            llm = gpt4_llm
        self.llm = llm

        # system-level info
        self.system_msg_tpl = PromptTemplate.from_template(
    template = """Convert the given SQL query with placeholders into human understandable text. 
    
    You must follow the basic criteria below: 
    ##CRITERIA## \
    \n\t- Each placeholder is a combination of table and column names, formatted as "[Table.Column]", like "[User.Name]".\
    \n\t- Keep the original placeholders from the SQL queries intact.\
    \n\t- Create text that can be comprehended by people who have no knowledge of relational databases.\
    \n\t- {constraints}

    ##RESPONSE FORMAT##
    - Generate three translations of text that are diverse in phrasing and syntax, each in a separate line 
    - Do not include any other text in your response, even something like ##RESPONSE_END##.
    
""")
        self.linguistic_attr = None
        self.system_msg = None
        self.constraints = {
            "short": """Short and Clear: Keep your queries short and straightforward. Cut down on words and skip parts of speech, such as conjunctions and articles. It's okay to use fragmented phrases as long as they still convey the full meaning. Valid examples: "client of '[Project.Name]'" or "client for '[Project.Name]'"; Invalid Examples: "Find the client of a project named '[Project.Name]'. """,
            "long": "Complex Sentence Structure: Ensure your queries are always in complete sentences. Opt for longer, more complex sentence structures, incorporating elements of speech like conjunctions and articles for fuller expression. Each query should be at least 30 words long. You can add context and background information to the query.""",
            "interrogative": "Interrogative Form: Queries should take the form of direct questions, using interrogative words like \"who,\" \"what,\" \"where,\" \"when,\" \"why,\" and \"how.\" This form directly signals a request for information.",
            "directives": "Directives: Queries should be framed as directives or commands, such as \"Tell me about…\" or \"Show me…\". These are less interrogative but still clearly indicate a request for information.",
            "formal": "Formal: Queries should be written in a formal tone, using proper grammar and avoiding slang or colloquialisms. This is the most appropriate tone for professional settings.",
            "casual": "Formal: Queries should be written in a casual tone, using informal grammar and colloquialisms. This is the most appropriate tone for casual settings."
        }

        # instance-level info
        self.instance_msg = PromptTemplate.from_template(
            template="""##DATA SCHEMA##
            {sql_template}

            ##RESPONSE_START##
            """
        )

        # existing generations
        self.generations = {}
        
    def add_constraint(self, name:str, description:str):
        self.constraints[name] = description

    def set_system_msg(self, linguistic_attr:str):
        """
        Args:
            linguistic_attr: a string indicating the linguistic attribute of the text. 
                It should be the keys of the constraints dictionary.
        """
        assert linguistic_attr in self.constraints, f"Invalid linguistic attribute: {linguistic_attr}"
        self.linguistic_attr = linguistic_attr
        self.system_msg = self.system_msg_tpl.format(constraints=self.constraints[linguistic_attr]+list_item_suffix)
        self.generations = {}

    def generate(self, sql_template:str, verbose=False):
        """ Generate text templates for a given SQL template.
        Args:
            sql_template: a SQL template
        Returns:
            texts: a list of text templates
        """
        assert self.system_msg is not None, "Please set the system message first."
        if verbose:
            print(f"Text templates for the SQL template: {sql_template}")
        instance_msg = self.instance_msg.format(sql_template=sql_template)
        response = self.llm(instance_msg, self.system_msg)
        texts = [x for x in response.split("\n") if x]
        return texts
    
    def generate_batch(self, sql_templates:List[str], global_batch=True, verbose=False):
        """ Generate text templates for a given list of SQL templates. 
            This function can save the results to a file.
        Args:
            sql_templates: a list of SQL templates

        Returns:
            a dictionary with SQL templates as keys and lists of text templates as values
        """
        assert self.system_msg is not None, "Please set the system message first."
        if global_batch:
            for sql_template in sql_templates:
                if sql_template not in self.generations:
                    self.generations[sql_template] = self.generate(sql_template, verbose=verbose) 
                elif verbose:
                    print(f"Text templates for the SQL template: {sql_template}. EXIST!!!")
            return self.generations 
        else:
            return {sql_template: self.generate(sql_template, verbose=verbose) for sql_template in sql_templates}
    
    def from_file(self, linguistic_attr:str, root_dir:str):
        """ Instantiate the object from a file so that we can avoid re-generating the text."""
        self.set_system_msg(linguistic_attr)
        file_name = self.default_save_path(root_dir)
        if os.path.exists(file_name):
            with open(file_name, 'r') as fp:
                self.generations = json.load(fp)
        return self
    
    def default_save_path(self, root_dir):
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        return os.path.join(root_dir, f"{self.__class__.__name__}/{self.linguistic_attr}.json")

    def save(self, results, root_dir, overwrite=False):
        file_name = self.default_save_path(root_dir)
        if os.path.exists(file_name):
            if not overwrite:
                raise ValueError(f"File {file_name} already exists.")
            else:
                os.remove(file_name)
        
        with open(file_name, 'w') as fp:
            json.dump(results, fp)