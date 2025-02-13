from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from io import BytesIO

#limited, so not an option
def get_product_go_upc(self,upc):
    print(upc)
    try:
        headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}

        response=requests.get(f"https://smartlabel.org/product-search/?product={upc}",headers=headers)
        print(response)
        if response.status_code == 200:
            soup=bs(response.text,"html.parser")
            results_table=soup.find_all("div",{"id":"search-results"})
            print(results_table,response.text)
            for r in results_table:
                try:
                    links=r.find_all('a',{'target':'_blank'})
                    print(links)
                except Exception as e:
                    print(e)


    except Exception as e:
        print(e)
        print(repr(e))
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        a=get_product_go_upc(None,upc=sys.argv[1])
        print(a)
    else:
        print(f"please provide a upc via arg1, i.e. python3 ./{sys.argv[0]} $UPC")
