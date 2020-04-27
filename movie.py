from bs4 import BeautifulSoup
import json
import requests
import time
import sqlite3
import secrets # file that contains your OAuth credentials
import plotly.graph_objs as go


# Request header
headers = {
    'User-Agent': 'UMSI 507 Course final Project',
    'From': 'yiweixu@umich.edu',
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

CACHE_FILENAME = "movie_cache.json"
CACHE_DICT = {}

API_KEY = secrets.MOVIE_API_KEY


class SingleMovie:


    def __init__(self, name = "No Name", year = "No Year", rating = "No Rating", rating_count= "No Rating Count"):
        self.name = name
        self.year = year
        self.rating = rating
        self.rating_count = rating_count

    def info(self):
        return "{} ({}): {}".format(self.name,self.year,self.rating)

    pass

def build_movie_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.imdb.com/chart/moviemeter/

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a movie name and value is the url

    '''
    baseurl = "https://www.rottentomatoes.com/"
    url = 'https://www.rottentomatoes.com/top'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    """search_movie = soup.find('tbody', class_='lister-list')
    child_trs = search_movie.find_all('tr')
    #print(child_trs)
    dict = {}
    for tr in child_trs:
        child_td = tr.find("td", class_ = "titleColumn")
        for a in child_td.find('a', href=True):
            movie_name = a.string.lower()
            #print(a)
            movie_url = baseurl + child_td.find('a', href=True)['href']
            dict[movie_name] = movie_url
        for s in child_td.find('span', class_="secondaryInfo"):
            movie_year = s.string.lower()
            #print(movie_year)"""

    search_genre = soup.find('ul', class_='genrelist')
    child_lis = search_genre.find_all('li')
    dict = {}
    for li in child_lis:
        movies_genre = li.find("div").string
        # print(movies_genre)
        for a in li.find_all('a', href=True):
            dict[movies_genre] = baseurl + a['href']
    return dict
    pass

def construct_unique_key(baseurl, params):
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key


def load_cache(): # called only once, when we run the program
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache): # called whenever the cache is changed
    cache_file = open(CACHE_FILENAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        #print("Fetching")
        time.sleep(0.1)
        response = requests.get(url, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def get_movie_instance(movie_url):
    '''Make an instances from a movieURL.

    Parameters
    ----------
    site_url: string
        The URL for a movie page

    Returns
    -------
    instance
        a single movie instance
    '''
    CACHE_DICT = load_cache()
    url = movie_url
    #response = requests.get(url)
    url_text = make_url_request_using_cache(url, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')

    name = soup.find("h1", class_="mop-ratings-wrap__title mop-ratings-wrap__title--top").string
    year = soup.find("time").string.strip()[-4:]
    ratings = soup.find("span",class_="mop-ratings-wrap__percentage").string.strip()
    rating_count = soup.find("small", class_="mop-ratings-wrap__text--small").sring
    #print(year)
    return SingleMovie(name, year, ratings, rating_count)

    pass

def get_novies_for_genre(genre_url):
    '''Make a list of movie site instances from rotten tomatoes URL.

    Parameters
    ----------
    genre_url: string
        The URL for a genre page in rotten tomatoes

    Returns
    -------
    list
        a list of movie instances
    '''
    BASE_URL = 'https://www.rottentomatoes.com'
    #STATE_PATH = '/state/index.htm'
    #state_url = BASE_URL + STATE_PATH

    movies = []
    i = 1

    response = requests.get(genre_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    movie_parent = soup.find('table', class_="table")

    movie_trs = movie_parent.find_all('tr')
    #print(movie_trs[1])

    for tr in movie_trs[1:101]:
        tds = tr.find_all("td")
        #print(tds[2])
        movie_link_tag = tds[2].find('a',class_="unstyled articleLink")
        #print(movie_link_tag)
        movie_detail_path = movie_link_tag['href']
        movie_detail_url = BASE_URL + movie_detail_path

        movie = get_movie_instance(movie_detail_url)
        #parks.append("[{}] {}".format(i, park))
        movies.append(movie)


    return movies
    pass

def make_request(baseurl, params):
    print("Fetching")
    resp = requests.get(baseurl, params)
    results_object = json.loads(resp.text)
    #print(results_object)
    return results_object
    pass

def get_detail_info(movie_object):
    '''Get detailed movie information.

    Parameters
    ----------
    baseurl: string
    The URL for the API endpoint
    hashtag: string
    The movie to search
    count: int
    The number of tweets to retrieve

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    #TODO Implement function
    baseurl = "http://www.omdbapi.com"
    params = {}
    params['t']= movie_object.name
    params['apikey'] = API_KEY
    #params['page'] = 100
    #params['count'] = count
    #print(param_diction)
    unique_i = construct_unique_key(baseurl, params)
    if unique_i in CACHE_DICT:
        return CACHE_DICT[unique_i]
    else:
        result = make_request(baseurl, params)
        #resp = requests.get(baseurl,params,auth=oauth)
        #print(resp.text)
        #CACHE_DICT[unique_i]= json.loads(resp.text)
        CACHE_DICT[unique_i] = make_request(baseurl, params)
        dumped_json_cache = json.dumps(CACHE_DICT)
        fw = open(CACHE_FILENAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICT[unique_i]


def Show_movies():

    while True:

        i = 1
        genre_dict = build_movie_url_dict()
        genre_list = []
        for key in genre_dict.keys():
            genre_list.append(key)
        #genre_list = genre_dict.keys()
        #print(type(genre_list))
        for genre in genre_list:
            print("[{}] {}".format(i, genre))
            i = i+1

        resp = input("Enter the genre number you want to know or exit \n")
        selected_genre = genre_list[int(resp)]
        list_sites = []

        if int(resp) <= 100 and int(resp) >= 0:

            print("List of movies in " + selected_genre)
            site_url = genre_dict[selected_genre]
            movies = get_novies_for_genre(site_url)

            """for park in parks:
                list_sites.append(park.info())
                #print("[{}] {}".format(i, park.info()))"""

            return movies

        elif resp == "exit":
            break
        else:
            print("Wrong number, please input number between 1 and 100")
            break

def createmovie():

    conn = sqlite3.connect("Movietable.sqlite")
    cur = conn.cursor()

    drop_movies = '''
        DROP TABLE IF EXISTS "Movies";
    '''

    create_movies = '''
        CREATE TABLE IF NOT EXISTS "Movies" (
            "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Title"  TEXT NOT NULL,
            "Year"   TEXT NOT NULL,
            "CountryID" INTEGER NOT NULL,
            "GenreID"  INTEGER NOT NULL,
            "Rating_IMDB"    TEXT,
            "Rating_Tomato" TEXT,
            "Rating_meta" TEXT
        );
    '''

    cur.execute(drop_movies)
    cur.execute(create_movies)

    conn.commit()


if __name__ == "__main__":

    list_movies = Show_movies()
    i =1
    createmovie()
    for movie in list_movies:
        print("[{}] {}".format(i, movie.info()))
        i = i+1



    while True:

        choose_number = input("""See the ratings comparison, enter "Display",
        Enter a number in the list to see a specifc movie or enter back and exit \n""")
        if choose_number == "back":
            list_movies = Show_movies()
            i =1
            for movie in list_movies:
                print("[{}] {}".format(i, movie.info()))
                i = i+1
        elif choose_number == "exit":
            break
        elif choose_number.isnumeric() and int(choose_number) <= len(list_movies):

            movie_object = list_movies[int(choose_number) - 1]

            print("---------------------")
            print("The detail movie information of " + movie_object.name)
            print("---------------------")

            detail_info = get_detail_info(movie_object)
            #print(detail_info)

            title = detail_info["Title"]
            year = detail_info["Year"]
            length = detail_info["Runtime"]
            rating_imdb = detail_info["imdbRating"]
            rating_rt = detail_info["Ratings"][1]["Value"]
            rating_meta = detail_info["Metascore"]
            genre = detail_info["Genre"]
            director = detail_info["Director"]
            plot = detail_info["Plot"]
            language = detail_info["Language"]
            country = detail_info["Country"]
            print("Title :        {}".format(title))
            print("Release Year : {}".format(year))
            print("Movie Length : {}".format(length))
            print("Movie Genre :  {}".format(genre))
            print("Director :     {}".format(director))
            print("Plot :         {}".format(plot))
            print("Language :     {}".format(language))
            print("Country :      {}".format(country))
            print("IMDB Rating :  {}".format(rating_imdb))
            print("Rotten Tomatoes Rating : {}".format(rating_rt))
            print("Metacritic Rating :      {}".format(rating_meta))
            display= input("Do you want to see the rating comparison?     y/n")
            if display == "y":
            
                xvals = ["IMDB","Rotten Tomatoes","Metacritic"]
                yvals = [float(rating_imdb),int(rating_rt[:-1])/10,int(rating_meta)/10]

                bar_data = go.Bar(x=xvals, y=yvals)
                basic_layout = go.Layout(title="Ratings Bar Graph of" + title)
                fig = go.Figure(data=bar_data, layout=basic_layout)

                fig.show()


        #elif choose_number == "display":
