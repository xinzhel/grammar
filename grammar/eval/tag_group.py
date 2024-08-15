# from grammar.eval.metric import MetricForHypothesis
import json
from copy import deepcopy
from typing import Union, List, Dict, Tuple
from functools import lru_cache
from grammar.eval.result import Result

class TaggedGroup():
    def __init__(self, results: List[Result]):
        self.results = results

    @property
    def competent_tags(self):
        return set([result.query_tag for result in self.results if result.judgement == 'Correct'])

    @property
    def gap_tags(self):
        return set(self.all_tags) - set(self.competent_tags)
    
    @property
    @lru_cache(maxsize=None)
    def tag_to_examples(self):
        """ Tag to examples
        """
        tag_to_examples = {}
        for result in self.results:
            tag = result.query_tag
            if tag not in tag_to_examples:
                tag_to_examples[tag] = []
            tag_to_examples[tag].append(result)
        return tag_to_examples
    
    @property
    def non_robust_tags(self):
        """ Tag non-robust groups or potentially competent groups where there exists at least one example that is not correct and at least one example is correct.
        """
        
        tag_to_examples = self.tag_to_examples
        non_robust_tags = set()
        for tag in self.competent_tags:
            examples = tag_to_examples[tag]
            for example in examples:
                if example.judgement != 'Correct': # at least one example is not correct
                    non_robust_tags.add(tag)   
                    break
        return non_robust_tags
    
    @property
    def all_tags(self):
        tags = [result.query_tag for result in self.results]
        return set(tags)
    
    def get_incorrect_queries_in_non_robust_group(self):
        return {tag: [result.query for result in results if result.judgement != 'Correct'] for tag, results in self.non_robust_tags.items()}
    
    def get_correct_queries(self):
        return {tag: [result.query for result in results if result.judgement == 'Correct'] for tag, results in self.tag_to_examples.items()}
    
    def get_correct_incorrect_examples(self):
        incorrect_examples = self.get_incorrect_queries_in_non_robust_group()
        correct_examples = self.get_correct_queries()
        return {example: correct_examples[tag] for tag in incorrect_examples for example in incorrect_examples[tag]}
        
    def get_knowledge_accuracy(self):
        """ The accuracy derived purely from the system's knowledge base, disregarding issues related to system robustness or adaptability."""
        return len(self.competent_tags)/len(self.all_tags)
    
    def get_accuracy(self, results=None, for_retrieval=False, average_for_each_domain=False, average_all=False):
        num_correct = 0
        if results is None:
            results = self.results
            
        judgement_key = 'retrieval_judgement' if for_retrieval else 'judgement'
        for result in results:
            if  getattr(result, judgement_key) == 'Correct' or getattr(result, judgement_key) == 1:
                num_correct += 1
        return num_correct/len(results)

    def get_robustness(self, for_retrieval=False):
        results_for_competent_tags = [result for result in self.results if result.query_tag in self.competent_tags]
        return self.get_accuracy(results=results_for_competent_tags, for_retrieval=for_retrieval)

    def get_num_total_correct(self) ->  Dict[str, Tuple[int, int]]:
        """  Returns the number of total, correct answers for each query logic group

        Returns:
            dict:  {tag: (num_correct, num_total)}
        """
        def get_num_total_correct_for_each_qlogic(results, tag):
            # can be used to calculate in-group accuracy
            num_correct = 0
            num_total = 0
            for result in results:
                if result.query_tag == tag:
                    if result.judgement == 'Correct':
                        num_correct += 1
                    num_total += 1
            return num_correct, num_total
        return {tag: get_num_total_correct_for_each_qlogic(self.results, tag) for tag in self.all_tags}

class MetricsForHypothesis():
    def __init__(self, robust_groups: List[Dict], non_robust_groups: List[Dict]):
        self.tagged_group_robust = TaggedGroup(robust_groups) 
        self.tagged_group_non_robust = TaggedGroup(non_robust_groups)

    def mutual_gap_tags(self):
        return set.intersection(self.tagged_group_robust.gap_tags, self.tagged_group_non_robust.gap_tags)
    
    def print_data_stat(self):
        """ Print data statistics
        """
        for domain_name, metric in self.tagged_group.items():
            print("======", domain_name, "======")
            num_toal_correct_for_each_group: Dict[str, Tuple[int, int]] = metric.get_num_total_correct()
            # ensure that gap tags are in the domain-specific cluster
            all_tags_for_domain = list(num_toal_correct_for_each_group.keys())
            gap_tags_for_domain = [tag for tag in all_tags_for_domain if tag in self.mutual_gap_tags]
            # print data statistics
            print_data_stat_by_groups(num_toal_correct_for_each_group, gap_tags_for_domain)
            print("\n")

    # def get_correct_retrieved_context(self):

    #     self.tag_to_examples

    #     tag_to_retrieved_context_dict = {}
    #     for domain_name in self.results_for_retrieval:
    #         tag_to_retrieved_context_dict[domain_name] = {}
    #         for tag in all_tags[domain_name]:
    #             tag_to_retrieved_context_dict[domain_name][tag] = []
    #             for result in queries_answer_pairs_dict[domain_name]:
    #                 if result['query_tag'] == tag and result['judgement'] == 'Correct':
    #                     retrieved_documents = result['retrieved_documents'].replace("### Question:\n"+result['query'], '')
    #                     query = result['query']
    #                     answer = tuple(result['answer'])
    #                     tag_to_retrieved_context_dict[domain_name][tag].append((query, answer, retrieved_documents))
        
    #     return tag_to_retrieved_context_dict


