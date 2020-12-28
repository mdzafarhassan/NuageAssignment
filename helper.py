import time
import requests
import multiprocessing
import threading


class ProductSearch():

    def __init__(self):
        self.products_list = []
        self.display_list = []
        self.api_done = []

    def __call__(self, keyword, req_data):
        self.keyword = keyword
        self.req_data = req_data

        p1 = threading.Thread(target=self.paytm_data)
        p2 = threading.Thread(target=self.tatacliq_data)
        p3 = threading.Thread(target=self.shopclues_data)

        p1.start()
        p2.start()
        p3.start()

        while len(self.display_list)<self.req_data:
            if len(self.products_list) > 0:
                self.display_list.append(self.products_list.pop(0))
            elif len(self.api_done) >= 3:
                break
            else:
                time.sleep(0.5)
        return self.display_list


    def paytm_data(self):
        page = 1
        error = 0
        while len(self.display_list)<self.req_data and not error:
            args = f"https://search.paytm.com/v2/search?userQuery={self.keyword}&page_count={page}&items_per_page=20"
            r = requests.get(args)
            try:
                data_dict = r.json().get('grid_layout')[:]
                data_dict[0]
            except Exception as ex:
                error = 1
                self.api_done.append('Paytm')
                return
            for i in data_dict:
                temp = {
                    'product_name': i.get('name'),
                    'product_url': i.get('url'),
                    'product_image': i.get('image_url'),
                    'product_price': i.get('offer_price'),
                    'store': 'Paytm'}
                self.add_product(temp)

            self.api_done.append('Paytm')
            page+=1

    def tatacliq_data(self):
        page = 1
        error = 0
        while len(self.display_list)<self.req_data and not error:
            args = f"http://api.shopclues.com/api/v11/search?q={self.keyword}&z=1&key=d12121c70dda5edfgd1df6633fdb36c0&page={page}"
            r = requests.get(args)
            try:
                data_dict = r.json().get('products')[:]
                data_dict[0]
            except Exception as ex:
                error = 1
                self.api_done.append('TataCliq')
                return

            for i in data_dict:
                temp = {'product_name': i.get('product'),
                        'product_url': i.get('product_url'),
                        'product_image': i.get('image_url'),
                        'product_price': i.get('price'),
                        'store': 'TataCliq'}
                self.add_product(temp)

            self.api_done.append('TataCliq')
            page+=1

    def shopclues_data(self):
        page = 0
        error = 0
        while len(self.display_list)<self.req_data and not error:
            args = f"https://www.tatacliq.com/marketplacewebservices/v2/mpl/products/serpsearch?type=category&channel=mobile&ageSize=20&typeID=al&page={page}&searchText={self.keyword}&isFilter=false&isTextSearch=true"
            r = requests.get(args)
            try:
                print(r.json())
                data_dict = r.json().get('facetdata').get('')[:]
                data_dict[0]
            except Exception as ex:
                error = 1
                self.api_done.append('ShopClue')
                return
            for i in data_dict:
                temp = {'product_name': i.get('productname'),
                        'product_url': i.get('url'),
                        'product_image': i.get('imageURL'),
                        'product_price': i.get('mrpPrice'),
                        'store': 'ShopClue'}
                self.add_product(temp)
            self.api_done.append('ShopClue')
            page+=1

    def add_product(self, product):
        if not product in self.products_list:
            self.products_list.append(product)
