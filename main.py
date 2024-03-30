from resume_parsing.resume_parsing import parse_resume
from context_matching.context_matching import get_w2v_model

def main():
    resume_path = input("Enter the path to the resume you would like to parse match:\n")
    resume_dict = parse_resume(resume_path)
    w2v_model = get_w2v_model()

if __name__ == "__main__":
    main()