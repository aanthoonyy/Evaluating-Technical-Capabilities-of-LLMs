import numpy as np
from collections import Counter
import scipy.stats as stats
import random

class RandomnessAnalyzer:
    def __init__(self, sequence):
        # Clean the sequence to ensure we only have digits
        self.sequence = ''.join(filter(str.isdigit, sequence))
        self.digits = [int(d) for d in self.sequence]
        
    def frequency_analysis(self):
        """Test for uniform distribution of digits"""
        counts = Counter(self.digits)
        expected_freq = len(self.digits) / 10  # Expected frequency for truly random
        chi_square, p_value = stats.chisquare(
            [counts.get(i, 0) for i in range(10)],
            [expected_freq] * 10
        )
        return {
            'distribution_p_value': p_value,
            'digit_frequencies': dict(counts)
        }

    def runs_test(self):
        """Test for independence of consecutive digits"""
        median = np.median(self.digits)
        runs = ''.join('1' if x > median else '0' for x in self.digits)
        runs_count = len([i for i in range(1, len(runs)) if runs[i] != runs[i-1]]) + 1
        
        n1 = runs.count('1')
        n2 = runs.count('0')
        
        # Calculate expected runs and variance
        expected_runs = ((2 * n1 * n2) / (n1 + n2)) + 1
        variance = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))
        
        z_score = (runs_count - expected_runs) / np.sqrt(variance)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        return {
            'runs_p_value': p_value,
            'runs_count': runs_count
        }

    def autocorrelation_test(self, lag=1):
        """Test for correlation between digits at different positions"""
        correlation = np.corrcoef(self.digits[:-lag], self.digits[lag:])[0,1]
        return {'autocorrelation': correlation}

    def pattern_detection(self):
        """Look for repeating patterns"""
        sequence_str = ''.join(map(str, self.digits))
        pattern_scores = {}
        
        # Check for repeating subsequences
        for length in range(2, 6):
            patterns = {}
            for i in range(len(sequence_str) - length):
                pattern = sequence_str[i:i+length]
                patterns[pattern] = patterns.get(pattern, 0) + 1
            
            # Calculate pattern entropy
            total = sum(patterns.values())
            entropy = -sum((count/total) * np.log2(count/total) 
                         for count in patterns.values())
            pattern_scores[f'{length}_digit_patterns'] = entropy
        
        return pattern_scores

    def analyze(self):
        """Perform all randomness tests and return comprehensive results"""
        results = {
            'sequence_length': len(self.sequence),
            'frequency_analysis': self.frequency_analysis(),
            'runs_test': self.runs_test(),
            'autocorrelation': self.autocorrelation_test(),
            'pattern_analysis': self.pattern_detection()
        }
        
        # Calculate overall randomness score (0-100)
        score_components = [
            results['frequency_analysis']['distribution_p_value'] * 30,  # Weight: 30%
            results['runs_test']['runs_p_value'] * 30,                  # Weight: 30%
            (1 - abs(results['autocorrelation']['autocorrelation'])) * 20,  # Weight: 20%
            np.mean(list(results['pattern_analysis'].values())) / 4 * 20    # Weight: 20%
        ]
        
        results['randomness_score'] = min(100, max(0, sum(score_components)))

        return results

if __name__ == "__main__":
    import secrets
    avg_score = 0
    for _ in range(1000):
        num = ''.join(str(secrets.randbelow(10)) for _ in range(100))
        analyzer = RandomnessAnalyzer(num)
        results = analyzer.analyze()
        avg_score += results['randomness_score']
    avg_score /= 1000
    print(f"Average Randomness Score: {avg_score:.2f}/100")


