from gevent import monkey; monkey.patch_all()
from bottle import route, run, response
import pandas as pd
import bottle
import commands
import operator
import json
import razorpay
import googlemaps
from datetime import datetime
import random
import requests
from pprint import pprint
import redis_functions as rd
from redis_functions import *
app = bottle.app()

global daily_confirmed_carts
global daily_converted_value
global daily_delivered_carts

global y_converted_carts
global y_converted_value
global r_converted_carts
global r_converted_value
global o_converted_carts
global o_converted_value
global k_converted_carts
global k_converted_value

daily_converted_value = "daily_converted_value"
daily_confirmed_carts = "daily_confirmed_carts"
daily_delivered_carts = "daily_delivered_carts"
y_converted_value = "y_converted_value"
y_converted_carts = "y_converted_carts"
o_converted_carts = "o_converted_carts"
o_converted_value = "o_converted_value"
r_converted_value = "r_converted_value"
r_converted_carts ="r_converted_carts"
k_converted_value = "k_converted_value"
k_converted_carts ="k_converted_carts"

global orders
orders = {}
global orders_branch_R
orders_branch_R={}
global orders_branch_O
orders_branch_O={}
global orders_branch_Y
orders_branch_Y={}
global orders_branch_K
orders_branch_K={}
global busy

global shutdown
shutdown = []

busy = False

@app.route('/write_order/<d>')
def write_order(d):
	global orders
	global busy
	while busy==True:
		pass
	busy = True
	orders.append(d)
	busy = False
	yield "success"

@app.route('/is_carts/<identity>')
def is_carts(identity):
	key = get_cart_id(identity)
	cart = get_hash(key)
	if(key_exists(key)):
		if(cart!={}):
			yield "True"
		else:
			yield "False"
	else:
		yield "False"

@app.route('/<identity>/set_payment_key/<pass_key>')
def set_payment_key(identity,pass_key):
	key = 'user:'+ str(identity) +':payment_key'
	set_key(key,str(pass_key))

@app.route('/<identity>/get_payment_status')
def get_payment_status(identity):
	key = 'user:'+str(identity)+':payment_key'
	pay_key = get_key(key)
	result = payment(pay_key)
	yield result["status"]

@app.route('/get_cart_price/<id>')
def get_cart_price(id):
	global dishes_db
	carthotel = get_key("user:" + str(id) + ":assigned_rest")
	key = get_cart_id(id)
	cart = get_hash(key)
	prices = {"oos":[]}
	total = 0
	for item in cart:
		if(dishes_db[dishes_db["name"]==item][carthotel].tolist()[0]=="In"):
			if(int(cart[item])>0):
				#print item
				val =  dishes_db[dishes_db["name"] == item]["price"].tolist()[0]
				prices[item] = (int(val) ,int(cart[item]))
				a,b = prices[item]
				total += a*b
		else:
			delete_hash_field(key,item)
			prices["oos"].append(item)
	prices["total"] = total
	expire_key_in(key,3600)
	key = "user:"+str(id)+":details"
	if(key_exists(key) and hash_field_exists(key,"address") and hash_field_exists(key,"number")):
		prices["flag"] = True
	else:
		prices["flag"] = False
	key = "rest_discount"
	prices["discount"]=prices["total"]*int(get_key(key))/100
	return prices

def rpushl(key,value):
	command = "redis-cli rpush " + key + " " + value
	commands.getoutput(command)

global link
link = "https://bfe82c76.ngrok.io/"

@app.route('/cart/<identity>/add/<d>')
def change_cart(identity, d):
	global link
	call = link +"cart/" + str(identity) + "/add/" + json.dumps(d)
	d = d.lower()
	data = {"incart":[],"oos":[]}
	d = json.loads(d)
	carthotel = get_key("user:" + str(identity) + ":assigned_rest")
	key = "user:"+ identity +":cart:"+str(int(set_count("user:"+identity+":confirmed_carts"))+1)
	locflag = get_key("user:" + str(identity) + ":cart:" + str(int(set_count("user:"+identity+":confirmed_carts"))+1) + ":flag")
	print carthotel
	print locflag
	if locflag == '0':
		print 0
		data["locflag"] = 0
	else:
		print 1
		if carthotel == '':
			print 2
			set_key("user:"+str(identity)+":calls",call)
			set_key("user:"+str(identity)+":call-tags","add")
			return {"call":call,"locflag":2,"tag":"add"}
		else:
			print 3
			set_key("user:"+str(identity)+":calls",call)
			set_key("user:"+str(identity)+":call-tags","add")
			return {"call":call,"locflag":1,"tag":"add"}
	print d
	for item in d:
		if(dishes_db[dishes_db["name"]==item][carthotel].tolist()[0]=="In"):
			incr_hash_field_by(key,item,d[item])
			data["incart"].append(item)
		else:
			data["oos"].append(item)
	expire_key_in(key,3600)
	return data

@app.route('/cart/<identity>/cancel')
def cancel(identity):
	key = "user:"+ str(identity) +":cart:"+str(int(set_count("user:"+identity+":confirmed_carts"))+1)
	expire_key_in(key,1)

from geopy import distance , Point
global Hotel_locations
#Hotel_locations = {"Vasant_kunj":Point("28.5195110 77.1665260")}
Hotel_locations = {"Residency_Road":Point("12.9655 77.5989"),"Old_Airport_Road":Point("12.9603 77.6459"),"Yelahanka":Point("13.1047 77.5844"),"Koramangala":Point("12.940539 77.614897")}

@app.route('/add_new_hotel/<name>/<lat>/<longi>')
def add_new_hotel(name,lat,longi):
    global Hotel_locations
    Hotel_locations[name] = Point(lat+" "+longi)

