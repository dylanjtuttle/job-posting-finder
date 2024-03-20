from PyPDF2 import PdfReader
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

def parse_resume(path):
    HEADERS = ['experience', 'education', 'interests', 'software', 'spoken languages', 'publications', 'skills', 'accomplishments', 'certifications', 'awards', 'honours', 'courses', 'projects', 'objectives', 'languages', 'programming languages', 'leadership']
    header_dict = {}

    output_path = 'Resume_output.txt'
    stopwords = stopwords.words('english')

    with open(output_path, 'w', encoding='utf-8') as file:
        reader = PdfReader(path)
        number_of_pages = len(reader.pages)
        page = reader.pages[0]
        pdf_text = page.extract_text()

        active_header = ""
        skip_header = False
        for sentence_token in sent_tokenize(pdf_text):
            for sentence_token in sentence_token.split("\n"):
                sentence_token = sentence_token.lower()
                for header in HEADERS:
                    if header == sentence_token.strip() or header in sentence_token.strip():
                        skip_header = True
                        active_header = header
                        header_dict[active_header] = []
                        break
                if skip_header == True:
                    skip_header = False
                    continue
                if active_header != "":
                    header_dict[active_header].append(sentence_token)
    
    return header_dict