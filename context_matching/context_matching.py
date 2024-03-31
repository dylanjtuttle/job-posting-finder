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

    best_score = -1000000
    best_posting = {}

    for posting in job_postings:
        # "title"
        # "company"
        # "date"
        # "location"
        # "descrip"
        # "details"

        # 'experience'
        # 'education'
        # 'skills'
        # 'projects'
        # 'certifications'

        # Get the job title from the posting
        posting_title = posting["title"]
        # If the user's resume has an experience section
        if "experience" in resume_dict:
            user_jobs = resume_dict["experience"]

            sum = 0
            count = 0
            for posting_word in posting_title.split(" "):
                for line in user_jobs:
                    for resume_word in line.split(" "):
                        posting_word = posting_word.lower()
                        resume_word = resume_word.lower()

                        try:
                            count += 1
                            similarity = w2v_model.wv.similarity(posting_word, resume_word)
                            sum += similarity
                        except:
                            continue

            average = sum / count
            if average > best_score:
                best_score = average
                best_posting = posting

    return postings_with_score


def get_w2v_model(resume_dict, job_postings):
    try:
        saved_model = Word2Vec.load(MODEL_FILE)
        return saved_model
    except:
        training_data = get_w2v_training_data(resume_dict, job_postings)

        w2v_model = Word2Vec(training_data, vector_size=100, window=3, min_count=1, sg=0)
        w2v_model.train(training_data, total_examples=w2v_model.corpus_count, epochs=30, report_delay=1)
        w2v_model.init_sims(replace=True)

        w2v_model.save(MODEL_FILE)

        return w2v_model

def get_w2v_training_data(resume_dict, job_postings):
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
                        if '.' in word:
                            word = word.replace('.', '')
                        if ',' in word:
                            word = word.replace(',', '')
                        if word != '':
                            new_sentence.append(word.lower())
                    if len(new_sentence) > 0:
                        training_data.append(new_sentence)
                
                for sentence in sent_tokenize(row['job_description'].lower()):
                    new_sentence = []
                    for word in word_tokenize(sentence):
                        if '.' in word:
                            word = word.replace('.', '')
                        if ',' in word:
                            word = word.replace(',', '')
                        if word != '':
                            new_sentence.append(word.lower())
                    if len(new_sentence) > 0:
                        training_data.append(new_sentence)

                for sentence in sent_tokenize(row['job_type'].lower()):
                    new_sentence = []
                    for word in word_tokenize(sentence):
                        if '.' in word:
                            word = word.replace('.', '')
                        if ',' in word:
                            word = word.replace(',', '')
                        if word != '':
                            new_sentence.append(word.lower())
                    if len(new_sentence) > 0:
                        training_data.append(new_sentence)
                
                for sentence in sent_tokenize(row['salary'].lower()):
                    new_sentence = []
                    for word in word_tokenize(sentence):
                        if '.' in word:
                            word = word.replace('.', '')
                        if ',' in word:
                            word = word.replace(',', '')
                        if word != '':
                            new_sentence.append(word.lower())
                    if len(new_sentence) > 0:
                        training_data.append(new_sentence)
        
        # Add the user's resume to the training data
        for key, value in resume_dict.items():
            for sentence in value:
                new_sentence = []
                for word in word_tokenize(sentence):
                    if '.' in word:
                        word = word.replace('.', '')
                    if ',' in word:
                        word = word.replace(',', '')
                    if word != '':
                        new_sentence.append(word.lower())
                if len(new_sentence) > 0:
                    training_data.append(new_sentence)
        
        # Add the job postings to the training data
        for posting in job_postings:
            for key, value in posting.items():
                new_sentence = []

                # Details is a list, everything else is a string
                if key == "details":
                    for sentence in value:
                        for word in word_tokenize(sentence):
                            if '.' in word:
                                word = word.replace('.', '')
                            if ',' in word:
                                word = word.replace(',', '')
                            if word != '':
                                new_sentence.append(word.lower())
                        if len(new_sentence) > 0:
                            training_data.append(new_sentence)
                else:
                    for word in word_tokenize(value):
                        if '.' in word:
                            word = word.replace('.', '')
                        if ',' in word:
                            word = word.replace(',', '')
                        if word != '':
                            new_sentence.append(word.lower())
                    if len(new_sentence) > 0:
                        training_data.append(new_sentence)

    return training_data