def changestock(dname):
	Hotel_locations = ['Residency_Road','Old_Airport_Road','Koramangala','Yelahanka']
	global shutdown,dishes_db
	count = len(shutdown)
	if dname == 'Hotel':
		if count == 4:
			dishes_db['stock'] = dishes_db['stock'].replace('In','Out')
		else:
			dishes_db['stock'] = dishes_db['stock'].replace('Out','In')
	else:
		for ht in Hotel_locations:
			if ht not in shutdown:
				if(dishes_db[dishes_db['name']==dname][ht].tolist()[0]== 'Out'):
					count = count + 1
		if(count == 4):
			dishes_db.loc[dishes_db['name']==dname,'stock'] = 'Out'
		else:
			dishes_db.loc[dishes_db['name']==dname,'stock'] = 'In'
			with open('dishes15.txt','w') as outfile:
				json.dump(dishes_db.to_json(orient='index'),outfile)

@app.route('/shutdown_hotels/<hotel>')
def shutdownhotels(hotel):
        global shutdown
        if hotel in Hotel_locations:
                u = 'http://0.0.0.0:7000/shutingdown/'
                h ={ 'content-type': 'application/json; charset=utf-8'}
                r = requests.get(url=u+hotel,headers=h)
                if hotel in shutdown:
                        dishes_db[hotel] = dishes_db[hotel].replace("Out","In")
                        shutdown.remove(hotel)
                        changestock('Hotel')
                        return json.dumps({"status":"Hotel Alive!!"})
                else:
                     	shutdown.append(hotel)
                        dishes_db[hotel] = dishes_db[hotel].replace("In","Out")
                        changestock('Hotel')
                        return json.dumps({"status":"Hotel is Shutdown"})
        else:
             	return  json.dumps({"status":"Hotel name in correct","data" : Hotel_locations.keys()})

@app.route('/get_nearest_hotel/<lat>/<longi>')
def get_nearest_hotel(lat,longi):
	result = []
	for locations in Hotel_locations:
			p1 = Point(lat+" "+longi)
			dist = distance.distance(Hotel_locations[locations],p1).kilometers
			result.append((locations,dist))
	for a,b in result:
		if(b<=5):
			return a
	return None

@app.route('/cart/<identity>/show')
def show(identity):
	res = {"oos":[]}
	key = "user:"+ str(identity) +":cart:"+str(int(set_count("user:"+identity+":confirmed_carts"))+1)
	carthotel = get_key("user:" + str(identity) + ":assigned_rest")
	print carthotel
	if key_exists(key) == False:
		return json.dumps(res)
	if carthotel == '':
		return json.dumps(res)
	result = get_hash(key)
	for item in result:
		if(int(result[item])<=0):
			delete_hash_field(key,item)
		else:
			if(dishes_db[dishes_db["name"]==item][carthotel].tolist()[0] == "In"):
				res[item] = [dishes_db[dishes_db["name"] == item]["price"].tolist()[0],result[item]]
			else:
				delete_hash_field(key,item)
				res["oos"].append(item)
	expire_key_in(key,3600)
	return json.dumps(res)

@app.route('/cart/<identity>/replace/<d>')
def replace(identity,d):
	print "Enter"
	key = "user:"+ str(identity) +":cart:"+str(int(set_count("user:"+identity+":confirmed_carts"))+1)
	delete_key(key)
	d=json.loads(d)
	data = {"incart":[],"oos":[]}
	carthotel = get_key("user:" + str(identity) + ":assigned_rest")
	print carthotel
	for item in d:
		if(dishes_db[dishes_db["name"]==item][carthotel].tolist()[0]=="In"):
			set_hash_field(key,item,d[item])
			data["incart"].append(item)
		else:
			data["oos"].append(item)
	print "expiring"
	expire_key_in(key,3600)
	print "exit"
	yield json.dumps(data)

def get_details(identity):
	data = {}
	lat_long = get_key("user:"+str(identity)+":cur_address")
	lat_long = lat_long.split(",")
	key = "user:" + str(identity) + ":details"
	data['address'] = get_hash_field(key,"address").replace("_"," ")
	data['number'] = str(get_hash_field(key,"number")) #get_geocode(lat_long[0],lat_long[1])
	total = get_cart_price1(identity)
	data['total'] = total['total']
	data['discount'] = total["discount"]
	data['name'] = get_hash_field(key,"name").replace("_"," ")
	return data

def randnum():
	return random.randint(1,50)

@app.route('/discount/<num>')
def disc(num):
	key = "rest_discount"
	set_key(key,str(num))
	return "Success"

