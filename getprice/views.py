from django.shortcuts import render, HttpResponse, redirect
import requests
from bs4 import BeautifulSoup

# Our Web scraper
def webScrape(query):
    #url = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=2013+Panini+Prizm+Giannis+Antetokounmpo+Rookie+Card+graded&_sacat=0&LH_TitleDesc=0&_fsrp=1&LH_PrefLoc=3&_sop=13&_osacat=0&_odkw=2013+Panini+Prizm+Giannis+Antetokounmpo+Rookie+Card&rt=nc&_dcat=214&LH_Sold=1&_oaa=1"
    #url = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=2007+Patrick+Kane+Upper+Deck+Young+Guns+Rookie+Card+mint&_sacat=0&LH_TitleDesc=0&_fsrp=1&LH_PrefLoc=3&_sop=13&_osacat=0&_odkw=2007+Patrick+Kane+Upper+Deck+Young+Guns+Rookie+Card+min&LH_Sold=1"
    #short_url = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=Patrick+Kane+Young+Guns+Rookie+Card+Mint+2007&LH_Sold=1"

    url = (f'https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={query}&LH_Sold=1')

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    listings = soup.find_all(class_='s-item__wrapper')

    avg_price = 0.00

    if len(listings)<5:
        return ("not enough data")

    else:    
        for listing in listings[0:5]:
            #print(listing)
            #title = soup.find(class_='s-item__title').get_text()
            price = listing.find(class_='POSITIVE').get_text()
            price = price.replace("$", "")
            price = float(price)

            shipping = listing.find(class_='s-item__shipping').get_text()
            if shipping == "Free shipping":
                shipping = 0.00
            else:
                shipping = shipping.replace("+$", "")
                shipping = shipping.replace(" shipping", "")
                shipping = float(shipping)
            
            # to go from thumnail to large img remove 'thumbs/' and remplace '225' w/ '500
            # https://i.ebayimg.com/thumbs/images/g/JzgAAOSwcwRextIc/s-l225.jpg
            img = listing.find(class_='s-item__image-img')['src']
            img_url = img.replace("thumbs/", "")
            img_url = img_url.replace("225", "500")
            
            avg_price += price
            avg_price += shipping
    
    avg_price = float(avg_price/5)
    avg_price = round(avg_price, 2)
    avg_price = "{:.2f}".format(avg_price)

    return [img_url, avg_price]


# Create your views here.
def index(request):
    return render(request, 'index.html')

def search(request):
    if request.method == "POST":
        query = ""
        request.session['player_name'] = request.POST['player_name']
        query += " " + request.POST['player_name']

        query += " " + request.POST['card_keyword']
        request.session['keyword'] = request.POST['card_keyword']

        query += " " + request.POST['card_brand']
        request.session['brand'] = request.POST['card_brand']

        query += " " + request.POST['card_year']
        request.session['year'] = request.POST['card_year']

        request.session['mint'] = request.POST['is_mint']
        mint = request.POST['is_mint']
        if (mint):
            query += " " + "mint"
        
        query = query.replace("  ", " ")
        query = query.replace(" ", "+")
        data = webScrape(query)
        request.session['img_url'] = data[0]
        request.session['avg_price'] = data[1]

    return redirect(index)