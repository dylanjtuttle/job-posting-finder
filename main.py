from resume_parsing.resume_parsing import parse_resume
from context_matching.context_matching import get_w2v_model

def main():
    resume_dict = parse_resume("resume_parsing/IBM Resume - Dylan Tuttle.pdf")

    w2v_model = get_w2v_model()

if __name__ == "__main__":
    main()