@app.route('/cart/<identity>/confirm')
def confirm10(identity):
	global orders_branch_Y
	global orders_branch_O
	global orders_branch_R
	global orders_branch_K
	k="user:"+str(identity)+":assigned_rest"
	closest = get_key(k)

	key = "user:" + identity + ":confirmed_carts"
	member = "user:"+identity+":cart:"+str(int(set_count("user:"+identity+":confirmed_carts"))+1)
	persist_key(member)

	set_add(key,member)
	key = "user:"+str(identity)+":last_cart"
	set_key(key,member)
	order = get_hash(member)

	key = "user:"+str(identity)+":ordered_items"
	for item in order:
		ss_member_increment_by(key,item,"1")
	key = "user:"+str(identity)+":cart_status"
	set_key(key,"pending")

	for item in order:
		ss_member_increment_by(key,item,"1")
	key = "user:"+str(identity)+":history:category"
	for item in order:
		val =  dishes_db[dishes_db["name"] == item]["category"].tolist()[0]
		ss_member_increment_by(key,val,"1")
	key = "user:"+str(identity)+":history:base_ing"
	for item in order:
		val =  dishes_db[dishes_db["name"] == item]["base_ing"].tolist()[0]
		ss_member_increment_by(key,val,"1")
	key = "user:"+str(identity)+":history:v_n"
	for item in order:
		val =  dishes_db[dishes_db["name"] == item]["v_n"].tolist()[0]
		ss_member_increment_by(key,val,"1")
	key = "user:"+str(identity)+":cart_status"
	set_key(key,"pending")
	key = "user:" + str(identity) + ":tic"
	set_key(key,get_time_stamp())

	data = {"id":str(identity),"cart":order,"data":get_details(identity),"status":"pending"}
	print (data)

	if closest in "Residency_Road":
		orders_branch_R[str(identity)] = data

	elif closest in "Yelahanka":
		orders_branch_Y[str(identity)] = data

	elif closest in "Old_Airport_Road":
		orders_branch_O[str(identity)] = data

	elif closest in "Koramangala":
		orders_branch_K[str(identity)] = data

	global orders

	orders[str(identity)] = data
	#write_order(data)
	print(data)



'''
0 pending
1 accept/reject
2 in_kitchen
3 out_for_delivery
4 delivered
'''

@app.route('/cart/<identity>/accept')
def confirm4(identity):
	key = "user:"+str(identity)+":cart_status"
	set_key(key,"order_accepted")
	if str(identity) in orders_branch_O:
		orders_branch_O[str(identity)]['status'] = 'order_accepted'
	elif str(identity) in orders_branch_Y:
		orders_branch_Y[str(identity)]['status'] = 'order_accepted'
	elif str(identity) in orders_branch_R:
		orders_branch_R[str(identity)]['status'] = 'order_accepted'
	elif str(identity) in orders_branch_K:
		orders_branch_K[str(identity)]['status'] = 'order_accepted'
	orders[str(identity)]['status'] = 'order_accepted'

@app.route('/cart/<identity>/reject')
def confirm5(identity):
	key = "user:"+str(identity)+":cart_status"
	set_key(key,"rejected")
	if str(identity) in orders_branch_O:
		orders_branch_O[str(identity)]['status'] = 'rejected'
	elif str(identity) in orders_branch_Y:
		orders_branch_Y[str(identity)]['status'] = 'rejected'
	elif str(identity) in orders_branch_R:
		orders_branch_R[str(identity)]['status'] = 'rejected'
	elif str(identity) in orders_branch_K:
		orders_branch_K[str(identity)]['status'] = 'rejected'
	orders[str(identity)]['status'] = 'rejected'
	orders.pop(str(identity),None)
	orders_branch_O.pop(str(identity),None)
	orders_branch_Y.pop(str(identity),None)
	orders_branch_R.pop(str(identity),None)
	orders_branch_K.pop(str(identity),None)


@app.route('/cart/<identity>/in_kitchen')
def confirm6(identity):
	key = "user:"+str(identity)+":cart_status"
	set_key(key,"in_kitchen")
	if str(identity) in orders_branch_O:
		orders_branch_O[str(identity)]['status'] = 'in_kitchen'
	elif str(identity) in orders_branch_Y:
		orders_branch_Y[str(identity)]['status'] = 'in_kitchen'
	elif str(identity) in orders_branch_R:
		orders_branch_R[str(identity)]['status'] = 'in_kitchen'
	elif str(identity) in orders_branch_K:
		orders_branch_K[str(identity)]['status'] = 'in_kitchen'
	orders[str(identity)]['status'] = 'in_kitchen'


@app.route('/cart/<identity>/out_for_delivery/<contact>')
def confirm7(identity, contact):
	key = "user:"+str(identity)+":cart_status"
	set_key(key,"out_for_delivery")
	key = "user:"+str(identity)+":dboy"
	set_key(key,str(contact))
	key = "delivery_boy:" + str(contact) + ":deliveries"
	set_add(key,str(identity))
	if str(identity) in orders_branch_O:
		orders_branch_O[str(identity)]['status'] = 'out_for_delivery'
	elif str(identity) in orders_branch_Y:
		orders_branch_Y[str(identity)]['status'] = 'out_for_delivery'
	elif str(identity) in orders_branch_R:
		orders_branch_R[str(identity)]['status'] = 'out_for_delivery'
	elif str(identity) in orders_branch_K:
		orders_branch_K[str(identity)]['status'] = 'out_for_delivery'
	orders[str(identity)]['status'] = 'out_for_delivery'



@app.route('/get_data_for_delivery/<contact>')
def get_data(contact):
	key = "delivery_boy:" + str(contact) + ":deliveries"
	ids = set_members(key)
	ids = ids.split()
	result = {}
	for identity in ids:
		details = {}
		key = "user:" + str(identity) + ":details"
		name = get_hash_field(key,"name").replace("_"," ")
		key = "user:" + str(identity) + ":last_cart"
		last_cart = get_key(key)
		details["cart"] = get_hash(last_cart)
		cart = {}
		for key in details["cart"].keys():
			cart[key.replace("_"," ")] = details["cart"][key]
		details["cart"] = cart
		key = "user:" + str(identity) + ":cur_address"
		details["address"] = get_key(key)
		result[name] = details
	yield json.dumps(result)

