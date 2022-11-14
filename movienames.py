import validators
from flask import Flask , request, render_template
import requests
from bs4 import BeautifulSoup  
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import parse_qsl, urljoin, urlparse
import sys
import pandas as pd

app = Flask(__name__)

# Lists to append the movie details to each movie detail retrieved
internal_urls= set()  
external_urls = set()
all_urls = set()
broken_urls = set()
total_movie_names =[]
total_movie_ratings =[]
total_movie_urls =[]
total_genres =[]
total_release_dates =[]
total_running_time =[]
total_certifications =[]
total_tagline=[]
total_overview = []
total_status=[]
total_language=[]
total_budget=[]
total_revenue=[]
total_titles=[]
total_providers=[]
total_keywords = []
total_cast = []
count_urls_visited = 0

"""
 AUTHOR: Kavya Konisa
 NAME: movie_crawl
 PARAMETERS: count, count of the urls
 PURPOSE: The function crawls through the website pages based on the count.
 PRECONDITION: count should be greater or equal to 1
 POSTCONDITION: it saves the movie info in a dataframe and saves to excel sheet.It saves all internal and extrernal urls to the txt file
 """
@app.route("/movie/<count>")
def movie_crawl(count):
    df = pd.DataFrame()
    print(df)
    # df.drop(df.index, inplace=True)
    count= int(count)
    while(count != 0):
        url = 'https://www.themoviedb.org/movie?page='+str(count)
        get_movies_list(url)
        print("count..................",count)
        count = count -1
    df["names"]= total_movie_names
    df["rating"]= total_movie_ratings
    df['urls'] = total_movie_urls
    get_movie_details(df)
    print(df)  
    # add the retrieved details to excel sheet 
    df.to_excel("movie.xlsx")
    # add the external and internal urls to txt file
    with open("external1.txt", mode="w") as file:
        file.write("\n".join(external_urls))
    with open("internal1.txt", mode="w") as file:
        file.write("\n".join(internal_urls))
    #rendering to html table 
    return render_template('movie.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

    
"""
 AUTHOR: Kavya Konisa	
 NAME: get_movies_list
 PARAMETERS: URL, URL of the website
 PURPOSE: The function scrapes the movie data of such as name of the movie,rating and movie url.
 PRECONDITION: url passed should be a vaild url of the website.
 POSTCONDITION: It appends all the names, urls and rating to the respective list
 """
def get_movies_list(url):
    code = requests.get(url)
    plain= code.text
    soup = BeautifulSoup(plain,'html.parser')
    movie_names= []
    movie_rating= []
    movie_urls= []

    """
    NAME: get_movie_names
    PARAMETERS: soup, parsed html data of the url page
    PURPOSE: The Function to extract the movie names from HTML source code using BeautifulSoup. present in the url.
    PRECONDITION: soup passed should be in text format
    POSTCONDITION: It appends all the movie names to the total_movie_names list
    """
    def get_movie_names(soup):
        movie_names_all = soup.find_all('h2')[4:]
        movie_names_list = []
        for h2 in movie_names_all:
            movie_names_list.append(h2.a.text.strip())
            total_movie_names.append(h2.a.text.strip())
        # return movie_names_list
    """
    NAME: get_movie_rating
    PARAMETERS: soup, parsed html data of the url page
    PURPOSE: Function to extract the movie user rating from HTML source code using the BeautifulSoup.  present in the url.
    PRECONDITION: soup passed should be in text format.
    POSTCONDITION: It appends all the movie ratings to the total_movie_ratings list
    """
    def get_movie_rating(soup):
        movie_rating_all = soup.find_all('div', {'class': 'user_score_chart'})
        movie_rating_list = []
        for rating in movie_rating_all:
            movie_rating_list.append(rating.attrs['data-percent'])
            total_movie_ratings.append(rating.attrs['data-percent'])            

    """
    NAME: movie_urls
    PARAMETERS: soup, parsed html data of the url page
    PURPOSE: Function to extract the movie links from HTML source code using BeautifulSoup present in the url
    PRECONDITION: url passed should be a vaild url of the website.
    POSTCONDITION: It appends all the names, urls and rating to the respective list
    """
    def movie_urls(doc): 
        movies_urls = []
        base_url = 'https://www.themoviedb.org'
        movie_names_urls = doc.find_all('h2')[4:]
        for movie in movie_names_urls:
            movies_urls.append(base_url + movie.a['href'])
            total_movie_urls.append(base_url + movie.a['href'])
    movie_names= get_movie_names(soup)
    movie_rating = get_movie_rating(soup)
    movie_urls= movie_urls(soup)

"""
 AUTHOR: Dharani Kumar Vemuri	
 NAME: get_movie_details
 PARAMETERS: df, dataframe
 PURPOSE: The function calls all the functions that retrieves each movie details from the collected urls.
 PRECONDITION: The dataframe should contain movie url column 
 POSTCONDITION: It appends all the lists from the functions and add it to dataframe 
 """
def get_movie_details(df):
    for url in df['urls']:
        code = requests.get(url)
        plain= code.text
        details_soup = BeautifulSoup(plain,'html.parser')
        
        get_movie_overview(details_soup)
        get_movie_overview_info(details_soup)
        
        get_movie_left_columns(details_soup)
        
        get_movie_provider(details_soup)
        
        get_movie_keywords(details_soup)
        
        get_movie_cast(details_soup)
        global count_urls_visited
        count_urls_visited = count_urls_visited + 1
        if count_urls_visited < 50:
            get_all_urls(url)
    
    df['releaseDate'] = pd.Series(total_release_dates)
    df['genre'] = pd.Series(total_genres)
    df['running_time'] = pd.Series(total_running_time)
    df['certification'] = pd.Series(total_certifications)
    df['tagline'] = pd.Series(total_tagline)
    df['overview'] = pd.Series(total_overview)
    df['status'] = pd.Series(total_status)
    df['language'] = pd.Series(total_language)
    df['budget'] = pd.Series(total_budget)
    df['Revenue'] = pd.Series(total_revenue)
    df['Original Title'] = pd.Series(total_titles)
    df['Provider'] = pd.Series(total_providers)
    df['keywords'] = pd.Series(total_keywords)
    df['Cast'] = pd.Series(total_cast)


"""
 AUTHOR: Kavya Konisa
 NAME: get_movie_overview_info
 PARAMETERS: details_soup, parsed html data of the url page
 PURPOSE: The function scrapes the release date, genre, certification, running time from each url
 PRECONDITION: details_soup passed should be in text format.
 POSTCONDITION: It appends the release date, genre, certification, running time to the respective list
 """
def get_movie_overview_info(details_soup):
    div1_tags = details_soup.find('div', class_ = 'facts')
    if div1_tags is not None:
        release_date = div1_tags.find("span",class_="release").text.strip()[0:10]
        total_release_dates.append(release_date)
        genre =[]
        for a in div1_tags.find("span",class_="genres").find_all('a'):
            a= ''.join(a.text.strip())
            genre.append(a)
        total_genres.append(" ".join(genre))


        if div1_tags.find("span",class_="certification") is not None:
            certification = div1_tags.find("span",class_="certification").text.strip() 
        else:
            certification=None
        total_certifications.append(certification)

        if div1_tags.find("span",class_="runtime") is not None:
            running_time = div1_tags.find("span",class_="runtime").text.strip()
        else:
            running_time=None                       
        total_running_time.append(running_time)
    else:
        total_release_dates.append(None)
        total_genres.append(" ".join(None))

"""
 AUTHOR: Dharani Kumar Vemuri	
 NAME: get_movie_overview
 PARAMETERS: details_soup, parsed html data of the url page
 PURPOSE: The function scrapes the tagline and overview of each movie from each url
 PRECONDITION:details_soup passed should be in text format.details_soup passed should be in text format.
 POSTCONDITION: It appends the tagline and overview  to the respective list
 """
def get_movie_overview(details_soup):
    if details_soup.find('h3',class_='tagline') is not None:
        tagline= details_soup.find('h3',class_='tagline').text.strip()
    else:
        tagline= None
    total_tagline.append(tagline)

    if details_soup.find('div',class_='overview') is not None:
        p_tag = details_soup.find('div',class_='overview')
        overview= p_tag.find('p').text
    else:
        overview=None
    total_overview.append(overview)

"""
 AUTHOR: Dharani Kumar Vemuri	
 NAME: get_movie_provider
 PARAMETERS: details_soup, parsed html data of the url page
 PURPOSE:The function scrapes the  provider of the movie (where the movie is available to watch)
 PRECONDITION: details_soup passed should be in text format.
 POSTCONDITION: It appends provider of the movie to the total_providers list
 """   
def get_movie_provider(details_soup):
    provider =details_soup.find("div",class_="provider")
    if provider is not None:
        img = provider.find('img', alt=True)
        print(img)
        if img['alt'] is not None:
            if 'Available to Rent' in img['alt']:
                total_providers.append(img['alt'][28:])
            elif 'Now Streaming' in img['alt']:
                total_providers.append(img['alt'][17:])

        else:
            total_providers.append(None)
    else:
        total_providers.append(None)


"""
 AUTHOR: Dharani Kumar Vemuri	
 NAME: get_movie_left_col
 PARAMETERS:details_soup, parsed html data of the url page
 PURPOSE:The function scrapes the Budget, Original Language, Revenue, Status and Original Title of each movie from each url
 PRECONDITION: details_soup passed should be in text format.
 POSTCONDITION: It appends the Budget, Original Language, Revenue, Status and Original Title to the respective list
 """          
def get_movie_left_columns(details_soup):
    left_section = details_soup.find('section',class_='facts')
    for p_tag in left_section.find_all('p'):
        for strong_tag in p_tag.find('strong'):
            if strong_tag.text == 'Budget':
                total_budget.append(p_tag.text.split()[-1])

            elif strong_tag.text == 'Original Language':
                total_language.append(p_tag.text.split()[-1])

            elif strong_tag.text == 'Revenue':
                total_revenue.append(p_tag.text.split()[-1])

            elif strong_tag.text == 'Status':
                total_status.append(p_tag.text.split()[-1])

            elif strong_tag.text == 'Original Title':
                total_titles.append(p_tag.text.split()[-1])

"""
 AUTHOR: Vijay Thanikonda
 NAME: get_movie_keywords
 PARAMETERS: details_soup, parsed html data of the url page
 PURPOSE: The function scrapes the keywords of each movie in the movie url
 PRECONDITION: details_soup passed should be in text format.
 POSTCONDITION: It appends the keywords to the total_keywords list
 """
def get_movie_keywords(details_soup):
    keywords= details_soup.find('section',class_='keywords')
    list_items= keywords.find_all('a')
#     print(keywords)
    # print(list_items)
    list_items_text = []
    if keywords.find('p') is not None:
        list_items_text.append('No keywords have been added')
    elif list_items is not None:
        for list in list_items:
            list_items_text.append(list.text)
    print(list_items_text)

    total_keywords.append(list_items_text)

"""
 AUTHOR: Kavya Konisa
 NAME: get_movie_cast
 PARAMETERS: details_soup, parsed html data of the url page
 PURPOSE: The function scrapes the cast and crew of each movie in the movie url
 PRECONDITION: details_soup passed should be in text format.
 POSTCONDITION: It appends the cast and crew to the total_cast list
 """
def get_movie_cast(details_soup):
    cast= details_soup.find('div',class_='white_column')
    crew= cast.find('ol',class_ = 'people scroller' )
    if crew is not None:
        list_items= crew.find_all('li')
        list_items_text = []
        for p_tag in list_items:
            p_tag = p_tag.find("p")
            list_items_text.append(p_tag.text)
        total_cast.append(list_items_text)  
    else:
        total_cast.append(None)  

"""
 AUTHOR: Vijay Thanikonda
 NAME: get_all_urls
 PARAMETERS: URL, URL of the page in the website
 PURPOSE: The function crawls the website  and extract the urls in the website along with differentiating internal,external urls
 PRECONDITION: url passed should be a vaild url of the website.
 POSTCONDITION: It appends the internal and external urls to the internal and external urls sets
 """
def get_all_urls(url):
    code = requests.get(url)
    domain_name = urlparse(url).netloc
    plain= code.text
    soup = BeautifulSoup(plain,'html.parser')
    urls = set()
    base_url = 'https://www.themoviedb.org'
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "#" or  href is None:
            continue
        scheme = urlparse(href).scheme
        if len(scheme) > 0:
            if domain_name not in href:
                if validators.url(href):
                    if href not in external_urls:
                        print(f"External link: {href}")
                        external_urls.add(href)
                        all_urls.add(href)
                        urls.add(href)
                else:
                    print(f"Broken link: {href}")
                    broken_urls.add(href)
            else:
                print(f"Broken link: {href}")
                broken_urls.add(href)
            continue 

        href1 = base_url + href
        if validators.url(href1):
            print(f"Internal link: {href1}")
            internal_urls.add(href1)
            all_urls.add(href1)
            urls.add(href1)
        else:
            print(f"Broken link: {href1}")
            broken_urls.add(href1)
    # return urls





"""

 AUTHOR: Kavya Konisa, Dharani Kumar Vemuri	,Vijay Thanikonda
 FILENAME: movienames.py
 SPECIFICATION: It crawls through the TMDB website based on the given count, retrieves the movie information
 FOR: CS  5364 – Information Retrieval Section 001

"""

if __name__ == "__main__":
    app.run()
