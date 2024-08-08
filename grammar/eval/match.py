import json
from grammar.generator import Generator
from grammar.llm import AnyOpenAILLM

# def check_qa_answer(query, true_answer, gpt_response, eval_model=gpt4_llm):
#     prompt = """Evaluate the accuracy of the given response in relation to the true answer for the specified query. After evaluating, provide a judgement as either "Correct" or "Incorrect" based on whether the ##Given Response## accurately matches the ##True Answer##.

#     ##Query##: {}
#     ##True Answer##: {}
#     ##Given Response##: {}
#     ##Judgement##:
#     """.format(query, json.dumps(true_answer), gpt_response)
#     return eval_model(prompt)
class SemanticsMatch(Generator):
    verbalizer = {
        "short": "",
        "long": ""
    }
    def __init__(self, llm=None, verbalize_attrs=''):
        llm = llm or AnyOpenAILLM(model_name = "gpt4-short")
        llm.temperature = 0
        super().__init__( llm=llm, verbalize_attrs=verbalize_attrs)

    def _generate(self, query_truth_generation:tuple, num_generations=None, verbose=False):
        print('LLM is generating... for the key: ', str(query_truth_generation))
        query, true_answer, gpt_response = query_truth_generation
        prompt = """Evaluate the accuracy of the given response in relation to the true answer for the specified query. After evaluating, provide a judgement as either "Correct" or "Incorrect" based on whether the ##Given Response## accurately matches the ##True Answer##.

        ##Query##: {}
        ##True Answer##: {}
        ##Given Response##: {}
        ##Judgement##:
        """.format(query, json.dumps(true_answer), gpt_response)
        return [self.llm(prompt)]



        