import csv
from nltk.tokenize import word_tokenize, sent_tokenize
from gensim.models import Word2Vec

def get_w2v_model():
    training_data = get_w2v_training_data()

    w2v_model = Word2Vec(training_data, vector_size=100, window=3, min_count=1, sg=0)
    w2v_model.train(training_data, total_examples=w2v_model.corpus_count, epochs=30, report_delay=1)
    w2v_model.init_sims(replace=True)

    return w2v_model

def get_w2v_training_data():
    training_data = []

    with open('monster_com-job_sample.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sector = row['sector'].lower()
            if "software" in sector:
                for sentence in sent_tokenize(row['job_title'].lower()):
                    new_sentence = []
                    for word in word_tokenize(sentence):
                        if '.' in word or ',' in word:
                            continue
                        new_sentence.append(word)
                    if len(new_sentence) > 0:
                        training_data.append(new_sentence)
                
                for sentence in sent_tokenize(row['job_description'].lower()):
                    new_sentence = []
                    for word in word_tokenize(sentence):
                        if '.' in word or ',' in word:
                            continue
                        new_sentence.append(word)
                    if len(new_sentence) > 0:
                        training_data.append(new_sentence)

                for sentence in sent_tokenize(row['job_type'].lower()):
                    new_sentence = []
                    for word in word_tokenize(sentence):
                        if '.' in word or ',' in word:
                            continue
                        new_sentence.append(word)
                    if len(new_sentence) > 0:
                        training_data.append(new_sentence)
                
                for sentence in sent_tokenize(row['salary'].lower()):
                    new_sentence = []
                    for word in word_tokenize(sentence):
                        if '.' in word or ',' in word:
                            continue
                        new_sentence.append(word)
                    if len(new_sentence) > 0:
                        training_data.append(new_sentence)

    return training_data