@app.route('/cart/<identity>/delivered')
def confirm8(identity):
	key = "user:"+str(identity)+":cart_status"
	set_key(key,"delivered")
	key = "user:"+str(identity)+":assigned_rest"
	closest = get_key(key)
	key = "user:"+str(identity)+":cart:price"
	total = get_key(key)
	key_increment_by(daily_confirmed_carts,1)
	key_increment_by(daily_converted_value,total)
	if closest in "Residency_Road":
		key_increment_by(r_converted_carts,1)
		key_increment_by(r_converted_value,total)
	elif closest in "Yelahanka":
		key_increment_by(y_converted_carts,1)
		key_increment_by(y_converted_value,total)
	elif closest in "Old_Airport_Road":
		key_increment_by(o_converted_carts,1)
		key_increment_by(o_converted_value,total)
	elif closest in "Koramangala":
		key_increment_by(k_converted_carts,1)
		key_increment_by(k_converted_value,total)
	orders.pop(str(identity),None)
	orders_branch_O.pop(str(identity),None)
	orders_branch_Y.pop(str(identity),None)
	orders_branch_R.pop(str(identity),None)
	orders_branch_K.pop(str(identity),None)
	if str(identity) in orders_branch_O:
		orders_branch_O[str(identity)]['status'] = 'delivered'
	elif str(identity) in orders_branch_Y:
		orders_branch_Y[str(identity)]['status'] = 'delivered'
	elif str(identity) in orders_branch_R:
		orders_branch_R[str(identity)]['status'] = 'delivered'
	elif str(identity) in orders_branch_K:
		orders_branch_K[str(identity)]['status'] = 'delivered'
	if str(identity) in orders:
		orders[str(identity)]['status'] = 'delivered'


@app.route('/geniidata')
def geniidata():
	result = {}
	result["total_converted_value"] = get_key(total_converted_value)
	result["total_converted_carts"] = get_key(total_converted_carts)
	result["y_converted_value"] = get_key(y_converted_value)
	result["y_converted_carts"] = get_key(y_converted_carts)
	result["r_converted_value"] = get_key(r_converted_value)
	result["r_converted_carts"] = get_key(r_converted_carts)
	result["o_converted_value"] = get_key(o_converted_value)
	result["o_converted_carts"] = get_key(o_converted_carts)
	result["k_converted_value"] = get_key(k_converted_value)
	result["k_converted_carts"] = get_key(k_converted_carts)
	return result


@app.route('/cart/<identity>/status')
def confirm3(identity):
	key = "user:"+str(identity)+":cart_status"
	result = {}
	if(key_exists(key)):
		result['status'] = get_key(key)
		if(get_key(key)=='out_for_delivery' or get_key(key)=='delivered'):
			key = "user:"+str(identity)+":dboy"
			result['dboy'] = get_key(key)
		yield json.dumps(result)
	else:
		yield "Status not set"

@app.route('/show_old_carts/<identity>')
def old_carts(identity):
	s = set_members("user:" + identity + ":confirmed_carts")
	'''print "Surya"
	s = s.split()
	print s
	result = {}
	for i in s:
		result[i] = get_hash(i)
	yield result'''
	s = s.split()
	result = {}
	command = "redis-cli HGETALL "
	for i in s:
		result[i] = commands.getoutput(command+i)
	yield json.dumps(result)

@app.route('/<identity>/last_cart')
def last_cart(identity):
	key = "user:"+str(identity)+":last_cart"
	last_cart = get_key(key)
	yield json.dumps(get_hash(last_cart))

@app.route('/<identity>/item_history')
def last_cart(identity):
	key = "user:"+str(identity)+":ordered_items"
	yield json.dumps(ss_range(key,"0","-1"))

@app.route('/get_menu')
def get_menu():
	global dishes_db
	return dishes_db.to_json(orient="records")

@app.route('/hotel_status/<hotel>')
def gethotelstatus(hotel):
        global shutdown
        if hotel in shutdown:
                return json.dumps("1")
        else:
                return json.dumps("0")

@app.route('/get_user_menu/<identity>')
def get_user_menu(identity):
	global dishes_db, Hotel_locations
	locflag = get_key("user:" + str(identity) + ":cart:" + str(int(set_count("user:"+str(identity)+":confirmed_carts"))+1) + ":flag")
	if(locflag=='0'):
		hotel = get_key("user:" + str(identity) + ":assigned_rest")
		dish_db = dishes_db.copy(deep = True)
		for hot in Hotel_locations:
			if(hot!=hotel):
				dish_db.drop([hot], axis = 1 , inplace = True)
		dish_db['stock'] = dish_db[hotel]
		dish_db.drop([hotel],axis= 1,inplace = True)
		print dish_db
		print dishes_db
		return dish_db.to_json(orient = "records")
	else:
		return dishes_db.to_json(orient="records")

@app.route('/loading_df/<filename>')
def load_df(filename):
	df = pd.DataFrame()
	i1 = open(filename,'r').read()
	df = pd.read_json(json.loads(i1),orient='index')
	print df
	#yield df

def display():
	global dishes_db
	print dishes_db


@app.route('/add_dish/<d>')
def add_dish(d):
	u = 'http://0.0.0.0:7000/addingdish/'
	h ={ 'content-type': 'application/json; charset=utf-8'}
	r = requests.get(url=u+d,headers=h)
	global dishes_db
	df = pd.read_json(d, orient = 'records')
	for row in df.itertuples():
		row.link.replace("_","/")
	print(df)
	dishes_db = dishes_db.append(df,ignore_index=True)
	#print(dishes_db)
	xyz = dishes_db.to_json(orient='index')
	with open('dishes15.txt','w') as outfile:
		json.dump(xyz, outfile)
	d = json.loads(d)
	url = "https://api.api.ai/v1/entities/2d04d8e5-02c5-4eb5-afaf-037bfb662513/entries?v=20150910"
	Headers={"Authorization": 'Bearer 9afd07100b9a4f27ae0f03eda9e3c752',"Content-Type": 'application/json; charset=utf-8'}
	body=[{"value":d[0]['name'],'synonyms':[d[0]['name']]}]
	r = requests.post(url,headers=Headers,json=body)
	display()
	#print(dishes_db)

