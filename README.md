# Grounded and Modular Assessment of Closed-Domain RAG Systems
GRAMMAR is structured around two key components:
1) GRAMMAR-Gen: A Grounded Data Generation Method to generate a set of text queries and a corresponding answer for one query semantics (represented by a SQL query). We call the set of text queries and the corresponding answer a semantic group.
   * A relational database and a LLM are used to generate SQL queries and ground-truth answers; 
   * An LLM is used to generate text queries
2) GRAMMAR-Eval: A Modular Evaluation Protocol to identifying vulnerabilities in three modules in RAG systems: retrieval databases, retrieval methods or the language models.

Below is an example.

<img src="pics/grammar.png" alt="GRAMMAR" width="800" >

To run this example, please use the notebook in the benchmark folder.
* Run GRAMMAR-Gen ([Notebook](benchmarks/grammar_gen.ipynb))
* Generate responses from a RAG system ([Notebook](benchmarks/llm_response.ipynb)) (You can replace this with your own RAG system)
* Run GRAMMAR-Eval ([Notebook](benchmarks/grammar_eval.ipynb))

Below is a demonstration to overview the basic usage for modular evaluation and hyposesis testing.

## GRAMMAR-Gen
GRAMMAR-Gen follows the follwoing steps:

<img src="pics/data_gen_2.0.png" alt="Data Generation Diagram" width="800" >

### Step 1: Preparing Database and LLM

