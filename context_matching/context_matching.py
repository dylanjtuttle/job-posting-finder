import csv
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from gensim.models import Word2Vec
from thefuzz import fuzz
import heapq

class PostingWithScore(object):
    def __init__(self, posting, score):
        self.posting = posting
        self.score = score

    def __lt__(self, other):
        return self.score < other.score
    
    def __le__(self, other):
        return self.score <= other.score

MODEL_FILE = "context_matching/w2v_model"
PUNCTUATION = [";", ".", ",", "!" "(", ")", ":"]

def context_matching(resume_dict, job_postings, w2v_model):
    print("Matching your resume to job postings...")

    # A heap of PostingWithScore objects
    postings_with_score = []

    for posting in job_postings:
        posting_score = 0

        # If the user's resume has an experience section,
        # perform an experience match with the posting
        if "experience" in resume_dict:
            posting_score += experience_match(w2v_model, resume_dict, posting)

        # If the user's resume has an education section,
        # perform an education match with the posting
        if "education" in resume_dict:
            posting_score += education_match(w2v_model, resume_dict, posting)

        # If the user's resume has a skills section,
        # perform a skill match with the posting
        if "skills" in resume_dict:
            posting_score += skill_match(resume_dict, posting)
        
        # If the user's resume has a projects section,
        # perform a project match with the posting
        if "projects" in resume_dict:
            posting_score += project_match(resume_dict, posting)
        
        # If the user's resume has a certifications section,
        # perform a certification match with the posting
        if "certifications" in resume_dict:
            posting_score += certification_match(resume_dict, posting)
        
        # Insert a new PostingWithScore object into the heap
        heapq.heappush(postings_with_score, PostingWithScore(posting, posting_score))

    return postings_with_score


def experience_match(w2v_model, resume_dict, posting):
    stop_words = set(nltk.corpus.stopwords.words("english"))

    # An entry in a resume's experience section usually contains
    # a job title
    # a company name (not useful, the user is probably looking for a job at a different company)
    # a time range (again not useful)
    # a location (could be useful to recommend jobs in the same city(ies) that a user has worked before)
    # a description of the job, potentially including experience gained and skills learned
    # 
    # We will combine different parts of the job posting to try and
    # synthesize a blurb that might resemble the set of words
    # that would appear in a user's entry in their resume describing their time at this job
    # so that we can compare with the user's experience section
    posting_experience = " ".join([posting["title"],
                                    posting["location"],
                                    posting["experience"],
                                    posting["technical_skills"],
                                    posting["soft_skills"]])

    # Get the user's experience
    user_experience = resume_dict["experience"]

    sum = 0
    count = 0
    # Get the model to calculate the similarity between every word in the user's experience
    # with every word in the synthesized experience from the posting
    for posting_word in word_tokenize(posting_experience):
        if posting_word not in PUNCTUATION and posting_word not in stop_words:
            for line in user_experience:
                for resume_word in word_tokenize(line):
                    if resume_word not in PUNCTUATION and posting_word not in stop_words:
                        posting_word = posting_word.lower().strip()
                        resume_word = resume_word.lower().strip()

                        try:
                            count += 1
                            similarity = w2v_model.wv.similarity(posting_word, resume_word)
                            sum += similarity
                        # Skip any words that don't appear in the model's vocabulary
                        except:
                            continue

    # Return the average similarity of all the words
    if count == 0:
        return 0
    else:
        return sum / count


def education_match(w2v_model, resume_dict, posting):
    stop_words = set(nltk.corpus.stopwords.words("english"))

    sum = 0
    count = 0
    # Get the model to calculate the similarity between every word in the user's education section
    # with every word in the posting's degree requirements
    for posting_word in word_tokenize(posting["degree_requirements"]):
        if posting_word not in PUNCTUATION and posting_word not in stop_words:
            for line in resume_dict["education"]:
                for resume_word in word_tokenize(line):
                    if resume_word not in PUNCTUATION and posting_word not in stop_words:
                        posting_word = posting_word.lower().strip()
                        resume_word = resume_word.lower().strip()

                        try:
                            count += 1
                            similarity = w2v_model.wv.similarity(posting_word, resume_word)
                            sum += similarity
                        # Skip any words that don't appear in the model's vocabulary
                        except:
                            continue
    
    # Return the average similarity of all the words
    if count == 0:
        return 0
    else:
        return sum / count


def skill_match(resume_dict, posting):
    stop_words = set(nltk.corpus.stopwords.words("english"))

    num_matches = 0
    num_words = 0
    # Count how many words in the user's skills section match a word in the posting's skill requirements
    for posting_word in word_tokenize(" ".join([posting["experience"],
                                                posting["technical_skills"],
                                                posting["soft_skills"]])):
        if posting_word not in PUNCTUATION and posting_word not in stop_words:
            for line in resume_dict["skills"]:
                for resume_word in word_tokenize(line):
                    if resume_word not in PUNCTUATION and posting_word not in stop_words:
                        num_words += 1

                        posting_word = posting_word.lower().strip()
                        resume_word = resume_word.lower().strip()

                        # If the words match (within a certain threshold allowing for minor spelling mistakes)
                        if fuzz.ratio(resume_word, posting_word) > 90:
                            num_matches += 1
    
    # Return the percentage of words in the skills section that match the posting's skill requirements
    if num_words == 0:
        return 0
    else:
        return num_matches / num_words


def project_match(resume_dict, posting):
    stop_words = set(nltk.corpus.stopwords.words("english"))

    num_matches = 0
    num_words = 0
    # Count how many words in the user's projects section match a word in the posting's skill requirements
    for posting_word in word_tokenize(" ".join([posting["experience"],
                                                posting["technical_skills"],
                                                posting["soft_skills"]])):
        if posting_word not in PUNCTUATION and posting_word not in stop_words:
            for line in resume_dict["projects"]:
                for resume_word in word_tokenize(line):
                    if resume_word not in PUNCTUATION and posting_word not in stop_words:
                        num_words += 1

                        posting_word = posting_word.lower().strip()
                        resume_word = resume_word.lower().strip()

                        # If the words match (within a certain threshold allowing for minor spelling mistakes)
                        if fuzz.ratio(resume_word, posting_word) > 90:
                            num_matches += 1
    
    # Return the percentage of words in the projects section that match the posting's skill requirements
    if num_words == 0:
        return 0
    else:
        return num_matches / num_words


def certification_match(resume_dict, posting):
    stop_words = set(nltk.corpus.stopwords.words("english"))

    num_matches = 0
    num_words = 0
    # Count how many words in the user's certifications section match a word in the posting's skill requirements
    for posting_word in word_tokenize(" ".join([posting["experience"],
                                                posting["technical_skills"],
                                                posting["soft_skills"]])):
        if posting_word not in PUNCTUATION and posting_word not in stop_words:
            for line in resume_dict["certifications"]:
                for resume_word in word_tokenize(line):
                    if resume_word not in PUNCTUATION and posting_word not in stop_words:
                        num_words += 1

                        posting_word = posting_word.lower().strip()
                        resume_word = resume_word.lower().strip()

                        # If the words match (within a certain threshold allowing for minor spelling mistakes)
                        if fuzz.ratio(resume_word, posting_word) > 90:
                            num_matches += 1
    
    # Return the percentage of words in the certifications section that match the posting's skill requirements
    if num_words == 0:
        return 0
    else:
        return num_matches / num_words


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