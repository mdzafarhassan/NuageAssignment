from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from helper import ProductSearch
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db=SQLAlchemy(app)


class ProductMaster(db.Model):
    id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1), primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_url = db.Column(db.String(500), nullable=False)
    product_image = db.Column(db.String(500), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    store = db.Column(db.String(25), nullable=False)
    search_tag = db.Column(db.String(200), nullable=False)

    def __rep__(self):
        return '<Task %r>'  % self.id

    def __str__(self):
        return self.product_name

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        keyword = request.form['search_keyword']
        if not keyword or keyword=='':
            return render_template('index.html')

        p1 = threading.Thread(target=update_db_data, args=[keyword])
        p1.start()

        product_list = ProductMaster.query.filter(ProductMaster.product_name.ilike(f"%{keyword}%"), ProductMaster.search_tag.ilike(f"%{keyword}%"))[:50]
        return render_template('index.html', products=product_list, data='Search Result')
    return render_template('index.html')


def update_db_data(keyword):
    products = ProductSearch()
    product_list = products(keyword)
    for product in product_list:
        try:
            ProductMaster.query.filter_by(product_name=product['product_name'], product_url=product['product_url'])[0]
        except:
            row = ProductMaster(product_name=product['product_name'], product_url=product['product_url'], product_image=product['product_image'], product_price=product['product_price'], store=product['store'], search_tag=keyword)
            db.session.add(row)
            db.session.commit()
            pass

if __name__ == "__main__":
    app.run(debug=True)
