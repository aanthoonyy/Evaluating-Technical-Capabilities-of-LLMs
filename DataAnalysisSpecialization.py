import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys

def analyze_specialization(file_path):
    # Redirect stdout to both file and console
    class Logger(object):
        def __init__(self, filename="Default.log"):
            self.terminal = sys.stdout
            self.log = open(filename, "w")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            self.terminal.flush()
            self.log.flush()

    sys.stdout = Logger("specialization_analysis.txt")

    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Set model as index
    models = df['Model']
    df_scores = df.drop('Model', axis=1)
    
    # First normalize all scores within each category (0 to 1 scale)
    normalized_df = pd.DataFrame()
    for column in df_scores.columns:
        min_val = df_scores[column].min()
        max_val = df_scores[column].max()
        normalized_df[column] = (df_scores[column] - min_val) / (max_val - min_val)
    
    # Store the normalized scores with model names for reference
    normalized_with_names = normalized_df.copy()
    normalized_with_names['Model'] = models
    
    # Calculate average normalized score for each model
    normalized_df['AverageScore'] = normalized_df.mean(axis=1)
    
    # Calculate specialization scores based on normalized data
    specialization_scores = pd.DataFrame()
    for column in df_scores.columns:
        specialization_scores[column] = normalized_df[column] - normalized_df['AverageScore']
    
    # Find the highest specialization for each model
    specializations = {}
    specialization_magnitude = {}
    
    for i, model in enumerate(models):
        # Get the category with highest positive deviation
        max_spec = specialization_scores.iloc[i].max()
        max_spec_category = specialization_scores.iloc[i].idxmax()
        
        # Store the results
        specializations[model] = max_spec_category
        specialization_magnitude[model] = max_spec
    
    # Create a sorted list of models by specialization magnitude
    sorted_models = sorted(specialization_magnitude.items(), key=lambda x: x[1], reverse=True)
    
    # Print results
    print("\nModel Specializations Analysis (Based on Normalized Scores):")
    print("=========================================================")
    for model, magnitude in sorted_models:
        spec_category = specializations[model]
        normalized_score = normalized_with_names[normalized_with_names['Model'] == model][spec_category].iloc[0]
        original_score = df[df['Model'] == model][spec_category].iloc[0]
        
        print(f"\nModel: {model}")
        print(f"Specializes in: {spec_category}")
        print(f"Specialization magnitude: {magnitude:.3f}")
        print(f"Normalized score in this category: {normalized_score:.3f}")
        print(f"Original score in this category: {original_score:.3f}")
        
        # Get relative performance in specialty
        all_norm_scores = normalized_with_names[spec_category].values
        rank = sorted(all_norm_scores, reverse=True).index(normalized_score) + 1
        print(f"Ranks #{rank} in its specialty category")
        
        # # Print comparison to other models in this category (using normalized scores)
        # print("\nPerformance comparison in specialty category (normalized scores):")
        # category_comparison = normalized_with_names[['Model', spec_category]].sort_values(by=spec_category, ascending=False)
        # for idx, row in category_comparison.iterrows():
        #     print(f"  {row['Model']}: {row[spec_category]:.3f}")
        
        # # Also show original scores for reference
        # print("\nOriginal scores in specialty category:")
        # original_comparison = df[['Model', spec_category]].sort_values(by=spec_category, ascending=False)
        # for idx, row in original_comparison.iterrows():
        #     print(f"  {row['Model']}: {row[spec_category]:.3f}")

    # Additional summary statistics
    print("\nSummary Statistics:")
    print("==================")
    print("\nCategory Distribution (number of models specializing in each):")
    category_dist = pd.Series(specializations.values()).value_counts()
    print(category_dist)

    # Create visualization
    plt.figure(figsize=(12, 6))
    
    # Prepare data
    models, magnitudes = zip(*sorted_models)
    
    # Create color mapping for categories
    categories = list(df_scores.columns)
    color_map = {
        'ComplexCalculationsScore': '#FF9999',  # Light red
        'MultiStepScore': '#66B2FF',           # Light blue
        'RandomStringIdentificationScore': '#99FF99',  # Light green
        'RandomStringGenerationScore': '#FFCC99'  # Light orange
    }
    
    # Get colors for each bar based on specialization
    bar_colors = [color_map[specializations[model]] for model in models]
    
    # Create bars
    bars = plt.bar(range(len(models)), magnitudes, color=bar_colors)
    
    # Customize the appearance
    plt.title('Model Specialization Ranking')
    plt.xlabel('Models')
    plt.ylabel('Specialization Magnitude')
    plt.xticks(range(len(models)), models, rotation=45, ha='right')
    
    # Create legend
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color_map[cat], 
                      label=cat.replace('Score', '')) for cat in categories]
    plt.legend(handles=legend_elements, title='Specialization Category', 
              bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig('specialization_ranking.png', bbox_inches='tight', dpi=300)
    plt.close()

    return specializations, specialization_magnitude

# Run the analysis
specializations, magnitudes = analyze_specialization('LLMResults.csv')