@app.route('/delete_dish/<name>')
def delete_dish(name):
	global dishes_db
	u = 'http://0.0.0.0:7000/deletingdish/'
	h ={ 'content-type': 'application/json; charset=utf-8'}
	r = requests.get(url=u+name,headers=h)
	name = json.loads(name)
	for nam in name:
		dishes_db = dishes_db[dishes_db.name != str(nam)]
	xyz = dishes_db.to_json(orient='index')
	with open('dishes15.txt','w') as outfile:
		json.dump(xyz, outfile)
	url = "https://api.api.ai/v1/entities/2d04d8e5-02c5-4eb5-afaf-037bfb662513/entries?v=20150910"
	Headers={"Authorization": 'Bearer 9afd07100b9a4f27ae0f03eda9e3c752',"Content-Type": 'application/json; charset=utf-8'}
	body=[{"value":name}]
	r = requests.delete(url,headers=Headers,json=name)


@app.route('/set_menu')
def store_the_dishes():
	temp =  {"Courses":{"Breakfast":{"P For Pakora Platter":
["100","Veg","aloo"],"Fluffy Poori Allo":
["115","Veg","aloo"],"Anda Aur Aloo Combo":
["120","Veg","U"],"Power-up Combo":
["120","Veg","U"],"Chole Wale Bhature":
["120","Veg","chole"]},"New Launch":{"Punjabi Aloo Parantha Combo":
["155","Veg","aloo"],"Punjabi Paneer Parantha Combo":
["155","Veg","paneer"],"Aloo Matar":
["155","Veg","aloo"],"Baigan Bhartha":
["145","Veg","U"],"Punjabi Aloo Ka Parantha":
["60","Veg","aloo"],"Punjabi Paneer Ka Parantha":
["155","Veg","paneer"]},"Power Up Main Course":{"Pindi Chole":
["115","Veg","pindi"],"Murgh Kali Mirch":
["240","Non Veg","chicken"],"Paneer Makhanwala":
["240","Veg","paneer"],"Paneer Lababdar":
["240","Veg","paneer"],"Saagwala Paneer":
["240","Veg","paneer"],"Subzi Meloni":
["200","Veg","subzi"],"Dal Makhani":
["160","Veg","dal"],"Dal Saath Salam":
["115","Veg","dal"],"Chicken Lababdar":
["280","Non Veg","chicken"],"Chicken Makhanwala":
["260","Non Veg","chicken"],"Mutton Rogan Josh":
["290","Non Veg","mutton"]},"Tank Up On Rice":{"Steamed Rice":
["85","Veg","rice"],"Jeera Rice":
["115","Veg","rice"],"Chicken Biryani":
["250","Non Veg","rice"],"Mutton Biryani":
["290","Non Veg","rice"]},"Piping Breads":{"Tandoori Roti":
["22", "Veg","U"],"Naan":
["25", "Veg","U"],"Onion Kulcha":
["35","Veg","U"],"Wheat Tawa Roti":
["17","Veg","U"]},"Riveting Desserts":{"Phirni":
["90","Veg","U"],"Kheer":
["90","Veg","U"],"B&W Chocolate Cake Eggless":
["140","Veg","U"]},"Super Coolants":{"Shikanji":
["30", "Veg","U"],"Masala Chaas":
["40", "Veg","U"],"Lassi Sweet":
["75","Veg","U"],"Lassi Salt":
["75", "Veg","U"]},"Beverages":{"Water Bottle 500ml":
["20","Veg","U"],"Water Bottle 1l":
["40", "Veg","U"],"Soft Drink 250ml":
["30", "Veg","U"], "Soft Drink 500ml":
["44", "Veg","U"], "Diet Coke 330ml":
["45", "Veg","U"]},"Top Gear Combos":{"Dilli Combo veg":
["280","Veg","U"],"Amritsari Combo veg":
["280","Veg","U"],"Lucknowi Combo veg":
["280","Veg","U"],"Dilli Combo nonveg":
["295","Non Veg","chicken"],"Amritsari Combo nonveg":
["295","Non Veg","chicken"],"Kashmiri Combo nonveg":
["360","Non Veg","chicken"],"Healthy Jalandhar Combo":
["260","Veg","U"]},"Speedy Combos":{"Dilli Combo veg":
["160","Veg","U"],"Lucknowi Combo veg":
["160","Veg","U"],"Amritsari Combo veg":
["160","Veg","U"],"Dal Makhni Combo":
["99","Veg","dal"],"Dilli Combo nonveg":
["160","Non Veg","chicken"],"Amritsari Combo nonveg":
["160","Non Veg","chicken"],"Kashmiri Combo nonveg":
["220","Non Veg","chicken"],"Pindi Chole Combo":
["120","Veg","pindi"]},"Convertible Combos":{"Lucknowi Convertible Combo veg":
["135","Veg","U"],"Amritsari Convertible Combo veg":
["135","Veg","U"],"Dilli Convertible Combo veg":
["150","Veg","U"],"Amritsari Convertible Combo nonveg":
["145","Non Veg","chicken"],"Dilli Convertible Combo nonveg":
["150","Non Veg","chicken"],"Kashmiri Convertible Combo nonveg":
["170","Non Veg","mutton"]},"Full Throttle Starters":{"Chicken Tikka":
["220", "Non Veg","chicken"],"Paneer Tikka":
["210","Veg","paneer"],"Hariyali Chicken Kebab":
["220","Non Veg","chicken"],"Malai Chicken Kebab":
["240","Non Veg","chicken"],"Mutton Seekh Kebab":
["260","Non Veg","mutton"],"Assorted Veg Tikkis":
["195","Veg","U"]},"Blazing Rolls":{"Paneer Kathi Roll":
["135","Veg","paneer"],"Chicken Kathi Roll":
["160","Non Veg","chicken"],"Mutton Kathi Roll":
["200","Non Veg","mutton"],"Prawn Roll":
["200","Non Veg","prawn"]}}}
	global dishes_db , dishes_dicti
	dishes_db_new = {"name":[],"v_n":[],"base_ing":[],"course":[],"category":[],"count":[],"price":[],"stock":[],"link":[],"Old_Airport_Road":[],"Yelahanka":[],"Residency_Road":[],"Koramangala":[]}
	for course in temp["Courses"]:
		for dish in temp["Courses"][course]:
			dishes_db_new["course"].append(course)
			if(course == "New Launch"):
				dishes_db_new["category"].append("specials")
			elif(course == "Power Up Main Course"):
				dishes_db_new["category"].append("subzi")
			elif(course == "Full Throttle Starters"):
				dishes_db_new["category"].append("starters")
			elif(course == "Blazing Rolls"):
				dishes_db_new["category"].append("roll")
			elif(course == "Piping Breads"):
				dishes_db_new["category"].append("bread")
			elif(course == "Tank Up On Rice"):
				dishes_db_new["category"].append("rice")
			elif(course == "Top Gear Combos"):
				dishes_db_new["category"].append("combo")
			elif(course == "Speedy Combos"):
				dishes_db_new["category"].append("mini_combo")
			elif(course == "Convertible Combos"):
				dishes_db_new["category"].append("convertible_combo")
			elif(course == "Riveting Desserts"):
				dishes_db_new["category"].append("dessert")
			elif(course == "Super Coolants"):
				dishes_db_new["category"].append("beverage")
			elif(course == "Beverages"):
				dishes_db_new["category"].append("beverage")
			elif(course == "Breakfast"):
				dishes_db_new["category"].append("breakfast")
			else:
				dishes_db_new["category"].append("HERO")
			dishes_db_new["name"].append(dish.replace(" ","_").lower().replace("(","").replace(")",""))
			dishes_db_new["stock"].append("In")
			dishes_db_new["Old_Airport_Road"].append("In")
			dishes_db_new["Koramangala"].append("In")
			dishes_db_new["Yelahanka"].append("In")
			dishes_db_new["Residency_Road"].append("In")
			s = 'http://genii.ai/activebots/Babadadhaba/img/db/'
			if dish in ["P For Pakora Platter","Fluffy Poori Allo","Anda Aur Aloo Combo","Chole Wale Bhature","Healthy Jalandhar Combo","Prawn Roll"]:
				dishes_db_new["link"].append(s  + "bdd_logo.jpg")
			else:
				dishes_db_new["link"].append(s + dish.replace("nonveg","Non-Veg").replace("veg","Veg").replace(" ","-").replace("(","").replace(")","") + ".jpg")
			if dish in dishes_dicti:
				dishes_db_new["count"].append(dishes_dicti[dish.replace(" ","_").lower().replace("(","").replace(")","")])
			else:
				dishes_db_new["count"].append(0)
			count = 1
			for data in temp["Courses"][course][dish]:
				if (count == 1):
					dishes_db_new["price"].append(data)
				if(count == 2):
					data = data.replace(" ","").lower()
					dishes_db_new["v_n"].append(data)
				if(count == 3):
					data = data.replace(" ","_").lower()
					dishes_db_new["base_ing"].append(data)
				count = count + 1
	dishes_db = pd.DataFrame.from_dict(dishes_db_new, orient='index')
	a_db = dishes_db.transpose()
	dishes_db = a_db
	#print(type(dishes_db))
	xyz = a_db.to_json(orient='index')
	#pprint(xyz)
	with open('dishes15.txt','w') as outfile:
		json.dump(xyz, outfile)
	#print(dishes_db)

