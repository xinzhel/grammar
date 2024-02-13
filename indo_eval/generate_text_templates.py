from indo_eval.llm import gpt4_llm
import os
import json
import langchain
print(langchain.__version__)
from langchain.prompts import PromptTemplate
from indo_eval.prompt import list_item_suffix

##### Prompts #####
constraints = {
    "short": """Short and Clear: Keep your queries short and straightforward. Cut down on words and skip parts of speech, such as conjunctions and articles. It's okay to use fragmented phrases as long as they still convey the full meaning. Valid examples: "client of '[Project.Name]'" or "client for '[Project.Name]'" """,
    "shortest": """Short and Clear: Keep your queries short and straightforward. Cut down on words and skip parts of speech, such as conjunctions and articles. It's okay to use fragmented phrases as long as they still convey the full meaning. Valid examples: "client of '[Project.Name]'" or "client for '[Project.Name]'"; Invalid Examples: "Find the client of a project named '[Project.Name]'. """,
    "long": "Complex Sentence Structure: Ensure your queries are always in complete sentences. Opt for longer, more complex sentence structures, incorporating elements of speech like conjunctions and articles for fuller expression. Each query should be at least 30 words long. You can add context and background information to the query.""",
    "interrogative": "Interrogative Form: Queries should take the form of direct questions, using interrogative words like \"who,\" \"what,\" \"where,\" \"when,\" \"why,\" and \"how.\" This form directly signals a request for information.",
    "directives": "Directives: Queries should be framed as directives or commands, such as \"Tell me about…\" or \"Show me…\". These are less interrogative but still clearly indicate a request for information.",
    "formal": "Formal: Queries should be written in a formal tone, using proper grammar and avoiding slang or colloquialisms. This is the most appropriate tone for professional settings.",
    "casual": "Formal: Queries should be written in a casual tone, using informal grammar and colloquialisms. This is the most appropriate tone for casual settings."
}

task_description_tpl = PromptTemplate.from_template(
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

##### Generate Text Templates #####
def generate_texts( sql_templates, linguistic_attr):
    """ 
    Args:
    task_description_prompt: the prompt for the task description used for system message
    """
    
    task_description_prompt = task_description_tpl.format(constraints=constraints[linguistic_attr]+list_item_suffix)
    given_sql_template_tpl = PromptTemplate.from_template(
        template="""##DATA SCHEMA##
        {sql_template}

        ##RESPONSE_START##
        """
    )
    
   
    texts_for_templates = {}
    for i, sql_template in enumerate(sql_templates):
        print(sql_template)
        response = gpt4_llm(given_sql_template_tpl.format(sql_template=sql_template), task_description_prompt)
        texts_for_templates[sql_template] = [x for x in response.split("\n") if x]
        
    return texts_for_templates

def generate_texts_for_all_domains(all_templates, linguistic_attr):
    """ 
    Args:
    all_templates: a dictionary with domain names as keys and lists of SQL templates as values
    linguistic_attr: a string indicating the linguistic attribute of the text, e.g., "short", "long", "interrogative", "directives", "formal", "casual"

    Returns:
    a dictionary with domain names as keys and lists of text templates as values, as the following structure: 
    { domain1: {"sql_template1": [text1, text2], 
               "sql_template2": [text1, text2]}, 
     {domain2: {"sql_template1": [text1, text2], 
                "sql_template2": [text1, text2}, 
    ...
    }
    """
    results = {}
    for domain, sql_templates in all_templates.items():
        text_templates = generate_texts(sql_templates, linguistic_attr)
        results[domain] = text_templates
    return results


