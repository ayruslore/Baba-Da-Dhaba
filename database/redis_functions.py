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

class EnableCors(object):
    name = 'enable_cors'
    api = 2
    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors



#-----------------------------------------
command = "redis-cli "

def set_coin(identity,coin):
    set_hash_field("user:"+str(identity)+":coins","coins",str(coin))

def settle_coins(identity,payamount):
    cart = int(set_count("user:"+str(identity)+":confirmed_carts"))
    print cart
    print payamount
    coin = get_coins(identity)
    if(coin == {}):
        coin = 0
    else:
        coin = int(coin["coins"])
        print coin
    if(cart > 0 and cart <=3):
        if(cart == 1):
            money = int(payamount*0.15) + 100
            set_hash("user:"+str(identity)+":coins",{"type":"bronze","coins":str(money)})
            return {"earned":int(payamount*0.15),"remain_coins":money,"type":"bronze"}
        else:
            money = int(payamount*0.15) + coin
            set_hash("user:"+str(identity)+":coins",{"type":"bronze","coins":str(money)})
            return {"earned":int(payamount*0.15),"remain_coins":money,"type":"bronze"}
    elif(cart > 3 and cart < 11):
        money = int(payamount*0.2) + coin
        set_hash("user:"+str(identity)+":coins",{"type":"silver","coins":str(money)})
        return {"earned":int(payamount*0.2),"remain_coins":money,"type":"silver"}
    else:
        money = int(payamount*0.25) + coin
        set_hash("user:"+str(identity)+":coins",{"type":"gold","coins":str(money)})
        return {"earned":int(payamount*0.25),"remain_coins":money,"type":"gold"}

def get_coins(identity):
    return get_hash("user:"+str(identity)+":coins")

def get_time_stamp():
	s = str(datetime.now())
	s = s.split(' ')
	date = s[0].split('-')
	days = float(date[0]) * 365 + float(date[1]) * 30 + float(date[2])
	time = s[1].split(':')
	mins = float(time[0]) * 60 + float(time[1])
	return str(days)+ "X" + str(mins)

def get_geocode(lat,longi):
	gmaps = googlemaps.Client(key='AIzaSyCGIi0Ts6EavD1FN4Ckx0uR7Ikr1Z1Jwgw')
	reverse_geocode_result = gmaps.reverse_geocode((lat,longi))
	return reverse_geocode_result[0]['formatted_address']

def payment(paymentkey):
	client = razorpay.Client(auth=("rzp_test_HMAxicoOIZn8Xx", "SbdWXpN4zDLnn82U4xic5RrN"))
	client.set_app_details({"title" : "Being a cunt", "version" : "1.8.17"})
	#print client.payment.all()
	return client.payment.fetch(paymentkey)

def rpushl(key,value):
    command = "redis-cli rpush " + key + " " + value
    commands.getoutput(command)

def getlist(key):
    command = "redis-cli lrange " + key + " 0 -1"
    l = commands.getoutput(command)
    l = l.split('\n')
    return l

def remlist(key,value):
    command = "redis-cli llen " + key
    le = commands.getouput(command)
    command = "redis-cli lrem " + key + " " + str(le) + " " + value
    commands.getoutput(command)

def set_hash(key,d):
	command = "redis-cli  "
	command = command + "HMSET " + key + " "
	for i in d:
		command = command + i + " " + str(d[i]) + " "
	commands.getoutput(command)

def get_hash(key):
	command = "redis-cli  "
	command = command + "HGETALL " + key
	d = commands.getoutput(command)
	result = {}
	if(d!=''):
		d = d.split('\n')
		keys = d[::2]
		result = {}
		for i in keys:
			result[i] = d[ ( d.index(i) + 1 ) ]
		return result
	else:
		return result

def get_hash_field(key,field):
	command = "redis-cli  "
	command = command + "HGET " + key + " " + field
	return commands.getoutput(command)

def set_hash_field(key,field,value):
	command = "redis-cli  "
	command = command + "HSET " + key + " " + field + " " + value
	return commands.getoutput(command)

def delete_hash_field(key,field):
        command = "redis-cli  "
        command = command + "HDEL " + key + " " + field
        commands.getoutput(command)

def incr_hash_field_by(key,field,value):
	command = "redis-cli  "
	command = command + "HSETNX " + key + " " + field + " 0"
	commands.getoutput(command)
	command = "redis-cli  "
	command = command + "HINCRBY " + key + " " + field + " " + str(value)
	if(commands.getoutput(command)<1):
		delete_hash_field(key,field)
	#return command

