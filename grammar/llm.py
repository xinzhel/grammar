import os
import openai
from openai import OpenAI, AzureOpenAI
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ['AZURE_OPENAI_API_KEY'],  
    api_version=os.environ['AZURE_OPENAI_API_VERSION'], 
)
import numpy as np
import json
from typing import Optional, Union, List
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
class GPTUsageRecord:
    def __init__(self):
        self.episode_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    # update the total usage of the model
    def write_usage(self, model_name):
        file = model_name+'_usage.json'
        # if exist
        if os.path.exists(file):
            with open(file, 'r') as f:
                previous_usage = json.load(f)
        else:
            previous_usage = {'total': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}, 'recent': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}}


        # write gpt usage record to json
        for key in previous_usage['total'].keys():
            previous_usage['total'][key] += self.episode_usage[key]

        for key in previous_usage['recent'].keys():
            previous_usage['recent'][key] = self.episode_usage[key]


        with open(model_name+'_usage.json', 'w') as f:
            json.dump(previous_usage, f)


class AnyOpenAILLM:

    def __init__(self, model_name:str='gpt-3.5-turbo', max_tokens:int = 2048, temperature=1):
        self.model_name = model_name
        self.temperature = temperature # < 1.0: more random
        self.max_tokens = max_tokens
        self.gpt_usage_record =  GPTUsageRecord()
        API_KEY = os.getenv("AZURE_OPENAI_API_KEY", None)
        if API_KEY is None:
            raise ValueError("OPENAI_API_KEY not set, please run `export OPENAI_API_KEY=<your key>` to ser it")
        else:
            openai.api_key = API_KEY
    
    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(5))
    def __call__(self, usr_msg, system_msg='', 
                 history: List[str]=[], 
                 temperature=None, 
                 max_tokens=None, 
                 top_p: float = 1.0, 
                 num_return_sequences: int = 1,
                 stop: Optional[str] = None): 
        if temperature is None:
            temperature = self.temperature

        if max_tokens is None:
            max_tokens = self.max_tokens

        if not history:
            messages= [{"role": "system", "content": system_msg}, 
                      {"role": "user", "content": usr_msg} ]
        else:
            messages= [{"role": "system", "content": system_msg}]
            # loop every two messages in history
            for i in range(0, len(history), 2):
                messages.append({"role": "user", "content": history[i]})
                messages.append({"role": "assistant", "content": history[i+1]})
            messages.append({"role": "user", "content": usr_msg})

        completion = client.chat.completions.create(
            model=self.model_name,
            messages=messages ,
            temperature= temperature, 
            max_tokens=self.max_tokens,
            top_p=top_p,  # top_p should be a float between 0 and 1
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop,
            n=num_return_sequences
        )
        # update the usage record
        for key in self.gpt_usage_record.episode_usage.keys():
            try:
                self.gpt_usage_record.episode_usage[key] += completion.usage.to_dict()[key]
            except:
                pass
        return completion.choices[0].message.content
        
    
    def write_usage(self):
        self.gpt_usage_record.write_usage(self.model_name)

    def batch_generate(self, messages_list):

        responses = [
            self.__call__(messages)
            for messages in messages_list
        ]

        return responses
    
    def async_run(self):
        # TODO: the async version is adapted from https://gist.github.com/neubig/80de662fb3e225c18172ec218be4917a
        raise NotImplementedError
      
    
    def get_next_token_logits(self,
                              prompt: Union[str, list[str]],
                              candidates: Union[list[str], list[list[str]]],
                              **kwargs) -> list[np.ndarray]:
        prompt = ""
        return [[0.7, 0.3]] # for yes and no

    def get_loglikelihood(self,
                    prompt: Union[str, list[str]],
                    **kwargs) -> list[np.ndarray]:
        
        raise NotImplementedError("GPTCompletionModel does not support get_log_prob")
    

class OpenAILLMAgent(AnyOpenAILLM):
    def __init__(self, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
    
    def __call__(self, usr_msg, history: List[str]=[], **kwargs):
        system_msg = self.role
        return super().__call__(usr_msg, system_msg, history, **kwargs)


# singleton for general purposes 
chatgpt_llm = AnyOpenAILLM(model_name = "chatgpt-4k")
gpt4_llm = AnyOpenAILLM(model_name = "gpt4-short")  # 

company_name = '' #"Aurecon"
role = f"""I am an AI assistant for {company_name}, a Design, Engineering, and Advisory company. My task is to assist {company_name} employees in finding factual, grounded responses to their queries. """
gen_model = OpenAILLMAgent(model_name = "chatgpt-16k", role=role)

# if __name__ == "__main__":
#     chat = OpenAIChat(model_name='llama-2-7b-chat-hf')

#     predictions = asyncio.run(chat.async_run(
#         messages_list=[
#             [{"role": "user", "content": "show either 'ab' or '['a']'. Do not do anything else."}],
#         ] * 20,
#         expected_type=List,
#     ))

#     print(predictions)
    # Usage
    # embed = OpenAIEmbed()
    # batch = ["string1", "string2", "string3", "string4", "string5", "string6", "string7", "string8", "string9", "string10"]  # Your batch of strings
    # embeddings = asyncio.run(embed.process_batch(batch, retry=3))
    # for embedding in embeddings:
    #     print(embedding["data"][0]["embedding"])