@app.route('/cart/<identity>/remove/<d>')
def change_cart(identity, d):
	d = d.lower()
	d = json.loads(d)
	key = "user:"+ identity +":cart:"+str(int(set_count("user:"+identity+":confirmed_carts"))+1)
	for item in d:
		incr_hash_field_by(key,item,d[item])
	cart = get_hash(key)
	for dish in cart:
			if(int(cart[dish]) <= 0):
				delete_hash_field(key,dish)
	cart = get_hash(key)
	if(cart == {}):
		yield "Cart empty"
	else:
		yield "Done"

@app.route('/<identity>/set_contact/<contact>')
def set_contact(identity,contact):
	key = "user:"+str(identity)+":cur_contact"
	set_key(key,str(contact))
	key = "user:"+str(identity)+":contacts"
	ss_member_increment_by(key,str(contact),"1")

def getcalls(key):
	command = "redis-cli lrange " + key + " 0 -1"
	calls = commands.getoutput(command)
	calls = calls.split('\n')
	print calls
	expire_key_in(key,1)
	return calls

@app.route('/use_saved/<identity>')
def saved_address(identity):
	set_key("user:" + str(identity) + ":cart:" + str(int(set_count("user:"+str(identity)+":confirmed_carts"))+1) + ":flag","0")
	expire_key_in("user:" + str(identity) + ":cart:" + str(int(set_count("user:"+str(identity)+":confirmed_carts"))+1) + ":flag",3600)
	return {"calls":get_key("user:"+str(identity)+":calls"),"tags":get_key("user:"+str(identity)+":call-tags")}

