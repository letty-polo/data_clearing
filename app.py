from flask import Flask, request, render_template, session
import os
import requests
import pymysql

app = Flask(__name__)


@app.route("/")
def index():
	user = os.environ['API_USER']
	password = os.environ['API_PASS']
	return render_template("index.html")



@app.route('/response.html',methods=['GET', 'POST'])
def response():
	message=""
	mysqluser=os.environ['LDAP_USER']
	mysqlpass=os.environ['LDAP_PASS']
	db=pymysql.connect(host='mysql-slave.prod.nym1.adnxs.net',user=mysqluser,password=mysqlpass,db='bidder')
	try:
		segments = request.form.get('segments')
		query= "select dpc.id as dpc_id,dpcs.data_provider_member_id,dpcs.is_public,dpcs.segment_id,s.short_name,s.code,dpc.price_cpm as category_price,dpcs.active,dpcs.deleted,dpcs.created_on from bidder.data_price_category_segment dpcs join api.segment s on dpcs.segment_id= s.id join data_price_category dpc on dpc.id=dpcs.data_price_category_id where dpcs.segment_id in (" + segments +")"  
		with db.cursor() as cursor:
			cursor.execute(query)
			found = cursor.fetchall()


		
		clearing=[]
		out_clearing=[]
		custom_rates=[]
		not_clearing=[]
		clearing_list=[]
		data_members=[]
		for id in found:    #found contains all valid segments from the user input
			clearing_list.append(int(id[3]))  #clearing_list contains the ids of the segments having data clearing
			clearing.append(str(id[3]))	       #clearing_list contains the ids of the segments having data clearing
			custom_rates.append(str(id[0]))  #custom_rates contains the data price category on clearing segments
			data_members.append(str(id[1]))    # data_members contains the data providers members ids
		all_segments=segments.split(",")	#all_segments transform the user input into a tuple
		for (id) in all_segments:
			if str(id) not in clearing:
				out_clearing.append(id)		#out_clearing contains all the segment not having clearing
		notClearingString = ','.join(out_clearing)  #string to use in query to get not clearing segments info
		custom_ratesString= ','.join(custom_rates)  # string to use in query to get custom rates data
		all_data_members= ','.join(data_members)
		if notClearingString != "" :
			query= "SELECT id,short_name,active,deleted,member_id,	object_type_id FROM api.segment where id in (" + notClearingString +")"  
			with db.cursor() as cursor:
				cursor.execute(query)
				not_clearing = cursor.fetchall()

		custom_rates_found =""
		if custom_ratesString != "" :
			query= "select id,	data_price_category_id,	buyer_member_id, data_provider_member_id, price_cpm, currency_code,	active,	deleted from bidder.data_price_category_buyer_custom_price where data_price_category_id in (" + custom_ratesString +")"  
			with db.cursor() as cursor:
				cursor.execute(query)
				custom_rates_found = cursor.fetchall()


	
		query= "select mdas.segment_id,mdas.buyer_member_id from api.member_data_access_segments mdas where mdas.deleted=0 and mdas.segment_id in (" + segments +")"
		with db.cursor() as cursor:
			cursor.execute(query)
			sharing_buyers = cursor.fetchall()

		buyers_all=""
		if all_data_members != "" :
			query= "select buyer_member_id,data_member_id from api.member_data_access where  segment_exposure = 'all' and deleted=0 and data_member_id in (" + all_data_members + ")"
			with db.cursor() as cursor:
				cursor.execute(query)
				buyers_all = cursor.fetchall()
		
	except:
		message="No segments found, please make sure you are using comma separated segments ids in the text box"

	
	
	if message=="":
		return render_template("response.html",found=found,not_clearing=not_clearing,custom_rates_found=custom_rates_found,clearing_list=clearing_list,sharing_buyers=sharing_buyers,buyers_all=buyers_all)
	else:
		return render_template("response.html",message=message)

if __name__ == '__main__':
	app.run(debug=True,host='3851.lpolo.user.nym2.adnexus.net',port=8805)
 
 
 