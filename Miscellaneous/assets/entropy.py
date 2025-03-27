import math
from collections import Counter

# Function to calculate Shannon entropy
def calculate_entropy(fragment):
    # Count the frequency of each character
    freq = Counter(fragment)
    # Calculate probabilities for each character
    probabilities = [count / len(fragment) for count in freq.values()]
    # Apply Shannon entropy formula
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy

# Function to process the fragments from a file
def process_file(file_path):
    with open(file_path, 'r') as file:
        fragments = file.read().split()

    if not fragments:
        print("No fragments found in the file.")
        return []

    # Calculate entropy for each fragment
    entropy_values = [(fragment, calculate_entropy(fragment)) for fragment in fragments]
    
    # Sort fragments by entropy (lowest first)
    sorted_fragments = sorted(entropy_values, key=lambda x: x[1])
    
    return sorted_fragments

file_path = 'fragments.txt'

sorted_fragments = process_file(file_path)

if sorted_fragments:
    print(f"Fragments sorted by entropy (from least to most):\n")
    for idx, (fragment, entropy) in enumerate(sorted_fragments, start=1):
        print(f"Fragment {idx}: {fragment} | Entropy: {entropy}")
else:
    print("No valid fragments found or processed.")
