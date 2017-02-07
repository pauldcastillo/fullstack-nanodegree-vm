from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

restuarant_url = '/restaurant/<int:restaurant_id>'
menu_id_url = restuarant_url + '/menu/<int:menu_id>'

def render_message(message):
    return render_template('message.html', message=message)

@app.route('/')
@app.route('/restaurants')
@app.route('/restaurants/')
def all_restaurants():
    #restaurants = session.query(Restaurant).all()
    if len(restaurants) <= 0:
        return render_template(
            'all_restaurants.html', restaurants=0)
    else:
        return render_template(
            'all_restaurants.html', restaurants=restaurants)

@app.route('/restaurant/new')
@app.route('/restaurant/new/')
def new_restaurant():
    return render_template('new_restaurant.html')

@app.route(restuarant_url)
@app.route(restuarant_url + '/')
@app.route(restuarant_url + '/menu')
@app.route(restuarant_url + '/menu/')
def restaurant_menu(restaurant_id):
    #restaurant = (
    #    session.query(Restaurant).filter_by(id = restaurant_id).first())
    #items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    if len(items) <= 0:
        return render_template('menu.html',
                               restaurant=restaurant,
                               items=0)
    else:
        return render_template('menu.html',
                               restaurant=restaurant,
                               items=items)

@app.route(restuarant_url + '/edit')
@app.route(restuarant_url + '/edit/')
def edit_restaurant(restaurant_id):
    #restaurant = (
    #    session.query(Restaurant).filter_by(id = restaurant_id).first())
    if restaurant:
        return render_template('edit_restaurant.html',
                               restaurant=restaurant,
                               restaurant_id=restaurant_id)
    else:
        return redirect(url_for('all_restaurants'))

@app.route(restuarant_url + '/delete')
@app.route(restuarant_url + '/delete/')
def delete_restaurant(restaurant_id):
    #restaurant = (
    #    session.query(Restaurant).filter_by(id = restaurant_id).first())
    if restaurant:
        return render_template('delete_restaurant.html',
                               restaurant=restaurant,
                               restaurant_id=restaurant_id)
    else:
        return redirect(url_for('all_restaurants'))

@app.route(restuarant_url + '/menu/new')
@app.route(restuarant_url + '/menu/new/')
def new_menu_item(restaurant_id):
    if request.method == 'POST':
        # new_item = MenuItem(name=request.form['name'],
        #                    restaurant_id=restaurant_id)
        #session.add(new_item)
        #session.commit()
        #flash("New menu item, %s, created!" % new_item.name)
        #return redirect(url_for('restaruant_menu', restaurant_id=restaurant_id))
        pass
    else:
        return render_template('new_menu_item.html',
                               restaurant_id=restaurant_id)


@app.route(menu_id_url + '/edit')
@app.route(menu_id_url + '/edit/')
def edit_menu_item(restaurant_id, menu_id):
    #edited_item = session.query(MenuItem).filter_by(id = menu_id).one()
    edited_item = item
    if request.method == 'POST':
    #    if request.form['name']:
    #        old_name = edited_item.name
    #        edited_item.name = request.form['name']
    #        session.add(edited_item)
    #        session.commit()
    #        flash('%s is now named %s!' % (old_name, edited_item.name))
    #    return redirect(url_for('restaruant_menu',
    #                    restaurant_id=restaurant_id))
        pass
    else:
        return render_template('edit_menu_item.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               item=edited_item)

@app.route(menu_id_url + '/delete')
@app.route(menu_id_url + '/delete/')
def delete_menu_item(restaurant_id, menu_id):
    # to_delete_item = session.query(MenuItem).filter_by(id = menu_id).one()
    to_delete_item = item
    if request.method == 'POST':
    #    if request.form['Delete']:
    #        session.delete(to_delete_item)
    #        session.commit()
    #        flash('%s was deleted.' % to_delete_item.name)
    #    return redirect(url_for('restaruant_menu',
    #                            restaurant_id=restaurant_id))
        pass
    else:
        return render_template('delete_menu_item.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               item=to_delete_item)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)