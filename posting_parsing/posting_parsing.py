import requests
from bs4 import BeautifulSoup
import json
import sys
import datetime
import os

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


#Takes a list of jobs for alberta job board. 
#Scrapes job description. 
#Returns a list of job information. The job information structure will be a dictionary with the following keywords. 
    #job title
    #company
    #date posted
    #location
    #description
    #details 
def webscrape_page(jobs, home_url):
    job_list = []

    for job in jobs:

        job_dict = {}
        
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

        job_description_url = home_url + job["href"]
        
        response = requests.get(job_description_url)

        description_soup = BeautifulSoup(response.content, "html.parser")

        job_descrip = description_soup.find("div", {"class": "clearfix u_text--90 u_mb-base u_overflow-hidden"})


        details =  description_soup.find_all("div", {"class": "rf_tag u_mb-xxs u_mr-xxs"})
        details = [detail.text for detail in details]
        details += [extra_detail.text for extra_detail in description_soup.find_all("a", {"class": "rf_tag u_mb-xxs u_mr-xxs"})]

        job_dict["descrip"] = job_descrip.text

        job_dict["details"] = details

        job_list.append(job_dict)

    return job_list