def hash_field_exists(key,field):
	command = "redis-cli  "
	command = command + "HEXISTS " + key + " " + field
	if commands.getoutput(command) == '1' :
		return True
	else:
		return False

def get_hash_keys(key):
	command = "redis-cli  "
	command = command + "HKEYS " + key + " "
	result = commands.getoutput(command)
	result = result.split('\n')
	return result

def set_add(key,member):
	command = "redis-cli  SADD " + key + " " + member
	commands.getoutput(command)

def set_members(key):
	command = "redis-cli  SMEMBERS " + key
	return commands.getoutput(command)

def set_count(key):
	command = "redis-cli  SCARD " + key
	return commands.getoutput(command)

def ss_count(key):
	command = "redis-cli  ZCARD "
	command += key
	return commands.getoutput(command)

def ss_member_rank(key, member):
	command = "redis-cli  ZRANK "
	command += key + " " + member
	return commands.getoutput(command)

def ss_member_remove(key, member):
	command = "redis-cli  ZREM "
	command += key + " " + member
	commands.getoutput(command)

def ss_member_score(key, member):
	command = "redis-cli  ZSCORE "
	command += key + " " + member
	return commands.getoutput(command)

def ss_range(key,start,end):
	command = "redis-cli  ZRANGE "
	command += key + " " + str(start) + " " + str(end) + " WITHSCORES"
	result = commands.getoutput(command)
	result = result.split('\n')
	items = result[::2]
	scores = result[1::2]
	result = {}
	for i in range(len(items)):
		result[items[i]] = scores[i]
	return result

def ss_member_add(key, member, score):
	command = "redis-cli  ZADD "
	command += key + " " + str(score) + " " + member
	commands.getoutput(command)

def ss_member_increment_by(key, member, increment):
	command = "redis-cli  ZINCRBY "
	command += key + " " + str(increment) + " " + member
	commands.getoutput(command)

def get_all_keys():
	command = "redis-cli  "
	command += "KEYS \*"
	return commands.getoutput(command).split('\n')

def key_exists(key):
	command = "redis-cli  "
	command += "EXISTS " + key
	if commands.getoutput(command) == '1':
		return True
	else:
		return False

def expire_key_in(key,seconds):
	command = "redis-cli  "
	command += "EXPIRE " + key + " " + str(seconds)
	commands.getoutput(command)

def set_key(key,value):
	command = "redis-cli  "
	command += "SET " + key + " " + value
	commands.getoutput(command)

def get_key(key):
	command = "redis-cli  "
	command += "GET " + key
	return commands.getoutput(command)

def key_time_left(key):
	command = "redis-cli  "
	command += "TTL " + key
	return commands.getoutput(command)

def key_increment_by(key,increment):
	command = "redis-cli  "
	command += "INCRBY " + key + " " + str(increment)
	commands.getoutput(command)

def delete_key(key):
	command = "redis-cli  DEL " + key
	commands.getoutput(command)

def persist_key(key):
    command = "redis-cli  PERSIST " + key
    commands.getoutput(command)

global dishes_dicti
stream = open('products.txt','r')
dishes_dicti = {}
'''for line in stream.readlines():
	line = line.split()
	a = ('_').join(line[:-1]).lower()
	b = line[-1]
	if(a in dishes_dicti):
		dishes_dicti[a] += int(b)
	else:
		dishes_dicti[a] = int(b)
'''
global dishes_db


def get_cart_id(identity):
	key = "user:"+ str(identity) +":cart:"+str(int(set_count("user:"+str(identity)+":confirmed_carts"))+1)
	return key

def get_some_dish(db, base, category):
	db = db[db["base_ing"]==base]
	db = db[db["category"]==category]
	return db

def flip(p):
	return (random.random() < p)

