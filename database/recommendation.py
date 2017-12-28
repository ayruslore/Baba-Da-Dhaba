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
import redis_functions as rd
from redis_functions import *

global dishes_db
i1 = open('dishes15.txt','r').read()
df = pd.read_json(json.loads(i1),orient='index')
dishes_db = df
app = bottle.app()

@app.route('/recommend')
def reco():
	global dishes_db
	result = dishes_db[dishes_db['stock']=='In']
	result = {"reco": result['name'].tolist()[:5],"links":result['link'].tolist()[:5],"prices":result['price'].tolist()[:5]}
	yield json.dumps(result)

@app.route('/recommend/<v_n>/<base_ing>/<category>')
def reco_filter1(v_n,base_ing,category):
	global dishes_db
	result = dishes_db[dishes_db['stock']=='In']
	if v_n in ["veg","nonveg"]:
		result = result[result["v_n"]==v_n]
	if base_ing in ["chicken","mutton","dal","rice","chole","chocolate","paneer"]:
		result = result[result["base_ing"]==base_ing]
	if category in ["roll","rice","combo","mini_combo","subzi","bread","starter","dessert"]:
		result = result[result["category"]==category]
	result = {"reco": result['name'].tolist()[:5],"links":result['link'].tolist()[:5],"prices":result['price'].tolist()[:5]}
	yield json.dumps(result)

def reco_filter(v_n,base_ing,category):
	global dishes_db
	result = dishes_db[dishes_db['stock']=='In']
	if v_n in ["veg","nonveg"]:
		result = result[result["v_n"]==v_n]
	if base_ing in ["chicken","mutton","dal","rice","chole","chocolate","paneer"]:
		result = result[result["base_ing"]==base_ing]
	if category in ["roll","rice","combo","mini_combo","subzi","bread","starter","dessert"]:
		result = result[result["category"]==category]
	result = {"reco": result['name'].tolist()[:5],"links":result['link'].tolist()[:5],"prices":result['price'].tolist()[:5]}
	return result

@app.route('/specials')
def special():
	global dishes_db
	'''result = dishes_db
	result = {"reco": result['name'].tolist()[:5],"links":result['link'].tolist()[:5],"prices":result['price'].tolist()[:5]}
	yield json.dumps(result)
	'''
	result = dishes_db[dishes_db['stock']=='In']
	result = result[result["category"]=="specials"]
	result = {"reco": result['name'].tolist()[:5],"links":result['link'].tolist()[:5],"prices":result['price'].tolist()[:5]}
	yield json.dumps(result)


@app.route('/<identity>/get_history_reco')
def get_recommend_dishes2(identity):
	global dishes_db
	print dishes_db
	if(key_exists("user:"+str(identity)+":ordered_items") == False):
		dik = reco_filter('k','k','k')
		print dik
		yield json.dumps(dik)
	else:
		di = dishes_db[dishes_db['stock']=='In']
		dishes_list = get_history_reco3(di,identity)
		recommendation = {"reco": [],"links":[],"prices":[]}
		for dish in dishes_list:
			result = dishes_db[dishes_db["name"] == dish]
			recommendation["reco"].append(result["name"].tolist()[0])
			recommendation["prices"].append(result["price"].tolist()[0])
			recommendation["links"].append(result["link"].tolist()[0])
		print recommendation
		yield json.dumps(recommendation)

def get_recommend_dishes(identity):
	global dishes_db
	if(key_exists("user:"+str(identity)+":ordered_items") == False):
		return json.dumps(reco_filter('k','k','k'))
	else:
		dishes_list = get_history_reco(identity)
		recommendation = {"reco": [],"links":[],"prices":[]}
		for dish in dishes_list:
			result = dishes_db[dishes_db["name"] == dish]
			recommendation["reco"].append(result["name"].tolist()[0])
			recommendation["prices"].append(result["price"].tolist()[0])
			recommendation["links"].append(result["link"].tolist()[0])
		return recommendation


def get_usual(identity):
	key = "user:"+str(identity)+":ordered_items"
	total = get_total_sorted(key)
	count = int(ss_count(key))
	count = min(5,count)
	d={}
	if (count >=1):
		'''
		top_item, top_quantity = get_top_item(key)
		d[top_item]= float(top_quantity) / total * 1.0
		i=2'''
		for i in range(1,count +1):
			item, quant = get_nth_item(key, i)
			d[item]= float(quant) / total * 1.0
	return d