* `DBTool` , implemented by sqlalchemy,  supports various relational databases, e.g., MySQL, SQLite. Refer to [Features - SQLAlchemy](https://www.sqlalchemy.org/features.html#:~:text=Supported Databases,of which support multiple DBAPIs.) for all the supported database.

```python
from grammar.db_tool import DBTool
connection_string = 'sqlite:///spider-database/database/company_employee/company_employee.sqlite'
db_tool = DBTool(connection_string)
```

* `AnyOpenAILLM` supports the use of OpenAI GPT series language models, e.g., `'gpt-3.5-turbo`, `gpt-4`. Refer to the [Models - OpenAI API](https://platform.openai.com/docs/models/model-endpoint-compatibility) for the supported model.

```python
from grammar.llm import AnyOpenAILLM
gpt4_llm = AnyOpenAILLM(model_name = "gpt4")  
```

### Step 2: Generate SQL templates

```python
sql_template_generator = SQLTemplateGenerator(connection_string, llm)
sql_templates = sql_template_generator.generate()
sql_template_generator.save(file_path='sql_templates.json')
```

Use `` to save the output:
The output is saved in "eval_data/spider/SQLTemplateGenerator/sql_templates.txt" :


If you want to generate new SQL templates for other schemas, use `from_file` to instantiate the object. The caching mechanism will merge new generations with old generations and avoid generations for the same schema.
```python
sql_template_generator = SQLTemplateGenerator.from_file("sql_templates.json", sql_connection=connection_string, llm=llm)
sql_template_generator.save(file_path='sql_templates.json')
```
> We HIGHLY ENCOURAGE you to check the reliability of the generated SQL templates. Manually verify and modify them. Before doning the following steps.

Here are the examples in our paper: [`benchmarks/spider/SQLTemplateGenerator/sql_templates.json`](benchmarks/spider/SQLTemplateGenerator/sql_templates.json)


<!-- Below are guidelines for **b) manually modify the SQL templates**:

1. **Selecting Attributes That Are Understandable to Humans**
   The selected and condition columns in the query MUST BE MEANINGFUL and DESCRIPTIVE to ensure the queries are easily understood by non-technical users.

2. **Generating Queries With One Ground-truth Answer**
Avoiding Answer Multiplicity
   In the evaluation of question-answering (QA) models, a unique challenge arises from the existence of multiple valid answers to a single query, which necessitates a nuanced approach to assessing model performance. 
   Consider the question: ""Get the name of the client in the digital industry'". For such a question, a set of correct responses could include any combination of names from a predefined list, such as Apple, Amazon, Meta, Facebook\. This multiplicity of correct answers underscores the complexity of evaluating QA models, as it requires the assessment mechanism to recognize and validate the full spectrum of possible correct answers rather than comparing the model's output against a single 'gold standard' answer. Therefore, queries should be generated to ensure one ground-truth answer. Specifically, the evaluation of certain SQL queries, such as ``SELECT Name FROM Company WHERE Industry = '[Company.Industry]';``, requires a complete and thorough listing of multiple answers that can be dynamically changed. To solve the issue, the solution involves adding a specific criterion to the prompt for generating SQL queries. In contrast, the query ``SELECT Industry FROM Company WHERE Name = '[Company.Name]';`` is preferred as it's likely to yield a singular answer about a company's industry based on a specific company name. -->


### Step 3: Generate Text Templates
Generate text templates give textual constraints, e.g., `long` text.
```python
linguistic_attr = "long"
file_path = f'spider/TextTemplateGenerator/{linguistic_attr}.json'
text_template_generator = TextTemplateGenerator(verbalize_attrs=linguistic_attr, llm=llm) 
sql_to_text_templates = text_template_generator.generate_batch(sql_templates, verbose=True, override=False)
text_template_generator.save(file_path=file_path, override=True)
```
Here are the examples in our paper: [`benchmarks/spider/TextTemplateGenerator/short.json`](benchmarks/spider/TextTemplateGenerator/short.json)

Note that `verbalizer:dict` has been pre-defined in the tool, which will verbalize the attributes into concrete text as prompts. 
Below are default textual verbalizer within `TextTemplateGenerator`. You can define your own by adding new key-value pairs.
> Actually, `SQLTemplateGenerator` also include some attributes for users to easily generate SQL with different characteristics. 
```python
verbalizer = {
               "short": """Short and Clear: Keep your queries short and straightforward. Cut down on words and skip parts of speech, such as conjunctions and articles. It's okay to use fragmented phrases as long as they still convey the full meaning. Valid examples: "client of '[Project.Name]'" or "client for '[Project.Name]'"; Invalid Examples: "Find the client of a project named '[Project.Name]'. """,
               "long": "Complex Sentence Structure: Ensure your queries are always in complete sentences. Opt for longer, more complex sentence structures, incorporating elements of speech like conjunctions and articles for fuller expression. Each query should be at least 30 words long. You can add context and background information to the query.""",
               "interrogative": "Interrogative Form: Queries should take the form of direct questions, using interrogative words like \"who,\" \"what,\" \"where,\" \"when,\" \"why,\" and \"how.\" This form directly signals a request for information.",
               "directives": "Directives: Queries should be framed as directives or commands, such as \"Tell me about…\" or \"Show me…\". These are less interrogative but still clearly indicate a request for information.",
               "formal": "Formal: Queries should be written in a formal tone, using proper grammar and avoiding slang or colloquialisms. This is the most appropriate tone for professional settings.",
               "casual": "Formal: Queries should be written in a casual tone, using informal grammar and colloquialisms. This is the most appropriate tone for casual settings."}
```

### Step 4: Generate Query-Answer Pairs

```python
qa_generator = QADataGenerator(db_tool)
all_answers_to_text_queries = qa_generator.generate(sql_to_text_templates)
qa_generator.print_query_stats(all_answers_to_text_queries)
file_name = f"{linguistic_attr}.json"
qa_generator.save(all_answers_to_text_queries, root_dir, file_name)
```
Here are the examples in our paper: [`benchmarks/spider/QADataGenerator/long.json`](benchmarks/spider/QADataGenerator/long.json)



### Step 5: Re-Run Step 3 and Step 4 to Generate Constrastive Data

For example, one hypothesis can be that models are vulnerable to long queries. The only change is to set `attr=long` at Step 3.


## GRAMMAR-Eval

<!-- # Acknowledgement
A part of this work is progressed as my intern in Aurecon. Special thanks to Theodore Galanos, Slaven Marusic in Aurecon for supporting us via the access to OpenAI models and their retrieval module. -->

### Function 1: Balancing Gap Groups
Since semantics groups can be identified before evaluation, `TextTemplateGenerator` could be enforced to generate 10 generations for all the semantic groups, as demonstrated below.
```python
text_template_generator = TextTemplateGenerator.from_file(file_path=file_path, attrs=linguistic_attr, llm=llm) # 1st change
sql_to_text_templates = text_template_generator.generate_batch(sql_templates, verbose=True, num_generations=10, override=False)
```
### Function 2: Removing Gap Examples 3 & Function 3: Remove LLM Errors
These two functions are tied to `TaggedGroup`. It does two things:
1. tagging each semantic group as gap, robust or non-robust
2. calculating accuracy based on the tagging result 
   * Accuracy (Removing Gap Examples) using `TaggedGroup().get_robustness()` 
   * Accuracy (Removing LLM Errors) using `TaggedGroup().get_accuracy(for_retrieval=True)` 
   * Accurary (Removing Gap Examples & LLM Errors) using `TaggedGroup().get_robustness(for_retrieval=True)` 

```python
import json
from grammar.eval.result import RAGResult
from grammar.eval.tag_group import TaggedGroup 
from grammar.eval.match import SemanticsMatch

def get_eval_results(eval_results, linguistic_attr, root_dir, file_path):
    tagged_group = TaggedGroup(eval_results)
    semnatics_match = SemanticsMatch.from_file(root_dir=root_dir, verbalize_attrs=linguistic_attr)

    for eval_result in eval_results:
        # sleep for 20 seconds after 9 examples
        # if results.index(result) % 9 == 0 and results.index(result) != 0:
        #     print("Sleeping for 20 seconds")
        #     time.sleep(20)
        #     print("Waking up")
        eval_result.judge_retrieval_response(tagged_group=tagged_group, method='use_exist')
        eval_result.judge_rag_response(semnatics_match)

    num_retrieval_failure = sum([result.retrieval_judgement==0 for result in eval_results])
    print(f"Retrieval failed in {num_retrieval_failure} out of {len(eval_results)} examples")
    num_rag_failure = sum([result.judgement=="Incorrect" for result in eval_results])
    print(f"RAG failed in {num_rag_failure} out of {len(eval_results)} examples")
    semnatics_match.save(root_dir=f'{root_dir}', override=True)
    # semnatics_match.llm.gpt_usage_record.write_usage(model_name='chatgptk' )

    # save results
    results = [result.asdict() for result in eval_results]
    # ensure json serializable
    for result in results:
        result['true_document_ids'] = list(result['true_document_ids'])
        result['retrieved_document_ids'] = list(result['retrieved_document_ids'])
    with open(file_path, 'w') as f:
        json.dump(results, f, indent=4)

    return eval_results, tagged_group

root_dir = 'aurp'
closed_domain = True
results, metric = get_eval_results( 'short', root_dir, file_path=f'{root_dir}/eval_results/results_short_balanced.json')

print('Baseline Accuracy: ', metric.get_accuracy())
print('Accuracy (Remove LLM Errors): ', metric.get_accuracy(for_retrieval=True))
print('Removing Gap Examples: ', metric.get_robustness())
print('Removing LLM Errors & Gap Examples: ', metric.get_robustness(for_retrieval=True))
```


## Common Questions
* What if I want to scale the generations?
You can reuse the code from the initial generation. ONLY TWO changes are required: 1) using `from_file` for object creation; 2) setting a new `num_generations`. Below is an example:
```python
linguistic_attr = "long"
file_path = f'spider/TextTemplateGenerator/{linguistic_attr}.json'
text_template_generator = TextTemplateGenerator.from_file(file_path=file_path, attrs=linguistic_attr, llm=llm) # 1st change
sql_to_text_templates = text_template_generator.generate_batch(sql_templates, verbose=True, num_generations=10, override=False)
 # 2st change
text_template_generator.save(file_path=file_path, override=True)
```
* How to add new content to `verbalizer`?