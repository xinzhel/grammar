import json
from copy import deepcopy
from typing import Union, List, Dict, Tuple
from functools import lru_cache
class Metric:
    def __init__(self, results):
        self.results = results
        self.results_for_retrieval = self.correct_results_for_retrieval()

    def tag_competency_groups(self, include_all_domains=False):
        """ Tag  competency groups.
        Technically, they should not be specific to the domain.
        Instead, we should include all domains, making sure that tags for each domain align with the tags for other domains. 
        In other words, Examples in group 1 for one domain are semantically identical to examples in group 1 for another domain.
        """
        valid_tags_dict = {}
        valid_tags_across_domains = []
        for domain_name in self.results:
            valid_tags_for_each_domain = []
            for result in self.results[domain_name]:
                if result['judgement'] == 'Correct':
                    valid_tags_for_each_domain.append(result['query_tag'])
                    valid_tags_across_domains.append(result['query_tag'])

            valid_tags_dict[domain_name] = set(valid_tags_for_each_domain)
        if include_all_domains:
            valid_tags_dict["include_all_domains"] = set(valid_tags_across_domains)
        return valid_tags_dict
    
    def tag_gap_groups(self):
        """ Groups whose tags are not in competency groups but in all tags
        """
        competent_tags = self.tag_competency_groups(include_all_domains=True)['include_all_domains']
        all_tags_across_domains = self.get_all_tags(include_all_domains=True)["include_all_domains"]
        gap_tags = all_tags_across_domains - competent_tags
        return gap_tags
    
    @property
    @lru_cache(maxsize=None)
    def tag_to_examples(self):
        """ Tag to examples
        """
        tag_to_examples = {}
        for domain_name in self.results:
            for result in self.results[domain_name]:
                tag = result['query_tag']
                if tag not in tag_to_examples:
                    tag_to_examples[tag] = []
                tag_to_examples[tag].append(result)
        return tag_to_examples
    
    def tag_non_robust_groups(self):
        """ Tag non-robust groups or potentially competent groups where there exists at least one example that is not correct and at least one example is correct.
        """
        competent_tags = self.tag_competency_groups(include_all_domains=True)['include_all_domains'] # at least one example is correct
        tag_to_examples = self.tag_to_examples
        non_robust_tags = set()
        for tag in competent_tags:
            examples = tag_to_examples[tag]
            for example in examples:
                if example['judgement'] != 'Correct': # at least one example is not correct
                    non_robust_tags.add(tag)   
                    break
        return non_robust_tags
    
    def get_incorrect_queries_in_non_robust_group(self):
        """ Get incorrect examples in non-robust groups
        """
        non_robust_tags = self.tag_non_robust_groups()
        tag_to_examples = self.tag_to_examples
        incorrect_examples = {}
        for tag in non_robust_tags:
            examples = tag_to_examples[tag]
            incorrect_examples[tag] = [example['query'] for example in examples if example['judgement'] != 'Correct']
        return incorrect_examples
    
    def get_correct_queries(self):
        """ Get correct examples
        """
        tag_to_examples = self.tag_to_examples
        correct_examples = {}
        for tag in tag_to_examples:
            examples = tag_to_examples[tag]
            correct_examples[tag] = [example['query'] for example in examples if example['judgement'] == 'Correct']
        return correct_examples
    
    def get_correct_incorrect_examples(self):
        """ Get correct and incorrect examples
        """
        incorrect_examples = self.get_incorrect_queries_in_non_robust_group()
        correct_examples = self.get_correct_queries()

        incorrect_vs_correct_examples = {}
        for tag in incorrect_examples:
            for example in incorrect_examples[tag]:
                
                incorrect_vs_correct_examples[example] = correct_examples[tag]
        return incorrect_vs_correct_examples

    
    def get_all_tags(self, include_all_domains=False):
        tags_dict = {}
        all_tags_across_domains = []
        for entity_with_spec in self.results:
            tags = []
            for result in self.results[entity_with_spec]:
                tags.append(result['query_tag'])
                all_tags_across_domains.append(result['query_tag'])

            tags_dict[entity_with_spec] = set(tags)
        if include_all_domains:
            tags_dict["include_all_domains"] = set(all_tags_across_domains)
        return tags_dict
    
    def get_best_case_accuracy(self):
        results = self.results
        best_case_accuracy = {}
        competency_group_tags = self.tag_potentially_competency_groups()
        all_group_tags = self.get_all_tags()
        for entity_with_spec in results:
            try:
                best_case_accuracy[entity_with_spec] = len(competency_group_tags[entity_with_spec])/len(all_group_tags[entity_with_spec])
            except:
                Exception()
    
        return best_case_accuracy
    
    def get_accuracy(self, for_retrieval=False, average_for_each_domain=False, average_all=False):
        """ Calculate accuracy
        """
        if for_retrieval:
            results = self.results_for_retrieval
        else:        
            results = self.results
        if average_all:
            assert not average_for_each_domain
        if average_for_each_domain:
            # calculate accuracy
            accuracy = {}
            for domain_name in results:
                correct = 0
                for result in results[domain_name]:
                    if result['judgement'] == 'Correct':
                        correct += 1
                try:
                    accuracy[domain_name] = correct/len(results[domain_name])
                except:
                    Exception()
        elif average_all:
            correct = 0
            total = 0
            for domain_name in results:
                for result in results[domain_name]:
                    if result['judgement'] == 'Correct':
                        correct += 1
                    total += 1
            accuracy = correct/total
        else:
            raise Exception("Please Provide Aggregation method")
        
        return accuracy

    def get_robustness(self, for_retrieval=False, average_for_each_domain=False, average_all=False, include_all_domains_for_tagging=True):
        """ Calculate robustness
        """
        if for_retrieval:
            results = self.results_for_retrieval
        else:        
            results = self.results
        competency_group_tags = self.tag_competency_groups(include_all_domains=include_all_domains_for_tagging)
        if average_for_each_domain:
            
            robustness = {}
            for domain_name in results:
                correct = 0
                total = 0
                for result in results[domain_name]:
                    if include_all_domains_for_tagging:
                        potentially_competency_group_tags = competency_group_tags["include_all_domains"]
                    else:
                        potentially_competency_group_tags = competency_group_tags[domain_name]
                    if result['query_tag'] in potentially_competency_group_tags:
                        if result['judgement'] == 'Correct':
                            correct += 1
                        total += 1
                try:
                    robustness[domain_name] = correct/total
                except:
                    Exception()
        elif average_all:
            correct = 0
            total = 0
            for domain_name in results:
                for result in results[domain_name]:
                    if result['query_tag'] in competency_group_tags[domain_name]:
                        if result['judgement'] == 'Correct':
                            correct += 1
                    total += 1
            robustness = correct/total
        else:
            raise Exception("Please Provide Aggregation method")
        
        return robustness
    
    def get_num_total_correct(self) -> Dict[str, Dict[str, Tuple[int, int]]]:
        """  Returns the number of total, correct answers for each query logic group

        Returns:
            dict: {domain_name: {tag: (num_correct, num_total)}}
        """
        def get_num_total_correct_for_each_qlogic(results, tag):
            # can be used to calculate in-group accuracy
            num_correct = 0
            num_total = 0
            for result in results:
                if result['query_tag'] == tag:
                    if result['judgement'] == 'Correct':
                        num_correct += 1
                    num_total += 1
            return num_correct, num_total
        
        domain_to_num_total_correct = {domain_name: None for domain_name in self.results}
        domain_to_tags_dict = self.get_all_tags()
        for domain in domain_to_tags_dict:
            all_tags = domain_to_tags_dict[domain]
            all_results = self.results[domain]

            tag_to_nums_dict = {tag: get_num_total_correct_for_each_qlogic(all_results, tag) for tag in all_tags}
        
            domain_to_num_total_correct[domain] = tag_to_nums_dict
            
        return domain_to_num_total_correct

    def correct_retrieval_result(self, example):
        """ Correct retrieval result by comparing the document index with the correctly predicted document index."""
        # assert example['query_tag'] in self.tag_non_robust_groups()
        example = deepcopy(example)
        examples = self.tag_to_examples[example['query_tag']]
        examples_with_correct_prediction = [example for example in examples if example['judgement'] == 'Correct']
        for example_correct in examples_with_correct_prediction:
            if example_correct['top3'][0]['id'] == example['top3'][0]['id']: # this is not the retrieval's fault
                example['judgement'] = 'Correct'
        return example

    def correct_results_for_retrieval(self):
        """ False predictions may be caused by the LM. 
        So, we correct those examples that were successfully retrieved but wrongly predicted by LM."""
        non_robust_tags = self.tag_non_robust_groups()
        results_for_retrieval = { domain_name: [] for domain_name in self.results.keys() }
        filtered_results_for_lm = {domain_name: [] for domain_name in self.results.keys()}
        for domain_name in self.results:
            for example in self.results[domain_name]:
                if example['query_tag'] in non_robust_tags and example['judgement'] != 'Correct':
                    corrected_example = self.correct_retrieval_result(example)
                    results_for_retrieval[domain_name].append(corrected_example)
                else:
                    results_for_retrieval[domain_name].append(example)

        return results_for_retrieval

    def print_data_stat(self):
        """ Print data statistics
        """
        domain_to_num_total_correct = self.get_num_total_correct()
        gap_tags = self.tag_gap_groups()
        for domain_name in self.results:
            print("======", domain_name, "======")
            num_toal_correct_for_each_group: Dict[str, Tuple[int, int]] = domain_to_num_total_correct[domain_name]
            # ensure that gap tags are in the domain-specific cluster
            all_tags_for_domain = list(num_toal_correct_for_each_group.keys())
            gap_tags_for_domain = [tag for tag in all_tags_for_domain if tag in gap_tags]
            # print data statistics
            print_data_stat_by_groups(num_toal_correct_for_each_group, gap_tags_for_domain)
            print("\n")

    # def prepare_for_model_in_loop_correction(self):
    #     """ Prepare retrieval results for model in loop correction
    #     """
    #     result = self.results_for_retrieval
                

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