@app.route('/set_new_user_details/<identity>/<name>')
def set_new_details(identity,name):
	key = "user:" + str(identity) + ":details"
	set_hash_field(key,"name",name.replace(" ","_"))
	yield json.dumps({"first_name":name})

def get_price(items):
	global dishes_db
	result = {}
	count = 1
	for dish in items:
		print dish
		print dishes_db[dishes_db["name"] == dish[0]]["price"].tolist()
		result[str(count)] = [dish[0].replace("_"," "),dishes_db[dishes_db["name"] == dish[0]]["price"].tolist()[0],dish[1],dishes_db[dishes_db["name"] == dish[0]]["link"].tolist()[0]]
		count = count + 1
	return result

@app.route('/get_user_details/<identity>')
def user_details(identity):
	key = "user:" + str(identity) + ":details"
	result ={}
	if(key_exists(key) == False):
		result["name"] = "No name"
		result["usual"] = "Nothing"
		yield json.dumps(result)
	else:
		result["name"] = get_hash_field(key,"name").replace("_"," ")
		if(key_exists("user:"+str(identity)+":ordered_items") == True):
			s1 = get_key("user:"+str(identity)+":tic")
			result["day_diff"] = "None"
			result["time_diff"] = "None"
			if s1 !=  "":
			        s1 = s1.split("X")
				print dishes_db
				d1 = float(s1[0])
		        	t1 = float(s1[1])
				s2 = get_time_stamp()
	       		 	s2 = s2.split("X")
	        		d2 = float(s2[0])
	        		t2 = float(s2[1])
				result["day_diff"] = int(d2 - d1)
				result["time_diff"] = int(t2 - t1)
			result["usual"] = get_price(sorted(get_usual(identity).items(),key = lambda x:x[1],reverse = True))
		else:
			result["usual"] = "Nothing"
		yield json.dumps(result)
#Courses Category
#Shorba   shorba
#Kebab    kebab
#Kathi Rolls  kathi_roll
#Curries curry
#Dal  dal
#Rice  rice
#Roti Parantha  parantha
#Dahi dahi
#Dessert  dessert

