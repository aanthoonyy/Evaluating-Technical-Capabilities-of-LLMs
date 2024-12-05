import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Read the CSV file
df = pd.read_csv('LLMResults.csv')

# Calculate average performance
df['AverageScore'] = df.iloc[:, 1:].mean(axis=1)

# Create individual bar plots for each metric
metrics = ['ComplexCalculationsScore', 'MultiStepScore', 'RandomStringIdentificationScore', 'RandomStringGenerationScore']

for metric in metrics:
    # Sort DataFrame by current metric in descending order
    plot_df = df.sort_values(by=metric, ascending=False)
    
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(plot_df)), plot_df[metric])
    plt.title(f'Performance Comparison - {metric}')
    plt.xlabel('Models')
    plt.ylabel('Score')
    plt.xticks(range(len(plot_df)), plot_df['Model'], rotation=45, ha='right')
    
    # Add reference lines
    if metric in ['ComplexCalculationsScore', 'MultiStepScore', 'RandomStringIdentificationScore']:
        plt.axhline(y=0.25, color='r', linestyle='--', label='Random Guess (0.25)')
        plt.legend()
    elif metric == 'RandomStringGenerationScore':
        plt.axhline(y=0.8017, color='r', linestyle='--', label='True Random (0.8017)')
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(f'comparison_{metric}.png')
    plt.close()

# Create average performance bar plot
plot_df = df.sort_values(by='AverageScore', ascending=False)
plt.figure(figsize=(10, 6))
plt.bar(range(len(plot_df)), plot_df['AverageScore'])
plt.title('Average Performance Across All Metrics')
plt.xlabel('Models')
plt.ylabel('Average Score')
plt.xticks(range(len(plot_df)), plot_df['Model'], rotation=45, ha='right')
plt.tight_layout()
plt.savefig('average_performance.png')
plt.close()

# Create heatmap
plt.figure(figsize=(12, 6))
heatmap_data = df.set_index('Model').iloc[:, :-1]  # Exclude AverageScore
sns.heatmap(heatmap_data, annot=True, cmap='YlOrRd', fmt='.2f')
plt.title('Performance Heatmap')
plt.tight_layout()
plt.savefig('performance_heatmap.png')
plt.close()

# Create normalized line plot
normalized_df = df.copy()
for metric in metrics:
    min_val = normalized_df[metric].min()
    max_val = normalized_df[metric].max()
    normalized_df[metric] = (normalized_df[metric] - min_val) / (max_val - min_val)

melted_df = normalized_df.melt(id_vars=['Model'], 
                              value_vars=metrics,
                              var_name='Metric', 
                              value_name='Normalized Score')

plt.figure(figsize=(12, 6))
ax = sns.pointplot(data=melted_df, x='Metric', y='Normalized Score', hue='Model')
plt.title('Normalized Performance by Category')
plt.xticks(range(len(metrics)), metrics, rotation=45, ha='right')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('normalized_performance.png', bbox_inches='tight')
plt.close()

# Print average scores
print("\nAverage Scores:")
for _, row in df.iterrows():
    print(f"{row['Model']}: {row['AverageScore']:.3f}")
