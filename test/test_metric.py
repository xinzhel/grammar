def robustness_accuracy_stratified():
    print("\n")
    print("~~~~~Stratified Groups~~~~~")
    # Non-robust: 12 examples in gap groups, 12 in non-gap groups
    fake_cluster = [
        (1, 3),  # Group 0
        (2, 3),  # Group 1
        (3, 3),  # Group 2
        (2, 3),  # Group 3
        (0, 3),  # Group 4 (gap group)
        (0, 3),  # Group 5 (gap group)
        (0, 3),  # Group 6 (gap group)
        (0, 3)   # Group 7 (gap group)
    ]
    # print("\tAccuracy:", round(8/24, 2), '(8 / 24)')
    # print("\tRobustness:", round(8/12, 2), '(8 / 12)')
    # Robust
    # fake_cluster =[
    #     (3, 3), 
    #     (2, 3), 
    #     (3, 3), 
    #     (3, 3), 
    #     (0, 3), # gap group
    #     (0, 3), # gap group
    #     (0, 3), # gap group
    #     (0, 3)  # gap group
    # ]
    # print("\tAccuracy:", round(11/24, 2), '(11 / 24)')
    # print("\tRobustness:", round(11/12, 2), '(11 / 12)')
    print_cluster(fake_cluster)

    
robustness_accuracy_stratified()

def robustness_accuracy_unbalanced():
    print("\n")
    print("~~~~~Unbalanced Groups~~~~~")
    print("Non-robust: (6 examples in gap group, 12 in non-gap group)")
    print_cluster([
        (1, 3),  # Group 0
        (2, 3),  # Group 1
        (3, 3),  # Group 2
        (2, 3),  # Group 3
        (0, 3),  # Group 4 (gap group)
        (0, 3)   # Group 5 (gap group)
    ])
    print("Non-robust clusters (long queries)")
    print("\tAccuracy:", round(8/18, 2), '(8 / 18)')
    print("\tRobustness:", round(8/12, 2), '(8 / 12)')

    print("\n")
    print("Robust Cluster (short queries)")
    print("Robust: (12 examples in gap group, 12 in non-gap group)")
    print_cluster([
        (3, 3), 
        (2, 3), 
        (3, 3), 
        (3, 3), 
        (0, 3), # gap group
        (0, 3),  # gap group
        (0, 3), # gap group
        (0, 3)  # gap group
    ])
    
    print("\tAccuracy:", round(11/24, 2), '(11 / 24)')
    print("\tRobustness:", round(11/12, 2), '(11 / 12)')