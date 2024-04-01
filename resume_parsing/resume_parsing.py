# https://www.datacamp.com/tutorial/fuzzy-string-python 

# pip install thefuzz

from thefuzz import fuzz
from PyPDF2 import PdfReader
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from resume_parsing.headers import HEADERS, EDUCATION_HEADERS, EXPERIENCE_HEADERS, SKILLS_HEADERS, PROJECT_HEADERS, CERTIFICATION_HEADERS
import string
import re

output_path = 'Resume_output.txt'
stopwords = stopwords.words('english')
printable = set(string.printable)

def parse_resume(path):
    print("Hold tight, parsing your resume...")
    with open(output_path, 'w', encoding='utf-8') as file:
        reader = PdfReader(path)
        number_of_pages = len(reader.pages)
        lines = []
        for i in range(number_of_pages):
            page = reader.pages[i]
            pdf_text = page.extract_text()
            pdf_text = re.sub(r'-\n', '', pdf_text) # remove hyphenated words
            for sentence_token in sent_tokenize(pdf_text): # split by sentence
                for sentence_token in sentence_token.split("\n"): # split by newline
                    sentence_token = ' '.join([word for word in sentence_token.split() if word not in stopwords]) # remove stopwords
                    sentence_token = ''.join(filter(lambda x: x in printable, sentence_token)) # remove non-ascii characters like jot points
                    lines.append(sentence_token)
        header_dict = {}
        active_header = ''
        found_header = False
        header_dict[active_header] = []
        for line in lines:
            for header in HEADERS:
                if line.lower() == header or fuzz.ratio(header, line.lower()) > 75:
                    found_header = True
                    if header in EDUCATION_HEADERS:
                        active_header = 'education'
                    elif header in EXPERIENCE_HEADERS:
                        active_header = 'experience'
                    elif header in SKILLS_HEADERS:
                        active_header = 'skills'
                    elif header in PROJECT_HEADERS:
                        active_header = 'projects'
                    elif header in CERTIFICATION_HEADERS:
                        active_header = 'certifications'
                    else: 
                        active_header = 'unrelated header' 
                    if active_header not in header_dict:
                        header_dict[active_header] = []
                    break
            if found_header:
                found_header = False
                continue
            header_dict[active_header].append(line)

        for header in header_dict:
            if header == '':
                continue
            file.write(header.upper() + "\n----------\n")
            for sentence in header_dict[header]:
                file.write(sentence + "\n")
            file.write("\n")
    return header_dict
