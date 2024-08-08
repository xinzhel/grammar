import json
import os
from typing import List
from langchain.prompts import PromptTemplate
from grammar.prompt import list_item_suffix
from grammar.generator import Generator

class TextTemplateGenerator(Generator):

    verbalizer = {
                "short": """Short and Clear: Keep your queries short and straightforward. Cut down on words and skip parts of speech, such as conjunctions and articles. It's okay to use fragmented phrases as long as they still convey the full meaning. Valid examples: "client of '[Project.Name]'" or "client for '[Project.Name]'"; Invalid Examples: "Find the client of a project named '[Project.Name]'. """,
                "long": "Complex Sentence Structure: Ensure your queries are always in complete sentences. Opt for longer, more complex sentence structures, incorporating elements of speech like conjunctions and articles for fuller expression. Each query should be at least 30 words long. You can add context and background information to the query.""",
                "interrogative": "Interrogative Form: Queries should take the form of direct questions, using interrogative words like \"who,\" \"what,\" \"where,\" \"when,\" \"why,\" and \"how.\" This form directly signals a request for information.",
                "directives": "Directives: Queries should be framed as directives or commands, such as \"Tell me about…\" or \"Show me…\". These are less interrogative but still clearly indicate a request for information.",
                "formal": "Formal: Queries should be written in a formal tone, using proper grammar and avoiding slang or colloquialisms. This is the most appropriate tone for professional settings.",
                "casual": "Formal: Queries should be written in a casual tone, using informal grammar and colloquialisms. This is the most appropriate tone for casual settings."
            }
    
    system_msg_tpl = PromptTemplate.from_template(
        template = """Convert the given SQL query with placeholders into human understandable text. 
        
        You must follow the basic criteria below: 
        ##CRITERIA## \
        \n\t- Each placeholder is a combination of table and column names, formatted as "[Table.Column]", like "[User.Name]".\
        \n\t- Keep the original placeholders from the SQL queries intact.\
        \n\t- Create text that can be comprehended by people who have no knowledge of relational databases.\
        \n\t- {constraints}

        ##RESPONSE FORMAT##
        - No prefix or suffix, e.g., "1. " or "A. " or quotation marks for each text template.
        - Generate {num_generations} translations of text that are diverse in phrasing and syntax, each in a separate line 
        - Do not include any other text in your response, even something like ##RESPONSE_END##.
        
    """)

    instance_msg_tpl = PromptTemplate.from_template(
            template="""##DATA SCHEMA##
            {sql_template}

            ##RESPONSE_START##
            """
        )
    
    def __init__(self, verbalize_attrs, llm=None) -> None:
        assert isinstance(verbalize_attrs, str), "`verbalize_attrs` must be a string"
        super().__init__(verbalize_attrs, llm)

    def _generate(self, sql_template:str, num_generations:int=3, verbose=False):
        """ Generate text templates for a given SQL template.
        Args:
            sql_template: a SQL template
        Returns:
            texts: a list of text templates
        """
        self.system_msg = self.system_msg_tpl.format(constraints=self.verbalizer[self._system_msg_attrs[0]]+list_item_suffix, num_generations=num_generations)
        instance_msg = self.instance_msg_tpl.format(sql_template=sql_template)
        response = self.llm(instance_msg, self.system_msg)
        return [x for x in response.split("\n") if x]
    
    def explain_cache(self):
        print('=== Cache Meta Information ===')
        print("Key: SQL Template")
        print("Value: Text Templates")
        print("==============================")
    


    