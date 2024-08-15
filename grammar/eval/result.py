import json
import sys
sys.path.append('..')
from grammar.eval.match import SemanticsMatch
# import dataclass
from dataclasses import dataclass, asdict
from typing import Optional, List

@dataclass
class Result:
    query: str
    answer: str
    gpt_response: str
    query_tag: Optional[int] = None # for semantics group
    judgement: Optional[str] = None

    def asdict(self):
        return asdict(self)

    def judge_response(self, eval_model: SemanticsMatch):
        if self.judgement is not None:
            return
        
        self.judgement = eval_model.generate((self.query, self.answer, self.gpt_response), verbose=True)[0]

@dataclass
class RAGResult(Result):
    """A dataclass to store the result of RAG result and evaluation"""
    true_document_ids: Optional[List[int]] = None
    retrieved_document_ids: Optional[List[int]] = None
    retrieval_db_judgement: Optional[int] = None
    retrieval_judgement: Optional[int] = None
    closed_domain: Optional[bool] = None

    def judge_rag_response(self, eval_model: SemanticsMatch ):
        """ Judge the RAG result via semantics match: comparing the true answer with the gpt response."""
        if self.closed_domain and self.retrieval_judgement == 0:
            self.judgement = "Incorrect"
        else:
            self.judge_response(eval_model)
        

    def judge_retrieval_response(self, tagged_group, method='context_comparison'):
        """ Judge the retrieval result via context comparsion: comparing the document index with the correctly predicted document index."""
        if self.closed_domain and self.judgement == 'Correct':
            self.retrieval_judgement = 1
            return
        
        if method == 'use_exist':
            assert self.retrieval_judgement in [0, 1], "The `retrieval_judgement` should be provided"
        elif method == "use_ground_truth":
            assert self.true_document_ids is not None, "The `true_document_ids` should be provided"
            type_element = type(self.true_document_ids[0])
            self.retrieval_judgement = 1 if set(self.true_document_ids) == set([type_element(r) for r in self.retrieved_document_ids]) else 0
        elif method == 'context_comparison':
            assert self.query_tag in tagged_group.non_robust_tags, "This context-comparison method is only for an example in non-robust groups"
            examples = tagged_group.tag_to_examples[self.query_tag]
            examples_with_correct_prediction = [example for example in examples if example.judgement == 'Correct']
            for example_correct in examples_with_correct_prediction:
                if example_correct.retrieved_documents_id == self.retrieved_documents_id: # this is not the retrieval's fault
                    self.retrieval_judgement = 1
        else:
            # TODO
            raise Exception("So far, we only support the following method: `use_ground_truth`, `use_exist`, `context_comparison`")

