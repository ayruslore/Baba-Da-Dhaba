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

@app.route('/recommend/<v_n>/<base_ing>/<category>/<identity>')
def reco_filter1(v_n,base_ing,category,identity):
	global dishes_db,link
	carthotel = get_key("user:" + str(identity) + ":assigned_rest")
	locflag = locflaging(identity)
	if carthotel in shutdown:
		return json.dumps({"status":"shutdown","locflag":locflag})
	if locflag == 0:
		result = dishes_db[dishes_db[carthotel]=='In']
		if v_n in ["veg","nonveg"]:
			result = result[result["v_n"]==v_n]
		if base_ing in ["chicken","mutton","dal","rice","chole","chocolate","paneer","prawn"]:
			result = result[result["base_ing"]==base_ing]
		if category in ["roll","rice","combo","mini_combo","subzi","bread","starter","dessert"]:
			result = result[result["category"]==category]
		result = {"status":"open","reco": result['name'].tolist()[:5],"links":result['link'].tolist()[:5],"prices":result['price'].tolist()[:5],"locflag":0}
		return json.dumps(result)
	else:
		set_key("user:"+str(identity)+":calls",link + "/recommend/" + v_n + "/" + base_ing + "/" + category + "/" + str(identity))
		set_key("user:"+str(identity)+":call-tags","recommend_specific")
		result = {"status":"open","tag":"recommend_specific","locflag":locflag,"call":link + "/recommend/" + v_n + "/" + base_ing + "/" + category + "/" + str(identity)}
		return json.dumps(result)

def reco_filter(v_n,base_ing,category,hotel):
	global dishes_db
	result = dishes_db[dishes_db[hotel]=='In']
	if v_n in ["veg","nonveg"]:
		result = result[result["v_n"]==v_n]
	if base_ing in ["chicken","mutton","dal","rice","chole","chocolate","paneer","prawn"]:
		result = result[result["base_ing"]==base_ing]
	if category in ["roll","rice","combo","mini_combo","subzi","bread","starter","dessert"]:
		result = result[result["category"]==category]
	result = {"reco": result['name'].tolist()[:5],"links":result['link'].tolist()[:5],"prices":result['price'].tolist()[:5]}
	return result

@app.route('/specials/<identity>')
def special(identity):
	global dishes_db,link
	'''result = dishes_db
	result = {"reco": result['name'].tolist()[:5],"links":result['link'].tolist()[:5],"prices":result['price'].tolist()[:5]}
	yield json.dumps(result)
	'''
	carthotel = get_key("user:" + str(identity) + ":assigned_rest")
	locflag = locflaging(identity)
	if carthotel in shutdown:
		return json.dumps({"status":"shut_down","locflag":locflag})
	if locflag == 0:
		result = dishes_db[dishes_db[carthotel]=='In']
		result = result[result["category"]=="specials"]
		result = {"status":"open","reco": result['name'].tolist()[:5],"links":result['link'].tolist()[:5],"prices":result['price'].tolist()[:5],"locflag":0}
		return json.dumps(result)
	else :
		set_key("user:"+str(identity)+":calls",link + "/specials/" + str(identity))
		set_key("user:"+str(identity)+":call-tags","specials")
		return json.dumps({"tag":"special","locflag":locflag,"call":link + "/specials/" + str(identity),"status":"open"})

global shutdown
shutdown = []

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

@app.route('/shutingdown/<hotel>')
def shuting(hotel):
        global shutdown
        if hotel in shutdown:
                dishes_db[hotel] = dishes_db[hotel].replace("Out","In")
                with open('dishes15.txt','w') as outfile:
                       	json.dump(dishes_db.to_json(orient='index'), outfile)
                shutdown.remove(hotel)
        else:
               	shutdown.append(hotel)
                dishes_db[hotel] = dishes_db[hotel].replace("In","Out")
                with open('dishes15.txt','w') as outfile:
                        json.dump(dishes_db.to_json(orient='index'), outfile)
                changestock('Hotel')
        return json.dumps('Success')

