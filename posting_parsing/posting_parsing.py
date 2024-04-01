import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
import nltk
import sklearn.naive_bayes
import sklearn.feature_extraction.text
import imblearn

CORPORATE_JARGON_LABEL = "CJ"
CORPORATE_JARGON = 0
EXPERIENCE_LABEL = "E"
EXPERIENCE = 1
TECHNICAL_SKILL_LABEL = "TS"
TECHNICAL_SKILL = 2
SOFT_SKILL_LABEL = "SS"
SOFT_SKILL = 3
DEGREE_REQUIREMENT_LABEL = "D"
DEGREE_REQUIREMENT = 4
SALARY_LABEL = "S"
SALARY = 5

# Given a url for either the Alberta or BC jobs website (and a filename to pickle the data into)
# return a list of dictionaries with the following keys:
    # "title"
    # "company"
    # "date"
    # "location"
    # "descrip"
    # "details"
def get_job_data_from_site(home_url, filename):
    # If we've already pickled this particular dataset
    if os.path.isfile(filename) and os.path.getsize(filename) > 0:
        try:
            f = open(filename, "rb")
            data = json.load(f)
            f.close()
            if data["date"] == datetime.datetime.now().strftime("%d/%m/%Y"):
                return data["job_list"]
            else:
                return webscrape_site(home_url, filename)
        except:
            return webscrape_site(home_url, filename)
    else:
        return webscrape_site(home_url, filename)


def webscrape_site(home_url, filename):  
    job_list = []

    page_url = home_url + "/search-jobs?q=software+development&location=#page=1"
    page_number = 1

    print(f"Scraping job postings from {home_url}...")
    while True:
        jobs = []
        
        response = requests.get(page_url)

        soup = BeautifulSoup(response.content, "html.parser")
    
        jobs = jobs + soup.find_all("a" ,{"class" : "list-item-wrapper clearfix odd" })
        jobs = jobs + soup.find_all("a", {"class":"list-item-wrapper clearfix even"})

        job_list = job_list + webscrape_page(jobs, home_url)
        

        next_button = soup.find("a", attrs={"class": "btn btn-custom btn-default btn-sm" , "alt": "Next"})

        if next_button is None or page_number > 5: 
            f = open(filename, "w")
            json.dump({"date": datetime.datetime.now().strftime("%d/%m/%Y"), "job_list": job_list}, f)
            f.close()
            return job_list

        page_url = home_url + next_button["href"]
        page_number += 1


# Takes a list of jobs for a particular 
# Scrapes job description. 
# Returns a list of job posting dictionaries. Each dictionary will have the following keys: 
    # url
    # job title
    # company
    # date posted
    # location
    # corporate_jargon
    # experience
    # technical_skills
    # soft_skills
    # degree_requirements
    # salary
    # details
def webscrape_page(jobs, home_url):
    vectorizer = sklearn.feature_extraction.text.CountVectorizer()
    clf = get_topic_modeling_model(vectorizer)

    job_list = []

    for job in jobs:

        job_dict = {}

        job_description_url = home_url + job["href"]
        job_dict["url"] = job_description_url
        
        job_title = job.find("div", {"class" : "text-16 list-item-title text-limit text-bold"})
        job_dict["title"] = job_title.text
        
        company = job.find(lambda tag: tag.name == "div" and tag.get("class") == ["text-limit"])
        job_dict["company"] = company.text
        
        date_posted = job.find("strong")
        job_dict["date"] = date_posted.text
        
        location = job.find("div", {"class" : "col-xs-12 col-sm-4 text-right xs-text-left u_p-none"})
        location = str(location).split("</strong>")[1]
        job_dict["location"] = location

        #Scrape description
        response = requests.get(job_description_url)
        description_soup = BeautifulSoup(response.content, "html.parser")
        job_descrip = description_soup.find("div", {"class": "clearfix u_text--90 u_mb-base u_overflow-hidden"})

        # We need to go through each sentence in this job description,
        # use our naive bayes topic modeler to give it a label,
        # and then use the labels to sort the sentences into the appropriate list
        corporate_jargon = []
        experience = []
        technical_skills = []
        soft_skills = []
        degree_requirements = []
        salary = []

        # Get the job description from the soup object
        job_descrip = job_descrip.text
        # Tokenize the job description into sentences
        sentences = nltk.tokenize.sent_tokenize(job_descrip)
        # Label our sentences
        labels = label_sentences(clf, vectorizer, sentences)

        # Separate the list of sentences into multiple lists based on the labels
        for i in range(len(sentences)):
            sentence = sentences[i]
            label = labels[i]

            if label == CORPORATE_JARGON:
                corporate_jargon.append(sentence)
            if label == EXPERIENCE:
                experience.append(sentence)
            if label == TECHNICAL_SKILL:
                technical_skills.append(sentence)
            if label == SOFT_SKILL:
                soft_skills.append(sentence)
            if label == DEGREE_REQUIREMENT:
                degree_requirements.append(sentence)
            if label == SALARY:
                salary.append(sentence)
        
        job_dict["corporate_jargon"] = " ".join(corporate_jargon)
        job_dict["experience"] = " ".join(experience)
        job_dict["technical_skills"] = " ".join(technical_skills)
        job_dict["soft_skills"] = " ".join(soft_skills)
        job_dict["degree_requirements"] = " ".join(degree_requirements)
        job_dict["salary"] = " ".join(salary)

        details =  description_soup.find_all("div", {"class": "rf_tag u_mb-xxs u_mr-xxs"})
        details = [detail.text for detail in details]
        details += [extra_detail.text for extra_detail in description_soup.find_all("a", {"class": "rf_tag u_mb-xxs u_mr-xxs"})]
        job_dict["details"] = " ".join(details)

        job_list.append(job_dict)

    return job_list


