import spacy
from utilities import get_column
from collections import defaultdict


def country_pretrained(text_list):
    # load the pretrained model
    nlp = spacy.load("en_core_web_sm")

    entity_counts = defaultdict(int)

    for text in text_list:
        print(text)
        doc = nlp(text)
        print(doc.ents)
        for entity in doc.ents:
            entity_text = entity.text
            entity_label = entity.label_
            # filter entities based on label
            if entity_label == "GPE" or entity_label == "NORP":
                entity_counts[entity_text+","+entity_label] += 1

    for entity, count in entity_counts.items():
        print(entity, count)

# execution example
# plugin_descriptions = get_column(
#     '../../dataset/plugins_scrape/plugin_2024-03-19.xlsx', 'description')
# plugin_descriptions.pop()
# country_pretrained(plugin_descriptions)
