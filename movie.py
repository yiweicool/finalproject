from bs4 import BeautifulSoup
import json
import requests
import secrets # file that contains your OAuth credentials

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
        return "{} ({}): {}".format(self.name,self.year,self.link)

    pass


def build_genre_url_dict():
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
    search_genre = soup.find('ul', class_='genrelist')
    child_lis = search_genre.find_all('li')
    dict = {}
    for li in child_lis:
        movies_genre = li.find("div").string
        print(movies_genre)
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
        print("Fetching")
        time.sleep(1)
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
    year = soup.find("time").string[-4:]
    ratings = soup.find("span",class_="mop-ratings-wrap__percentage").string.strip()
    rating_count = soup.find("small", class_="mop-ratings-wrap__text--small").sring
    #print(year)
    return SingleMovie(name, year, ratings, rating_count)

    pass







"""def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and
    repeatably identify an API request by its baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs

    Returns
    -------
    string
        the unique key as a string
    '''
    #TODO Implement function

    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key

    pass

def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs

    Returns
    -------
    dict
        the data returned from making the request in the form of
        a dictionary
    '''
    #TODO Implement function
    resp = requests.get(baseurl, params)
    results_object = json.loads(resp.text)
    #print(results_object)
    return results_object
    pass """

def make_request_with_cache(baseurl, title):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new
    request, save it, then return it.

    Parameters
    ----------
    baseurl: string
    The URL for the API endpoint
    hashtag: string
    The hashtag to search (i.e. “#2020election”)
    count: int
    The number of tweets to retrieve

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    #TODO Implement function
    params = {}
    params['s']= title
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



if __name__ == "__main__":


    CACHE_DICT = open_cache()

    baseurl = "http://www.omdbapi.com"
    title = "batman"
    movie_data = make_request_with_cache(baseurl, title)
    print(movie_data)