def locflaging(identity):
	carthotel = get_key("user:" + str(identity) + ":assigned_rest")
	locflag = get_key("user:" + str(identity) + ":cart:" + str(int(set_count("user:"+str(identity)+":confirmed_carts"))+1) + ":flag")
	if locflag == '0':
		return 0
	if locflag == '2':
		return 2
	if locflag == '1':
		return 1
	elif locflag == '':
		if carthotel != '':
			return 1
		else:
			return 2

global link
link = "https://1971f758.ngrok.io"

@app.route('/<identity>/get_history_reco')
def get_recommend_dishes2(identity):
	global dishes_db,link
	#print dishes_db
	call = link + "/" + str(identity) + "/get_history_reco"
	print call
	carthotel = get_key("user:" + str(identity) + ":assigned_rest")
	locflag = locflaging(identity)
	if carthotel in shutdown:
		return json.dumps({"status":"shut_down","locflag":locflag})
	if(key_exists("user:"+str(identity)+":ordered_items") == False):
		if locflag == 0:
			dik = reco_filter('k','k','k',carthotel)
			dik['locflag'] = 0
			dik['status'] = "open"
			return json.dumps(dik)
		else :
			set_key("user:"+str(identity)+":calls",call)
			set_key("user:"+str(identity)+":call-tags","recommend")
			return json.dumps({"tag":"recommend","locflag":locflag,"call":link + "/" + str(identity)+"/get_history_reco","status":"open"})
	else:
		recommendation = {"reco": [],"links":[],"prices":[]}
		if locflag == 0:
			recommendation['locflag'] = 0
			di = dishes_db[dishes_db[carthotel]=='In']
			dishes_list = get_history_reco3(di,identity)
			for dish in dishes_list:
				result = dishes_db[dishes_db["name"] == dish]
				recommendation["reco"].append(result["name"].tolist()[0])
				recommendation["prices"].append(result["price"].tolist()[0])
				recommendation["links"].append(result["link"].tolist()[0])
			recommendation['locflag'] = 0
			recommendation['status'] = "open"
			return json.dumps(recommendation)
		else:
			set_key("user:"+str(identity)+":calls",call)
			set_key("user:"+str(identity)+":call-tags","recommend")
			return json.dumps({"tag":"recommend","locflag":locflag,"call":link + "/" + str(identity)+"/get_history_reco","status":"open"})

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
	set_key("user:"+str(identity)+":call-tags","New_user")
	yield json.dumps({"first_name":name,"locflag":2,"tag":"New_user"})

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
		result["locflag"] = locflaging(identity)
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
	dishes_db_new = {"name":[],"v_n":[],"base_ing":[],"course":[],"category":[],"count":[],"price":[],"link":[],"stock":[],"Yelahanka":[],"Koramangala":[],"Old_Airport_Road":[],"Residency_Road":[]}
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
			dishes_db_new["Yelahanka"].append("In")
			dishes_db_new["Old_Airport_Road"].append("In")
			dishes_db_new["Koramangala"].append("In")
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

@app.route('/outofstock_K/<dname>')
def outstocking_K(dname):
	global dishes_db
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['Koramangala'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'Koramangala'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['Koramangala'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'Koramangala'] = 'In'
	print dname
	print dishes_db
	return json.dumps('Success')

@app.route('/outofstock_Y/<dname>')
def outstocking_Y(dname):
	global dishes_db
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['Yelahanka'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'Yelahanka'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['Yelahanka'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'Yelahanka'] = 'In'
	print dname
	print dishes_db
	return json.dumps('Success')

@app.route('/outofstock_O/<dname>')
def outstocking_O(dname):
	global dishes_db
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['Old_Airport_Road'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'Old_Airport_Road'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['Old_Airport_Road'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'Old_Airport_Road'] = 'In'
	print dname
	print dishes_db
	return json.dumps('Success')

@app.route('/outofstock_R/<dname>')
def outstocking_R(dname):
	global dishes_db
	dname = dname.lower().replace(" ","_")
	if(dishes_db[dishes_db['name']==dname]['Residency_Road'].tolist()[0]== 'In'):
		dishes_db.loc[dishes_db['name']==dname,'Residency_Road'] = 'Out'
	elif(dishes_db[dishes_db['name']==dname]['Residency_Road'].tolist()[0]== 'Out'):
		dishes_db.loc[dishes_db['name']==dname,'Residency_Road'] = 'In'
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