def print_data_stat_by_groups(group_details: Dict[str, Tuple[int, int]], tags_for_gap_groups: List ):
    """ Print data statistics by groups

    Args:
        group_details (Dict[str, Tuple[int, int]] ): Dictionary containing (correct, total) for each group
        tags_for_gap_groups (List): List of indices for gap groups. Gap groups have to be identified by considering both hypothesis and counter-hypothesis clusters.
    """
    
    # gap groups
    num_gap_groups = len(tags_for_gap_groups)
    num_gap_examples = sum([group_details[tag][1] for tag in tags_for_gap_groups])
    print(f"Gap groups: {num_gap_groups} Groups with {num_gap_examples} Examples")

    # non-gap groups
    all_tags = list(group_details.keys())
    tags_no_gap_groups = [tag for tag in all_tags if tag not in tags_for_gap_groups]
    details_no_gap_groups = [group_details[tag] for tag in tags_no_gap_groups]

    # robust groups
    num_robust_groups = len([1 for correct, total in details_no_gap_groups if total==correct and correct!=0])
    num_robust_examples = sum([total for correct, total in details_no_gap_groups if total==correct and correct!=0]) 
    num_robust_correct_examples = sum([correct for correct, total in details_no_gap_groups if total==correct and correct!=0])
    print(f"Roubst groups (# of groups/examples/correct examples): {num_robust_groups} / {num_robust_examples} / {num_robust_correct_examples}")

    # non-robust groups
    num_non_robust_groups = len([1 for correct, total in details_no_gap_groups if correct!=0 and correct!=total])
    num_non_robust_examples = sum([total for correct, total in details_no_gap_groups if correct!=0 and correct!=total])
    num_non_robust_correct_examples = sum([correct for correct, total in details_no_gap_groups if correct!=0 and correct!=total])
    print(f"Non-robust groups (# of groups/examples/correct examples): {num_non_robust_groups} / {num_non_robust_examples} / {num_non_robust_correct_examples}")

    # total
    total_examples = sum([total for correct, total in group_details.values()])
    print(f"Total number of groups: {len(group_details)} groups with {total_examples} Examples")
    num_correct_examples = sum([correct for correct, total in group_details.values()])
    assert num_correct_examples ==  num_non_robust_correct_examples + num_robust_correct_examples

    # accuracy and robustness
    accuracy = num_correct_examples / total_examples
    robustness = (num_robust_examples+num_non_robust_correct_examples) / (num_robust_examples + num_non_robust_examples)
    print("\tAccuracy:", round(accuracy, 2), f'({num_correct_examples} / {total_examples})')
    print("\tRobustness:", round(robustness, 2), f'({num_robust_examples+num_non_robust_correct_examples} / {num_robust_examples + num_non_robust_examples})')


def print_data_stat_by_groups_naive(group_details: List, print_details=False ):
    """ Print data statistics by groups

    Args:
        group_details (List): List of tuples containing (correct, total) for each group
        print_details (bool, optional): Print details. Defaults to False.
    """
    tags = list(range(len(group_details)))

    if print_details:
        print(f"Index for Query Logic: (Correct, Total) in each group:")
        for i, (correct, total) in zip(tags, group_details):
            # tags_for_gap_groups
            group_type = ''
            if correct == 0:
                group_type = " => gap group" 
            elif correct==total:
                group_type = '' #" => Robust Group"
            else:
                group_type = "=> Non-robust Group"
            print(f"\tGroup {i}: ({correct}, {total}){group_type}")
    else:
        # gap groups
        num_gap_groups = len([total for correct, total in group_details if correct == 0])
        num_gap_examples = sum([total for correct, total in group_details if correct == 0])
        print(f"Gap groups: {num_gap_groups} Groups with {num_gap_examples} Examples")

        # robust groups
        num_robust_groups = len([1 for correct, total in group_details if total==correct and correct!=0])
        num_robust_examples = sum([total for correct, total in group_details if total==correct and correct!=0]) 
        num_robust_correct_examples = sum([correct for correct, total in group_details if total==correct and correct!=0])
        print(f"Roubst groups: {num_robust_groups} Groups with {num_robust_examples} Examples")

        # non-robust groups
        num_non_robust_groups = len([1 for correct, total in group_details if correct!=0 and correct!=total])
        num_non_robust_examples = sum([total for correct, total in group_details if correct!=0 and correct!=total])
        num_non_robust_correct_examples = sum([correct for correct, total in group_details if correct!=0 and correct!=total])
        print(f"Non-robust groups: {num_non_robust_groups} Groups with {num_non_robust_examples} Examples")

        # total
        total_examples = sum([total for correct, total in group_details])
        print(f"Total number of groups: {len(group_details)} groups with {total_examples} Examples")
        num_correct_examples = sum([correct for correct, total in group_details])
        assert num_correct_examples ==  num_non_robust_correct_examples + num_robust_correct_examples

        # accuracy and robustness
        accuracy = num_correct_examples / total_examples
        robustness = (num_robust_examples+num_non_robust_correct_examples) / (num_robust_examples + num_non_robust_examples)
        print("\tAccuracy:", round(accuracy, 2), f'({num_correct_examples} / {total_examples})')
        print("\tRobustness:", round(robustness, 2), f'({num_robust_examples+num_non_robust_correct_examples} / {num_robust_examples + num_non_robust_examples})')