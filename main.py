from resume_parsing.resume_parsing import parse_resume
from context_matching.context_matching import get_w2v_model
from posting_parsing.posting_parsing import webscrape_site

def main():
    resume_path = input("Enter the path to the resume you would like to match:\n")

    # Parse resume
    resume_dict = parse_resume(resume_path)

    # Scrape and parse job postings
    ab_postings = webscrape_site("https://www.albertajobcentre.ca", "saved_job_data/ab_job_data")
    # bc_postings = webscrape_site("https://www.bcjobs.ca", "saved_job_data/bc_job_data")

    # Get w2v model for help with context matching
    w2v_model = get_w2v_model()
    
if __name__ == "__main__":
    main()