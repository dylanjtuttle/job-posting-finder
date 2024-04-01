from resume_parsing.resume_parsing import parse_resume
from context_matching.context_matching import get_w2v_model, context_matching
from posting_parsing.posting_parsing import get_job_data_from_site

import heapq

def main():
    resume_path = input("Enter the path to the resume you would like to match:\n")

    # Parse resume
    resume_dict = parse_resume(resume_path)

    # Scrape and parse job postings
    ab_postings = get_job_data_from_site("https://www.albertajobcentre.ca", "saved_job_data/ab_job_data.json")
    bc_postings = get_job_data_from_site("https://www.bcjobs.ca", "saved_job_data/bc_job_data.json")
    postings = ab_postings + bc_postings

    # Get w2v model for help with context matching
    w2v_model = get_w2v_model(resume_dict, postings)

    # Perform context matching
    postings_with_score = context_matching(resume_dict, postings, w2v_model)

    print("")
    print("Here are the 10 best job postings we've found for you:")
    i = 0
    for entry in heapq.nlargest(10, postings_with_score):
        print(f"{i + 1} ({entry.score}): {entry.posting["url"]}")
        i += 1
    
if __name__ == "__main__":
    main()