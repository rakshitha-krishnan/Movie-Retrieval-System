from flask import Flask , request, render_template
import requests
from bs4 import BeautifulSoup  
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import parse_qsl, urljoin, urlparse
import sys
import pandas as pd

app = Flask(__name__)

# Lists to append the actor details to each actor detail retrieved
total_actor_names = []
total_actor_urls=[]
total_birth_dates =[]
total_place_of_birth=[]
total_also_known_as =[]
total_movie_data = []
total_credits=[]
total_gender = []
total_knownFor=[]
all_movies_list=[]

"""
 AUTHOR: Rakshitha Krishnan
 NAME: actor_crawl
 PARAMETERS: count, count of the urls
 PURPOSE: The function crawls through the website pages based on the count.
 PRECONDITION: count should be greater or equal to 1
 POSTCONDITION: It saves the actor info in a dataframe and saves to excel sheet.
 """
@app.route("/actor/<count>")
def actor_crawl(count):
    df = pd.DataFrame()
    df.drop(df.index, inplace=True)
    print(df)

    count= int(count)

    while(count != 0):
        url = 'https://www.themoviedb.org/person?page='+str(count)
        get_actor_list(url)
        count = count -1
    df["Actor Names"]= pd.Series(total_actor_names)
    df['actor bio urls'] = pd.Series(total_actor_urls)
    get_actor_Biodata(df)
    df.to_excel("actor.xlsx") # add the retrieved details to excel sheet
    #rendering to html table 
    return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

"""
 AUTHOR: Rakshitha Krishnan
 NAME: get_actor_list
 PARAMETERS: URL, URL of the website
 PURPOSE: The function scrapes the actor data of such as name of the actor and actor url.
 PRECONDITION: url passed should be a vaild url of the website.
 POSTCONDITION: It appends all the names, urls to the respective list
 """
def get_actor_list(url):
    code = requests.get(url)
    plain= code.text
    #Beautiful soup to parse the html
    soup = BeautifulSoup(plain,'html.parser')

    """
    NAME: get_actor_names
    PARAMETERS: soup, parsed html data of the url page
    PURPOSE: The Function to extract the actor names from HTML source code using BeautifulSoup present in the url.
    PRECONDITION: soup passed should be in text format
    POSTCONDITION: It appends all the ACTOR names to the total_actor_names list
    """
    def get_actor_names(soup):
        actor_names = soup.find_all('p', {'class': 'name'})
        actor_names_list = []
        for actor in actor_names:
            actor_names_list.append(actor.a.text.strip())
            total_actor_names.append(actor.a.text.strip())
        # return actor_names_list
    """
    NAME: get_actor_urls
    PARAMETERS: doc, parsed html data of the url page
    PURPOSE: The Function to extract the actor URLS from HTML source code using BeautifulSoup present in the url.
    PRECONDITION: doc passed should be in text format
    POSTCONDITION: It appends all the ACTOR URLS to the total_actor_urls list
    """
    def get_actor_urls(doc):
        actor_urls = []
        base_url = 'https://www.themoviedb.org'
        movie_names_urls = doc.find_all('p', {'class': 'name'})
        for actor in movie_names_urls:
            actor_urls.append(base_url + actor.a['href'])
            total_actor_urls.append(base_url +  actor.a['href'])
        # return actor_urls
    get_actor_names(soup)
    get_actor_urls(soup)

"""
    AUTHOR:Gayatri Regana
    NAME: get_actor_Biodata
    PARAMETERS: df, dataframe
    PURPOSE: The function retrieves each actor bio details from the collected urls.
    PRECONDITION: The dataframe should contain actor url column 
    POSTCONDITION: It appends all the ACTOR biodata to the respective lists 
"""    
def get_actor_Biodata(df):
    for url in df['actor bio urls']:
        code = requests.get(url)
        plain= code.text
        details_soup = BeautifulSoup(plain,'html.parser')
        div1_tags = details_soup.find('div', class_ = 'column')
        if div1_tags is not None:
            if div1_tags.find("section", class_ = "full_wrapper facts left_column") is not None:
                actor_info = div1_tags.find("section", class_ = "full_wrapper facts left_column")
                actor_info_det= actor_info.find("section")
                #Scraping info about birthdate, place , known for etc..
                for p_tag  in actor_info_det.findAll('p'):
                    if p_tag is not None:
                        strong_tag = p_tag.find('strong')
                        if strong_tag.text == 'Birthday':
                            total_birth_dates.append(p_tag.text.split()[1:2])
                        if strong_tag.text == 'Place of Birth':
                            total_place_of_birth.append(p_tag.text[14:])
                        if strong_tag.text == 'Gender':
                            total_gender.append(p_tag.text[7:])
                        if strong_tag.text == 'Known For':
                            total_knownFor.append(p_tag.text[9:])
                        if strong_tag.text == 'Known Credits':
                            total_credits.append(p_tag.text[14:])
                    else:
                        total_birth_dates.append(None)
                        total_place_of_birth.append(None)
                        total_gender.append(None)
                        total_knownFor.append(None)
                        total_credits.append(None)
                actor_alias= actor_info_det.find('ul')
                also_known_as=[]
                if actor_alias is not None:
                    for li_tag in actor_alias.find_all('li'):
                        li_tag= ''.join(li_tag.text.strip())
                        also_known_as.append(li_tag) 
                    total_also_known_as.append(" ".join(also_known_as))
                else:
                    also_known_as.append(None)      
                    total_also_known_as.append(also_known_as)
            else:
                total_birth_dates.append(None)
                total_place_of_birth.append(None)
                total_gender.append(None)
                total_knownFor.append(None)
                total_credits.append(None)
                total_also_known_as.append(None)
        else:
            total_birth_dates.append(None)
            total_place_of_birth.append(None)
            total_gender.append(None)
            total_knownFor.append(None)
            total_credits.append(None)
            total_also_known_as.append(None)

        #scraping the popular movies of the actor   
        movies_list=[]
        list_movies = details_soup.findAll('li',{'class':'account_adult_false item_adult_false'})
        if list_movies is not None:
            for li_tag in list_movies:
                if li_tag is not None:
                    for image_tag in li_tag.find('a',{"class":'title'}):
                        movies_list.append(image_tag.text.strip())
                else:
                    movies_list.append(None)
        else:
                    movies_list.append(None)
            
        print(movies_list)

        all_movies_list.append("  ,".join(movies_list))
        
    df['Birth_date'] = pd.Series(total_birth_dates)
    df['place_of_birth'] =pd.Series(total_place_of_birth)
    df['Known For'] = pd.Series(total_knownFor)
    df['Credits'] = pd.Series(total_credits)
    df['Gender'] = pd.Series(total_gender)
    df['Alias'] = pd.Series(total_also_known_as)
    df['Movies']= pd.Series(all_movies_list)
    # return df

"""

 AUTHOR: Rakshitha Krishnan,Gayatri Regana
 FILENAME: actor_names.py
 SPECIFICATION: It crawls through the TMDB website based on the given count, retrieves the actor information
 FOR: CS  5364 – Information Retrieval Section 001

"""
if __name__ == "__main__":
    app.run()
