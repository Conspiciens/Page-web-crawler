import requests 
import firebase_admin
from bs4 import BeautifulSoup
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://book-storage-69944.firebaseio.com/'
})

db = firestore.client() 

urls = []
selected_books = {}
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}
first_page = False 

def request_url(url): 
    '''
     Request the given url and retrieve any urls + books links 
    '''
    urls.append(url)

    # Iterate through the urls as they're appended 
    for url in urls: 
        response = requests.get(url, headers = headers)
    
        if response.status_code == 200: 
            soup = BeautifulSoup(response.content, 'html.parser')
            book_html = soup.find('div', {'class': 'products'})

            # First page retrieve all vital links 
            if first_page == False:
                top_urls_html = soup.find('ul', {'class': 'top-menu'})
                if top_urls_html == None: 
                    break 
                top_urls = top_urls_html.find_all('a')
                for drop_url in top_urls: 
                    if drop_url['href'] not in urls: 
                        urls.append(drop_url['href'])
            
            if book_html == None:
                break 

            section = soup.find('h1', {'class': 'h2'})
            if section != None: 
                section = section.get_text().split(' ', 1)[1]
                print(section)
                selected_books[section]= []
            else: 
                selected_books[section] = []

            # Put all selected books into a dictionary to be stored for firebase
            for book in book_html.find_all('a'):
                if book['href'] not in selected_books[section] and book['href'] != "#": 
                    selected_books[section].append(book['href']) 

        else: 
            print("URL is unable to process: " + url)
        
def init_firebase(): 
    ''' 
     Fill Firebase with the books selected
    '''
    
    for key, value in selected_books.items(): 
        for book in value: 
            if key != None: 
                link = {"link": book}
                db.collection(key).document().set(link)


def main(): 
    request_url("https://www.livingstream.com/en/")
    init_firebase()


if __name__ == '__main__': 
    main()