import requests
import pandas as pd
from utilities import filter_category, calculate_zscore, get_column
import numpy as np
import time

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
headers = {"Authorization": "Bearer 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"}

test_categories = ['Books', 'Business', 'Career', 'Document Management',
                   'Developer & Code', 'Education', 'Entertainment', 'Finance', 'Food & Drink', 'Games', 'Graphics & Design', 'Health & Fitness', 'Lifestyle',
                   'Medical', 'Music', 'Navigation', 'News', 'Photo & Video', 'Productivity', 'Reference', 'Shopping', 'Social Networking',
                   'Sports', 'Travel', 'Utilities', 'Weather']

categories = ['Books', 'Business', 'Career & Jobs', 'Charts & Diagrams', 'Document Management',
              'Developer & Code', 'Education & Learning', 'Entertainment & Game', 'Finance & Trading', 'Travel & Lifestyle', 'Health & Medical', 'Audio & Music', 'News', 'Image & Video', 'Data & Research', 'Crypto & NFTs', 'Shopping & Deals', 'Law', 'Plugin Tips', 'Weather & Climate']


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def query_classification(description, categories):
    return query({
        "inputs": description,
        "parameters": {"candidate_labels": categories},
    })


def classify(description, categories):
    batch_size = 10
    results = {}

    # Loop through categories in batches
    for i in range(0, len(categories), batch_size):
        # Splitting categories into batches
        batch_categories = categories[i:i + batch_size]
        try:
            # calculate score for current batch with ML model
            output = query_classification(description, batch_categories)
            category_score = {label: score for label, score in zip(
                output['labels'], output['scores'])}

        except Exception as e:
            print("Incorrect output in classify:", output)
            time.sleep(30)
            return

        results = {**results, **category_score}
    results = dict(
        sorted(results.items(), key=lambda item: item[1], reverse=True))
    top10 = list(results.items())[:10]
    keys = [item[0] for item in top10]
    max_category = (classify_top10(description, keys))
    print(description)
    print(max_category)
    return max_category


def classify_top10(description, top10):
    results = {}
    try:
        output = query_classification(description, top10)
        category_score = {label: score for label, score in zip(
            output['labels'], output['scores'])}
    except Exception as e:
        print("Incorrect output:", output)
        time.sleep(30)
        return

    results = category_score
    results = dict(
        sorted(results.items(), key=lambda item: item[1], reverse=True))
    print(results)

    # find category with max score
    max_category = max(results, key=results.get)
    return max_category


def categorise_data(file_path, categorise, output_file, temp_file, categories):
    index = 0
    save_interval = 25
    results = {}
    df = pd.read_excel(file_path)
    num_categorised = 0
    plugins = dict(zip(df['title'], df['description']))
    for title, description in plugins.items():
        num_categorised += 1
        print(num_categorised)
        category = categorise(description, categories)
        results[title] = {
            'description': description,
            'category': category
        }
        # index to keep track of how many plugins have been categorised
        print("\n")
        index += 1
        # save data in intervals
        if index % save_interval == 0:
            try:
                # Add a new column 'category' with the results to the DataFrame
                df['category'] = [results[title]['category'] if title in results else None
                                  for title in df['title']]
                df.to_excel(temp_file, index=False)
            except Exception as e:
                print(e)
                pass

    # Save once entire file is categorised
    df['category'] = [results[title]['category'] for title in df['title']]
    df.to_excel(output_file, index=False)


# execution example
categorise_data('../../dataset/plugins_scrape/plugin_2024-03-19.xlsx', classify,
                'categorisation_result.xlsx', 'categorisation_partial.xlsx', categories)
