import csv
from nltk.tokenize import word_tokenize, sent_tokenize
from gensim.models import Word2Vec

MODEL_FILE = "context_matching/w2v_model"

def context_matching(resume_dict, job_postings, w2v_model):
    print("Matching your resume to job postings...")

    # A list of tuples, the first element of which will be the job posting dictionary
    # and the second element of which will be a score indicating how similar
    # the posting is to the user's resume
    postings_with_score = []

    for posting in job_postings:
        # "title"
        # "company"
        # "date"
        # "location"
        # "descrip"
        # "details"

        # 'experience'
        # 'education'
        # 'interests'
        # 'software'
        # 'programming languages'
        # 'programming experience'
        # 'publications'
        # 'skills'
        # 'accomplishments'
        # 'certifications'
        # 'awards'
        # 'honours'
        # 'courses'
        # 'projects'
        # 'objectives'
        # 'languages'
        # 'leadership'

        # Get the job title from the posting
        posting_title = posting["title"]
        # If the user's resume has an experience section
        


    return postings_with_score


def get_w2v_model():
    try:
        saved_model = Word2Vec.load(MODEL_FILE)
        return saved_model
    except:
        training_data = get_w2v_training_data()

        w2v_model = Word2Vec(training_data, vector_size=100, window=3, min_count=1, sg=0)
        w2v_model.train(training_data, total_examples=w2v_model.corpus_count, epochs=30, report_delay=1)
        w2v_model.init_sims(replace=True)

        w2v_model.save(MODEL_FILE)

        return w2v_model

def get_w2v_training_data():
    print("Training a quick context matching model...")

    training_data = []

    with open('context_matching/monster_com-job_sample.csv', newline='', encoding="utf8") as csvfile:
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