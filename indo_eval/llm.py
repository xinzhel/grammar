import openai
import json
import os
from typing import List
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

    def __init__(self, *args, **kwargs):
        self.model_name = kwargs.get('model_name', 'gpt-3.5-turbo') 
        self.temperature = kwargs.get('temperature', 1) # < 1.0: more random
        self.gpt_usage_record =  GPTUsageRecord()
        
    def __call__(self, usr_msg, system_msg='', history: List[str]=[], **kwargs):    
        temperature = kwargs.get('temperature', self.temperature)
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

        completion = openai.ChatCompletion.create(
            model=self.model_name,
            deployment_id=self.model_name,
            messages=messages ,
            temperature=self.temperature, 
            # max_tokens=150,
            top_p=1.0,  # top_p should be a float between 0 and 1
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        # update the usage record
        for key in self.gpt_usage_record.episode_usage.keys():
            try:
                self.gpt_usage_record.episode_usage[key] += completion.usage.to_dict()[key]
            except:
                pass
        try:
            return completion.choices[0].message['content']
        except:
            return "[The LLM does not generate response.]"
    
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