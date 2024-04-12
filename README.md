# job-posting-finder
A project for CPSC 599.27 (Natural Language Processing), using NLP technology to recommend a user relevant computer science job postings based on their resume

# Authors:
- Dylan Tuttle
- Kaylee Nasser
- Rachel Ralph

# Project Structure
- `main.py` contains logic involving prompting the user for a path to a resume, executing the three subsections of the project (resume parsing, job posting scraping, and context matching), and returning the results of the context matching in the form of the URLs of the 10 job postings that best suit the user's resume.
- `resume_parsing/` contains code for parsing and extracting information out of the user's resume
- `posting_parsing/` contains code and data related to scraping, parsing, and extracting information out of job postings
- `context_matching/` contains code and data related to training the custom Word2Vec model and matching job postings to the user's resume
- `Job Description Shenanigans/` contains a series of Jupyter notebooks which are not a part of the project's code, but contain Rachel's work trying to determine the best way to perform topic modelling on the job descriptions. The most successful of these, the Naive Bayesian model, was extracted from these notebooks and inserted into the actual code.
- `saved_job_data/` contains serialized JSON files which store job posting data so the project only needs to scrape live postings once a day
- `ExampleResumes/` contains resumes that we used to test our project.
- `resume_output.txt/` is a helpful file that shows what information was extracted from your resume.

# Running The Project
To run the project, enter the following command:
```bash
python main.py
```
When prompted to, enter the path to a resume you want to be analyzed and press Enter.