@app.route('/<identity>/set_address/<address>')
def set_address(identity,address):
	key = "user:"+str(identity)+":cur_address"
	s = address.split(",")
	q = get_nearest_hotel(s[0],s[1])
	print q
	set_key(key,str(address).replace(" ","_"))
	key = "user:"+str(identity)+":addresses"
	ss_member_increment_by(key,str(address).replace(" ","_"),"1")
	set_key("user:" + str(identity) + ":cart:" + str(int(set_count("user:"+str(identity)+":confirmed_carts"))+1) + ":flag","0")
	expire_key_in("user:" + str(identity) + ":cart:" + str(int(set_count("user:"+str(identity)+":confirmed_carts"))+1) + ":flag",3600)
	if(q!=None):
		key = "user:"+str(identity)+":assigned_rest"
		if q not in shutdown:
			set_key(key,q)
			det = {"area":q,"calls":get_key("user:"+str(identity)+":calls"),"tags":get_key("user:"+str(identity)+":call-tags")}
			return det
		else:
			set_key(key,"None")
			return {"status":"shut_down"}
	else:
		set_key(key,"None")
		return {"status":"out_of_range"}

@app.route('/<identity>/set_note/<note>')
def set_contact(identity,note):
	key = "user:"+str(identity)+":cur_note"
	set_key(key,str(note).replace(" ","_"))
	key = "user:"+str(identity)+":notes"
	ss_member_increment_by(key,str(note).replace(" ","_"),"1")

@app.route('/<identity>/get_contact')
def get_contact(identity):
	key = "user:"+str(identity)+":cur_contact"
	yield get_key(key)

@app.route('/<identity>/get_contacts')
def get_contacts(identity):
	key = "user:"+str(identity)+":contacts"
	yield json.dumps(ss_range(key,"0","-1"))

@app.route('/<identity>/get_address')
def get_address(identity):
	key = "user:"+str(identity)+":cur_address"
	yield get_key(key)

@app.route('/<identity>/get_addresses')
def get_addresses(identity):
	key = "user:"+str(identity)+":addresses"
	yield json.dumps(ss_range(key,"0","-1"))

@app.route('/<identity>/get_note')
def get_note(identity):
	key = "user:"+str(identity)+":cur_note"
	yield get_key(key)

@app.route('/<identity>/get_notes')
def get_contacts(identity):
	key = "user:"+str(identity)+":notes"
	yield json.dumps(ss_range(key,"0","-1"))

@app.route('/<pass_key>/get_payment_status_2')
def get_payment_status(pass_key):
	result = payment(str(pass_key))
	yield result["status"]


def get_cart_price1(id):
	global dishes_db
	key = "user:"+ str(id)+":cart:"+str(int(set_count("user:"+str(id)+":confirmed_carts")))
	print(key)
	cart = get_hash(key)
	prices = {}
	prices["cart_id"] = key
	total = 0
	for item in cart:
		if(int(cart[item])>0):
			val =  dishes_db[dishes_db["name"] == item]["price"].tolist()[0]
			prices[item] = (int(val) ,int(cart[item]))
			a,b = prices[item]
			total += a*b
	prices["total"] = total
	key = "user:"+str(id)+":cart:price"
	set_key(key,str(total))
	key = "rest_discount"
	prices["discount"]=prices["total"]*int(get_key(key))/100
	return prices

@app.route('/get_new_receipt/<dic>')
def get_new_reciept(dic):
	data = json.loads(dic)
	identity = data["Id"]
	confirm10(identity)
	lat_long = get_key("user:"+str(identity)+":cur_address")
	lat_long = lat_long.split(",")
	key = "user:" + str(identity) + ":details"
	data.pop("Id",None)
	data["address"] = data["address"].replace(" ","_")
	data['name'] = data["name"].replace(" ","_")
	set_hash(key,data)
	#data['address'] = get_hash_field(key,"address").replace("_"," ")
	#data['number'] = str(get_hash_field(key,"number")) #get_geocode(lat_long[0],lat_long[1])
	total = get_cart_price1(identity)
	data['cart'] = total
	data["address"] = data["address"].replace("_"," ")
	data['name'] = data["name"].replace("_"," ")
	#data['discount']
	key = "user:"+str(identity)+":cart_status"
	data['order_status'] = get_key(key)
	yield json.dumps(data)

@app.route('/get_receipt/<identity>')
def get_reciept(identity):
	data = {}
	confirm10(identity)
	lat_long = get_key("user:"+str(identity)+":cur_address")
	lat_long = lat_long.split(",")
	key = "user:" + str(identity) + ":details"
	data['address'] = get_hash_field(key,"address").replace("_"," ")
	data['number'] = str(get_hash_field(key,"number")) #get_geocode(lat_long[0],lat_long[1])
	total = get_cart_price1(identity)
	data['cart'] = total
	data['name'] = get_hash_field(key,"name").replace("_"," ")
	key = "user:"+str(identity)+":cart_status"
	data['order_status'] = get_key(key)
	yield json.dumps(data)

@app.route('/read_orders')
def read_orders():
	global orders
	yield json.dumps(orders)

@app.route('/read_orders_R')
def read_orders_R():
	global orders_branch_R
	yield json.dumps(orders_branch_R)

@app.route('/read_orders_O')
def read_orders_O():
	global orders_branch_O
	yield json.dumps(orders_branch_O)

@app.route('/read_orders_K')
def read_orders_K():
	global orders_branch_K
	yield json.dumps(orders_branch_K)

@app.route('/read_orders_Y')
def read_orders_Y():
	global orders_branch_Y
	yield json.dumps(orders_branch_Y)