@app.route('/set_menu')
def store_the_dishes():
	temp =  {"Courses":{"New Launch":{"Punjabi Aloo Paratha Combo":
["140","Veg","aloo"],"Punjabi Paneer Paratha Combo":
["160","Veg","paneer"]},"Power Up Main Course":{"Aloo Mutter":
["160","Veg","aloo"],"Baigan Bhartha":
["150","Veg","baigan"],"Pindi Chole":
["120","Veg","pindi"],"Murgh Tikka":
["250","Non Veg","chicken"],"Paneer Makhanwala":
["250","Veg","paneer"],"Paneer Lababdar":
["250","Veg","paneer"],"Saagwala Paneer":
["250","Veg","paneer"],"Subzi Meloni":
["180","Veg","subzi"],"Dal Makhani":
["160","Veg","dal"],"Dal Saath Salam":
["120","Veg","dal"],"Chicken Lababdar":
["250","Non Veg","chicken"],"Chicken Makhanwala":
["250","Non Veg","chicken"],"Mutton Rogan Josh":
["300","Non Veg","mutton"]},"Tank Up On Rice":{"Plain Rice":
["90","Veg","rice"],"Jeera Rice":
["120","Veg","rice"],"Chicken Biryani":
["220","Non Veg","rice"],"Mutton Biryani":
["290","Non Veg","rice"]},"Piping Breads":{"Tawa Roti":
["17", "Veg","U"],"Punjabi Paneer Ka Paratha":
["80","Veg","paneer"],"Punjabi Aloo Ka Paratha":
["60","Veg","aloo"],"Tandoori Roti":
["22", "Veg","U"],"Naan":
["25", "Veg","U"],"Onion Kulcha":
["35","Veg","U"],"Wheat Tawa Roti":
["15","Veg","U"]},"Riveting Desserts":{"Phirni":
["90","Veg","U"],"Kheer":
["90","Veg","U"]},"Super Coolants":{"Shikanji":
["30", "Veg","U"],"Chaas":
["40", "Veg","U"],"Lassi Sweet":
["75","Veg","U"],"Lassi Salted":
["75", "Veg","U"],"Water Bottle 500ml":
["20","Veg","U"],"Water Bottle 1l":
["40", "Veg","U"],"Soft Drink 250ml":
["30", "Veg","U"], "Soft Drink 500ml":
["44", "Veg","U"], "Diet Coke":
["45", "Veg","U"]},"Top Gear Combos":{"Dilli Combo veg":
["280","Veg","U"],"Amritsari Combo veg":
["280","Veg","U"],"Lucknowi Combo veg":
["280","Veg","U"],"Dilli Combo nonveg":
["280","Non Veg","chicken"],"Amritsari Combo nonveg":
["280","Non Veg","chicken"],"Kashmiri Combo nonveg":
["370","Non Veg","chicken"]},"Speedy Combos":{"Dilli Mini Combo veg":
["160","Veg","U"],"Lucknowi Mini Combo veg":
["160","Veg","U"],"Amritsari Mini Combo veg":
["160","Veg","U"],"Dal Makhani Mini Combo":
["99","Veg","dal"],"Dilli Mini Combo nonveg":
["160","Non Veg","chicken"],"Amritsari Mini Combo nonveg":
["160","Non Veg","chicken"],"Kashmiri Mini Combo nonveg":
["220","Non Veg","chicken"],"Pindi Chole Combo":
["120","Veg","pindi"]},"Full Throttle Starters":{"Chicken Tikka":
["220", "Non Veg","chicken"],"Paneer Tikka":
["220","Veg","paneer"],"Hariyali Chicken Kebab":
["220","Non Veg","chicken"],"Malai Chicken Kebab":
["220","Non Veg","chicken"],"Mutton Seekh Kebab":
["260","Non Veg","mutton"]},"Blazing Rolls":{"Paneer Tikka Roll":
["140","Veg","paneer"],"Chicken Tikka Roll":
["160","Non Veg","chicken"],"Mutton Seekh Roll":
["200","Non Veg","mutton"]}}}
	global dishes_db , dishes_dicti
	dishes_db_new = {"name":[],"v_n":[],"base_ing":[],"course":[],"category":[],"count":[],"price":[],"link":[],"stock":[]}
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
			elif(course == "Riveting Desserts"):
				dishes_db_new["category"].append("dessert")
			elif(course == "Super Coolants"):
				dishes_db_new["category"].append("beverage")
			else:
				dishes_db_new["category"].append("HERO")

			dishes_db_new["name"].append(dish.replace(" ","_").lower().replace("(","").replace(")",""))

			s = 'http://ec2-35-154-42-243.ap-south-1.compute.amazonaws.com/img/db/'
			dishes_db_new["link"].append(s + dish.replace(" ","-").replace("(","").replace(")","") + ".jpg")
			dishes_db_new["stock"].append("In")
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
	xyz = a_db.to_json(orient='index')
	with open('dishes15.txt','w') as outfile:
		json.dump(xyz, outfile)

@app.route('/get_logged_msg')
def get_messages():
	fil = open('msg_nt_ndrstd.txt','r')
	fil = fil.readlines()
	return json.dumps(fil)

@app.route('/log_message/<message>')
def logger(message):
	fil = open("msg_nt_ndrstd.txt",'a')
	fil.write(message + "\n")
	return "Success"

@app.route('/addingdish/<d>')
def add_dish(d):
	global dishes_db
	df = pd.read_json(d, orient = 'records')
	for row in df.itertuples():
		row.link.replace("_","/")
	dishes_db = dishes_db.append(df,ignore_index=True)
	return json.dumps('Success')

@app.route('/deletingdish/<name>')
def delete_dish(name):
	global dishes_db
	name = json.loads(name)
	for nam in name:
		dishes_db = dishes_db[dishes_db.name != str(nam)]
	return json.dumps('Success')

@app.route('/outofstock/<dname>')
def outstocking(dname):
	global dishes_db
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['stock'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'stock'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['stock'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'stock'] = 'In'
	print dname
	print dishes_db
	return json.dumps('Success')

@app.route('/refreshing')
def refresh_stock():
	global dishes_db
	dishes_db = dishes_db.replace("Out","In")
	print dishes_db
	return json.dumps('Success')


#store_the_dishes()

app.install(EnableCors())

app.run(host='0.0.0.0', port=7000, debug=True, server='gevent')
