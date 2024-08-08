import os
import json
from typing import List, Union, Dict, Set
from abc import ABC, abstractmethod
from langchain.prompts import PromptTemplate
from grammar import llm

class Generator(ABC):
    # Class-level attribute placeholders, expected to be overridden in subclasses
    verbalizer: Dict[str, str] = {}
    system_msg_tpl:PromptTemplate  = None 
    instance_msg_tpl:PromptTemplate = None
    only_cache_default:bool=False

    def __init__(self, verbalize_attrs: Union[str, List[str]]=[], llm=None) -> None:
        # system-level instantiation
        self._system_msg_attrs = [verbalize_attrs] if isinstance(verbalize_attrs, str) else verbalize_attrs        
        for attr in self._system_msg_attrs:
            if attr not in self.verbalizer:
                raise ValueError(f"Invalid attribute: {attr}. The attribute should be one of {self.verbalizer.keys()}")

        # llm
        self.llm = llm.gpt4_llm if llm is None else llm

        # cache
        if self.only_cache_default:
            self.cache_generations = []
        else:
            # avoid re-generating with the same prompt
            self.cache_generations = {}
            
    @classmethod
    def from_file(cls, file_path:str=None, root_dir: str='.', **kwargs):
        """ Instantiate the object from a file so that we can avoid re-generating the text."""
        generator = cls(**kwargs)

        # load the cache
        file_path = generator._default_save_path(root_dir) if file_path is None else file_path
        if os.path.exists(file_path):
            with open(file_path, 'r') as fp:
                if generator.only_cache_default:
                    generator.cache_generations = load_txt_lines(file_path)
                else:
                    cache_generations = json.load(fp)
                    # convert the keys to the original type
                    try:
                        generator.cache_generations =  {eval(k): v for k, v in cache_generations.items()}
                    except:
                        generator.cache_generations = cache_generations
        return generator
    
    def save(self, file_path:str=None, root_dir:str='.', override=False):
        file_path = self._default_save_path(root_dir=root_dir) if file_path is None else file_path
        if os.path.exists(file_path):
            if not override:
                raise ValueError(f"File {file_path} already exists.")
            else:
                os.remove(file_path)
        with open(file_path, 'w') as fp:
            if self.only_cache_default:
                assert isinstance(self.cache_generations, list), "The `cache_generations` should be a list."
                fp.write('\n'.join([v for k, v in self.cache_generations.items()]))
            else:
                stringified_keys = {str(k): v for k, v in self.cache_generations.items()}
                json.dump(stringified_keys, fp)
            
    
    def _default_save_path(self, root_dir: str='.'):
        if not self._system_msg_attrs:
            return os.path.join(root_dir, f"{self.__class__.__name__}/default.json")
        return os.path.join(root_dir, f"{self.__class__.__name__}/{'_'.join(self._system_msg_attrs)}.json")
    
    @abstractmethod 
    def _generate(self, k: Union[str, tuple[str]], num_generations=None, verbose=False) -> Union[str, List[str]]:
        pass

    def check_cache(self, k: Union[str, tuple[str]]):
        assert k is None or isinstance(k, (str, list, tuple)), "The input `k` should be a string, a list, a tuple or None."
        k = tuple(k) if isinstance(k, list) else k
        return k in self.cache_generations
    
    def generate(self, k: Union[str, tuple[str]]=None, num_generations=None, verbose=False, override=False): 
        
        if self.only_cache_default:
            assert k is None, "The `k` should not be given when `only_cache_default` is True."
            if not self.cache_generations:
                self.cache_generations = self._generate(k, verbose=verbose)
            return self.cache_generations
 
        # Case 1: exists in cache and no need to override
        if self.check_cache(k) and not override:
            exist_generations = self.cache_generations[k]
            num_generations =  num_generations if num_generations is not None else len(exist_generations)
            
            # Case 1.1: no need to generate more
            if len(exist_generations) >= num_generations:
                if verbose:
                    print(f"The {len(exist_generations)} generations for the input `k` exist in `cache_generations`! No need to generate more.")
                return exist_generations[:num_generations+1]
            # Case 1.2: generate more
            new_generations = self._generate(k, num_generations=num_generations-len(exist_generations), verbose=verbose)
            self.cache_generations[k].extend(new_generations)
            if verbose:
                print(f"{len(new_generations)} new generations have been cached in `cache_generations`!")
        else:
            # Case 2: not in cache; 
            # Case 3: override
            self.cache_generations[k] = self._generate(k, num_generations=num_generations, verbose=verbose)
        return self.cache_generations[k]

    def explain_cache(self):
        pass

    def generate_batch(self, keys:Union[List[str], List[List[str]]], num_generations:int=None, verbose=False, override=False) -> Dict[str, Union[str, List[str]]]:
        if self.only_cache_default:
            raise ValueError("The method `generate_batch` is not supported when `only_cache_default` is True.")
        return {k: self.generate(k, verbose=verbose, override=override, num_generations=num_generations) for k in keys}
    
def load_txt_lines(file_path):
    with open(file_path, 'r') as file:
        texts = file.readlines()
    return [x.strip() for x in texts]
        