def label_sentences(clf, vectorizer, sentences):
    # Convert the sentences into the format that our model expects
    sentences = vectorizer.transform(sentences)
    sentences = sentences.toarray()
    # Get our model to generate labels for each of our sentences
    return clf.predict(sentences)


def get_topic_modeling_model(vectorizer):
    X, y = get_labeled_sentence_data()

    X = vectorizer.fit_transform(X)
    X = X.toarray()

    # We will be using multinomial naive baysian because it is the best for categorical data,
    # but multinomial naive bayesian can get messed up by uneven data distributions,
    # so we will try to undersample the corporate jargon
    rus = imblearn.under_sampling.RandomUnderSampler(random_state = 42,
                                                     sampling_strategy =
                                                        {CORPORATE_JARGON: 50,
                                                         EXPERIENCE: 14,
                                                         TECHNICAL_SKILL: 50,
                                                         SOFT_SKILL: 27,
                                                         DEGREE_REQUIREMENT: 6,
                                                         SALARY: 8})
    X, y = rus.fit_resample(X, y)

    # The model
    clf = sklearn.naive_bayes.MultinomialNB()
    clf.fit(X, y)

    return clf


def get_labeled_sentence_data():
    sentences = []
    labels = []

    # Loop through all four of the files with labeled sentences
    for i in range (1, 5):
        # Open the given file
        with open(f"posting_parsing/labeled_sentences{i}.txt", "r") as infile:
            # Loop through each line in the file
            for sentence in infile:
                # Split the line by a colon,
                # with the first element being the sentence and the second being the label
                sentence_and_label = sentence.split(":")

                # If the line has exactly one sentence and one label
                if (len(sentence_and_label) == 2):
                    sentence = sentence_and_label[0].strip()
                    label = sentence_and_label[1].strip()

                    # If the label is one of our valid labels
                    if is_valid_label(label):
                        # Perform preprocessing on the sentence and add it to the list
                        clean_sentence = job_description_preprocessing(sentence)
                        sentences.append(clean_sentence)
                        # Convert the label to a number and add it to the list
                        labels.append(label_to_num(label))
    
    return (sentences, labels)


def is_valid_label(label):
    return label == CORPORATE_JARGON_LABEL \
        or label == EXPERIENCE_LABEL \
        or label == TECHNICAL_SKILL_LABEL \
        or label == SOFT_SKILL_LABEL \
        or label == DEGREE_REQUIREMENT_LABEL \
        or label == SALARY_LABEL


def label_to_num(label):
    if label == CORPORATE_JARGON_LABEL:
        return CORPORATE_JARGON
    if label == EXPERIENCE_LABEL:
        return EXPERIENCE
    if label == TECHNICAL_SKILL_LABEL:
        return TECHNICAL_SKILL
    if label == SOFT_SKILL_LABEL:
        return SOFT_SKILL
    if label == DEGREE_REQUIREMENT_LABEL:
        return DEGREE_REQUIREMENT
    if label == SALARY_LABEL:
        return SALARY


def job_description_preprocessing(sentence):
    stop_words = set(nltk.corpus.stopwords.words("english"))
    punctuation = [";", ".", ",", "!" "(", ")", ":"]

    sentence = sentence.lower()

    # Remove punctuation
    sentence = "".join([w for w in sentence if w not in punctuation])

    # Word tokenize
    sentence = nltk.tokenize.word_tokenize(sentence)
    
    # Stem
    stemmer = nltk.stem.PorterStemmer()
    sentence = [stemmer.stem(w) + " " for w in sentence if not w in stop_words]

    # Join back into a sentence and return
    return "".join(sentence)