def recommend_dishes7(dishes_db,v_n,base,category):
	v_cards = int(10 * v_n)
	n_cards = 10 - v_cards
	cards = []
	result_veg = dishes_db[dishes_db["category"]!="bread"]
	result_non_veg = dishes_db[dishes_db["category"]!="bread"]
	result_veg = result_veg[result_veg["v_n"]=="veg"]
	result_non_veg = result_non_veg[result_non_veg["v_n"]=="nonveg"]
	for i in range(v_cards):
		temp = result_veg
		if base in ["paneer","chole","rice","dal"]:
			if(flip(0.7)):
				temp = temp[temp["base_ing"]==base]
		if(flip(0.7) and category != "U"):
			temp = temp[temp["category"]==category]
		temp =temp[:5]
		if(temp.empty == False):
			cards.append(temp.sample(n=1)["name"].tolist()[0])
	for i in range(n_cards):
		temp = result_non_veg
		if base in ["chicken","mutton","rice"]:
			if(flip(0.7)):
				temp = temp[temp["base_ing"]==base]
		if(flip(0.7) and category != "k"):
			temp = temp[temp["category"]==category]
		temp =temp[:5]
		if(temp.empty == False):
			cards.append(temp.sample(n=1)["name"].tolist()[0])
	cards = list(set(cards))
	return cards


def recommend_dishes(v_n,base,category):
	v_cards = int(10 * v_n)
	n_cards = 10 - v_cards
	cards = []
	global dishes_db
	result_veg = dishes_db[dishes_db["category"]!="bread"]
	result_non_veg = dishes_db[dishes_db["category"]!="bread"]
	result_veg = result_veg[result_veg["v_n"]=="veg"]
	result_non_veg = result_non_veg[result_non_veg["v_n"]=="nonveg"]
	for i in range(v_cards):
		temp = result_veg
		if base in ["paneer","chole","rice","dal"]:
			if(flip(0.7)):
				temp = temp[temp["base_ing"]==base]

		if(flip(0.7) and category != "k"):
			temp = temp[temp["category"]==category]

		temp =temp[:5]
		if(temp.empty == False):
			cards.append(temp.sample(n=1)["name"].tolist()[0])

	for i in range(n_cards):
		temp = result_non_veg
		if base in ["chicken","mutton","rice"]:
			if(flip(0.7)):
				temp = temp[temp["base_ing"]==base]

		if(flip(0.7) and category != "k"):
			temp = temp[temp["category"]==category]
		temp =temp[:5]
		if(temp.empty == False):
			cards.append(temp.sample(n=1)["name"].tolist()[0])
	cards = list(set(cards))
	return cards


def processing_cart_id(identity):
	return "user:" + str(identity) + ":processing cart"

def show_cart_by_id(cart_id):
	return get_hash(cart_id)

def clean_cart(cart_id):
	res = get_hash(cart_id)
	for item in res:
		if res[item] <= 0:
			delete_hash_field(cart_id, item)

def show_active_cart(identity):
	cart_id = current_cart_id(identity)
	clean_cart(cart_id)
	return get_hash(cart_id)

def get_top_item(sorted_set):
	if(key_exists(sorted_set)== True):
		return  ss_range(sorted_set,"-1","-1").keys()[0],ss_range(sorted_set,"-1","-1").values()[0]
	else:
		return (None,None)

def get_nth_item(sorted_set,n):
	return  ss_range(sorted_set,str(-(n)),str(-(n))).keys()[0],ss_range(sorted_set,str(-n),str(-n)).values()[0]

def get_total_sorted(sorted_set):
	d = ss_range(sorted_set,"0","-1")
	total = 0
	for item in d:
		total += int(d[item])
	return total

def get_top_fraction(sorted_set):
	top_item = get_top_item(sorted_set)
	_,top = top_item
	bottom = get_total_sorted(sorted_set)
	return float(top)/bottom

def get_history_reco3(dishes,identity):
	key = "user:"+str(identity)+":ordered_items"
	top_item, top_quantity = get_top_item(key)
	top_fraction = get_top_fraction(key)
	key = "user:"+str(identity)+":history:category"
	top_category,_ = get_top_item(key)
	key = "user:"+str(identity)+":history:base_ing"
	top_base,_ = get_top_item(key)
	key = "user:"+str(identity)+":history:v_n"
	v_n,_ = get_top_item(key)
	v_n_fraction = get_top_fraction(key)
	return recommend_dishes7(dishes,v_n_fraction,top_base,top_category)


def get_history_reco(identity):
	key = "user:"+str(identity)+":ordered_items"
	top_item, top_quantity = get_top_item(key)
	top_fraction = get_top_fraction(key)
	key = "user:"+str(identity)+":history:category"
	top_category,_ = get_top_item(key)
	key = "user:"+str(identity)+":history:base_ing"
	top_base,_ = get_top_item(key)
	key = "user:"+str(identity)+":history:v_n"
	v_n,_ = get_top_item(key)
	v_n_fraction = get_top_fraction(key)
	return recommend_dishes(v_n_fraction,top_base,top_category)
