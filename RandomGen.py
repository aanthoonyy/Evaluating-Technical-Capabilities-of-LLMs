import random
import secrets
import csv

def generate_sequential(length):
    """Pattern 1: Sequential numbers"""
    start = random.randint(0, 900000)
    return str(start).zfill(length)

def generate_repeating(length):
    """Pattern 2: Repeating single digit"""
    base = str(random.randint(0, 9))
    return (base * length)[:length]

def generate_alternating(length):
    """Pattern 3: Alternating two digits"""
    pattern = str(random.randint(0, 1)) + str(random.randint(0, 1))
    return (pattern * (length//2 + 1))[:length]

def generate_fibonacci_like(length):
    """Pattern 4: Fibonacci-like sequence"""
    a, b = random.randint(0, 9), random.randint(0, 9)
    result = str(a) + str(b)
    while len(result) < length:
        next_digit = (int(result[-1]) + int(result[-2])) % 10
        result += str(next_digit)
    return result[:length]

def generate_ascending(length):
    """Pattern 5: Ascending digits"""
    start = random.randint(0, 5)
    result = ''
    for i in range(length):
        result += str((start + i) % 10)
    return result

def generate_descending(length):
    """Pattern 6: Descending digits"""
    start = random.randint(4, 9)
    result = ''
    for i in range(length):
        result += str((start - i) % 10)
    return result

def generate_palindrome(length):
    """Pattern 7: Palindrome pattern"""
    half_length = length // 2
    first_half = ''.join(str(random.randint(0, 9)) for _ in range(half_length))
    if length % 2 == 0:
        return first_half + first_half[::-1]
    else:
        middle = str(random.randint(0, 9))
        return first_half + middle + first_half[::-1]

def generate_multiplicative(length):
    """Pattern 8: Multiplicative sequence"""
    base = random.randint(1, 3)
    result = ''
    current = 1
    while len(result) < length:
        result += str(current % 10)
        current *= base
    return result[:length]

def generate_squared(length):
    """Pattern 9: Squared numbers sequence"""
    result = ''
    i = random.randint(0, 3)
    while len(result) < length:
        result += str((i * i) % 10)
        i += 1
    return result[:length]

def generate_geometric(length):
    """Pattern 10: Geometric sequence"""
    start = random.randint(1, 5)
    ratio = random.randint(2, 3)
    result = ''
    current = start
    while len(result) < length:
        result += str(current % 10)
        current *= ratio
    return result[:length]

def generate_true_random(length, binary=False):
    """Generate a truly random number using secrets module"""
    if binary:
        return ''.join(str(secrets.randbelow(2)) for _ in range(length))
    else:
        return ''.join(str(secrets.randbelow(10)) for _ in range(length))

def get_random_pattern(length, binary=False):
    """Get a random pattern generator"""
    if binary:
        # Subset of patterns that work well with binary
        patterns = [
            generate_alternating,
            generate_repeating,
            lambda l: generate_palindrome(l)[:l],
            lambda l: generate_sequential(l)[:l]
        ]
    else:
        patterns = [
            generate_sequential,
            generate_repeating,
            generate_alternating,
            generate_fibonacci_like,
            generate_ascending,
            generate_descending,
            generate_palindrome,
            generate_multiplicative,
            generate_squared,
            generate_geometric
        ]
    return random.choice(patterns)

def generate_question_data(binary=False):
    """Generate a question data for CSV"""
    length = random.randint(6, 9)
    
    # Generate true random option
    true_random = generate_true_random(length, binary)
    
    # Generate three random pattern options
    used_patterns = set()
    options = []
    
    # Add three pattern-based options
    while len(options) < 3:
        pattern_func = get_random_pattern(length, binary)
        pattern_result = pattern_func(length)
        if pattern_result not in options:  # Avoid duplicate numbers
            options.append(pattern_result)
    
    # Add the true random option
    options.append(true_random)
    
    # Keep track of the correct answer
    correct_answer = 'D'  # Before shuffling, D is always correct
    
    # Shuffle options and update correct answer
    correct_index = 3
    indices = list(range(4))
    random.shuffle(indices)
    shuffled_options = [options[i] for i in indices]
    correct_answer = chr(65 + indices.index(correct_index))
    
    return {
        'Question': 'Which of the following is truly random?',
        'A': shuffled_options[0],
        'B': shuffled_options[1],
        'C': shuffled_options[2],
        'D': shuffled_options[3],
        'Answer': correct_answer
    }

def generate_csv(filename, num_questions=5):
    fieldnames = ['Question', 'A', 'B', 'C', 'D', 'Answer']
    questions = []
    
    for _ in range(num_questions):
        binary = random.choice([True, False])
        questions.append(generate_question_data(binary))
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(questions)

# Generate CSV file
generate_csv('random_number_questions.csv', 30)
