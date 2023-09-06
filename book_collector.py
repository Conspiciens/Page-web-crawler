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
    book_urls = []
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
                selected_books[section] = [] 
            else: 
                selected_books[section] = []

            # Put all selected books into a dictionary to be stored for firebase
            for book in book_html.find_all('a'):
                if book['href'] not in book_urls and book['href'] != "#": 
                    book_info = get_book_info(book['href'])
                    selected_books[section].append(book_info) 
                    book_urls.append(book['href'])

            print(selected_books)

        else: 
            print("URL is unable to process: " + url)

def get_book_info(book_url): 
    book_data = {}

    response = requests.get(book_url, headers = headers)
    if response.status_code == 200: 
        soup = BeautifulSoup(response.content, 'html.parser')
        
        price = soup.find('span', itemprop="price") 
        name = soup.find('h1', itemprop="name")
        description = soup.find('div', itemprop="description")
        stock = soup.find('span', {'class': 'js-product-availability'})
        image = soup.find('img', {'class': 'js-qv-product-cover img-fluid'})

        if price != None: 
            price = price.get_text()
            book_data["price"] = price
        if name != None:  
            name = name.get_text() 
            book_data["name"] = name  
        if description != None: 
            description = description.get_text()
            book_data["description"] = description 
        if stock != None:
            stock = stock.get_text()
            if "\n\ue5ca\n" in stock: 
                stock = stock.replace("\n\ue5ca\n", "").strip()
            else: 
                stock = stock.replace("\ue14b\n", "").strip()
            book_data["stock"] = stock 
        if image != None: 
            book_data["image"] = image["src"]
        
        book_data["link"] = book_url

    return book_data
        
        
def init_firebase(): 
    ''' 
     Fill Firebase with the books selected
    '''
    
    for key, value in selected_books.items(): 
        for book in value: 
            if key != None: 
                db.collection(key).document().set(book)


def main(): 
    request_url("https://www.livingstream.com/en/")
    init_firebase()


if __name__ == '__main__': 
    main()