@app.route('/<identity>/get_notes')
def get_contacts(identity):
	key = "user:"+str(identity)+":notes"
	yield json.dumps(ss_range(key,"0","-1"))


@app.route('/get_location_total/<identity>')
def location(identity):
	key = "user:" + str(identity) + ":cur_address"
	data = {}
	if(key_exists(key)):
		lat,longi = get_key(key).split(',')
		data["address"] = get_geocode(lat,longi)
	else:
		data["address"] = ''
	data["total"] = get_cart_price(identity)["total"]
	yield json.dumps(data)

def get_geocode_address(address):
	gmaps = googlemaps.Client(key='AIzaSyCGIi0Ts6EavD1FN4Ckx0uR7Ikr1Z1Jwgw')
	geocode_result = gmaps.geocode(address)
	return geocode_result

@app.route('/set_user_default/<identity>/<d>')
def set_user_def(identity,d):
	d = json.loads(d)
	print d
	key = "user:" + str(identity) + ":details"
	set_hash_field(key,"number",str(d["number"]))
	set_hash_field(key,"address",d["address"].replace(" ","_"))
	set_hash_field(key,"name",d["name"])

@app.route('/get_user_default/<identity>')
def get_user_def(identity):
	key = "user:" + str(identity) + ":details"
	key2 = "user:" + str(identity) + ":cur_address"
	result = get_hash(key)
	result["name"] = result["name"].replace("_"," ")
	if(hash_field_exists(key,"number")):
		result["number"] = result["number"].replace("_"," ")
	if(key_exists(key2)):
		latlong = get_key(key2)
		latlong = latlong.split(",")
		result["address"] = get_geocode(latlong[0],latlong[1])
	elif(hash_field_exists(key,"address")):
		result["address"] = result["address"].replace("_"," ")
	yield json.dumps(result)

def get_reciept1(identity):
	data = {}
	confirm10(identity)
	lat_long = get_key("user:"+str(identity)+":cur_address")
	lat_long = lat_long.split(",")
	key = "user:" + str(identity) + ":details"
	data['address'] = get_hash_field(key,"address").replace("_"," ")
	data['number'] = str(get_hash_field(key,"number")) #get_geocode(lat_long[0],lat_long[1])
	total = get_cart_price1(identity)
	data['cart'] = total
	data['name'] = get_hash_field(key,"name").replace("_"," ")
	key = "user:"+str(identity)+":cart_status"
	data['order_status'] = get_key(key)
	return data

@app.route('/bypass_payments/<identity>')
def bypass(identity):
	if (key_exists("user:"+str(identity)+":details")):
		#confirm10(identity)
		yield json.dumps(get_reciept1(identity))
	else:
		yield "No data"

@app.route('/set_confirmation/<identity>/<d>')
def set_confirm(identity,d):
	d = json.loads(d)
	key = "user:" + str(identity) + ":details"
	confirm10(identity)
	set_hash_field(key,"number",str(d["number"]))
	set_hash_field(key,"address",d["address"].replace(" ","_"))
	set_hash_field(key,"name",d["name"].replace(" ","_"))

@app.route('/refresh_stock')
def refresh_stock():
	global dishes_db
	dishes_db = dishes_db.replace("Out","In")
	u = 'http://0.0.0.0:7000/refreshing'
	h ={ 'content-type': 'application/json; charset=utf-8'}
	r = requests.get(url=u,headers=h)
	print dishes_db

@app.route('/outofstock/<dname>')
def outstock(dname):
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['stock'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'stock'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['stock'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'stock'] = 'In'
	u = 'http://0.0.0.0:7000/outofstock/'
	h ={ 'content-type': 'application/json; charset=utf-8'}
	r = requests.get(url=u+dname,headers=h)
	#print dishes_db
	return "Success"

@app.route('/outofstock_K/<dname>')
def outstock_K(dname):
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['Koramangala'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'Koramangala'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['Koramangala'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'Koramangala'] = 'In'
	u = 'http://0.0.0.0:7000/outofstock_K/'
	h ={ 'content-type': 'application/json; charset=utf-8'}
	r = requests.get(url=u+dname,headers=h)
	#print dishes_db
	return "Success"

@app.route('/outofstock_Y/<dname>')
def outstock_Y(dname):
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['Yelahanka'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'Yelahanka'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['Yelahanka'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'Yelahanka'] = 'In'
	u = 'http://0.0.0.0:7000/outofstock_Y/'
	h ={ 'content-type': 'application/json; charset=utf-8'}
	r = requests.get(url=u+dname,headers=h)
	#print dishes_db
	return "Success"

@app.route('/outofstock_O/<dname>')
def outstock_O(dname):
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['Old_Airport_Road'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'Old_Airport_Road'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['Old_Airport_Road'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'Old_Airport_Road'] = 'In'
	u = 'http://0.0.0.0:7000/outofstock_O/'
	h ={ 'content-type': 'application/json; charset=utf-8'}
	r = requests.get(url=u+dname,headers=h)
	#print dishes_db
	return "Success"

@app.route('/outofstock_R/<dname>')
def outstock_R(dname):
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['Residency_Road'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'Residency_Road'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['Residency_Road'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'Residency_Road'] = 'In'
	u = 'http://0.0.0.0:7000/outofstock_R/'
	h ={ 'content-type': 'application/json; charset=utf-8'}
	r = requests.get(url=u+dname,headers=h)
	#print dishes_db
	return "Success"

i1 = open('dishes15.txt','r').read()
df = pd.read_json(json.loads(i1),orient='index')
global dishes_db
dishes_db = df
#store_the_dishes()
app.install(EnableCors())
app.run(host='0.0.0.0', port=5000, debug=True,server='gevent')
