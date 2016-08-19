# -*- coding: utf-8 -*- 
import httplib
import urllib
import time
import pickle
#from  datetime  import  *
import sys
import os
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
#today = datetime.now().strftime('%Y-%m-%d')
#dump_file = open(today, 'wb+')
stock_group = [
	{'name':'煤炭', 'stocks':{'000552','600348','000983','601001','600792','601898','601225','600971','600121','002128','600188'}},
	{'name':'航空装备', 'stocks':{'002190','000738','600391','600893','600316','000768','002013','600372'}},
	{'name':'证券', 'stocks':{'000783','002500', '002736', '600999', '600030', '601788', '601377', '000166', '600109', '000776', '601688', '601901', '002797', '000712', '601211', '600958', '600369', '601555', '000686'}},
	{'name':'黄金', 'stocks':{'600766','600311','000506','600687','600547','600489','002237','600988','601899','601069','002155'}},
	{'name':'饮料制造', 'stocks':{'600779','000568','000869','600199','600702','002304','002646','000596','600809','000858','603589','600519','000799','603369','603198'}},
	{'name':'银行', 'stocks':{'600016','002142','601998','600000','601009','600036','601818','601328','000001','601988','600015','601166','601288','601939','601169','601398'}},
	{'name':'基础建设', 'stocks':{'600528','601611','601186','601390','601800','601669'}},
]

def get_stock_region(stock_code):
	if(stock_code[0] == '6'):
		return 'sh'
	if(stock_code[0] == '0'):
		return 'sz'

def get_current_price(stock_code):
	conn = httplib.HTTPConnection('hq.sinajs.cn')
	conn.request('GET', '/list=' + str(get_stock_region(stock_code)) + stock_code)
	result = conn.getresponse()
	data = result.read()
	start_quote_index = data.find('"')
	#print start_quote_index
	end_quote_index = data.find('"', start_quote_index + 1)
	#print end_quote_index
	data = data[start_quote_index + 1:end_quote_index].decode('gbk')
	#print data
	data = data.split(',')
	name = data[0]
	#print name
	current_price = data[3]
	#print current_price
	time = data[len(data) - 2]
	#print time
	return (current_price, time)

def compare_value(value1, value2):
	thres = 0.001
	rate = abs((float(value1) - float(value2))/float(value1))
	if value1 > value2 and rate > thres:
		return 1
	elif value1 < value2 and rate > thres:
		return -1
	else:
		return 0	

#data = get_current_price('600639')
#print dataa

price_dict = {}
#price_dict['aaa'] = {}
#price_dict['aaa']['111'] = 'bbb'

current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print current_time
print price_dict
iter_count = 0
time.sleep(1)
step = 10
while(1):
	iter_count = iter_count + 1
	if iter_count % 10 == 0:
		print '1 iter...'
		#log_file.write('1 iter...\n')
	if os.path.exists(today):
		dump_file = open(today, 'r')
		price_dict = pickle.load(dump_file)
		dump_file.close()
	for group in stock_group:
		#print group['name']
		#print group['stocks']
		group_score = 0
		stock_score_dict = {}
		str_group_score = ''
		str_group_change_rate = ''
		for stock in group['stocks']:
			try:
				(price, _time) = get_current_price(stock)
			except Exception as e:
				print 'exception: ' + str(e) + ' stock: ' + str(stock)
				continue
			if stock not in price_dict:
				price_dict[stock] = {}
			price_dict[stock][_time] = price
			#print stock
			keys = price_dict[stock].keys()
			#print keys
			#price_dict[stock] = sorted(price_dict[stock].iteritems(), key=lambda d:d[0])
			sorted_keys = sorted(keys, reverse=True)
			#print sorted_keys
			#print sorted_keys[0]

			if len(sorted_keys) < step * 2:
				continue
			time1 = sorted_keys[0]
			time2 = sorted_keys[step - 1]
			time3 = sorted_keys[step * 2 - 1]
			
			price1 = price_dict[stock][time1]
			price2 = price_dict[stock][time2]
			price3 = price_dict[stock][time3]

			score = 0
			score = score + compare_value(price1, price2)
			#socre = score + compare_value(price2, price3)

			stock_score_dict[stock] = score
			str_group_score = str_group_score + str(score) + ', '
			str_group_change_rate = str_group_change_rate + str((float(price1) - float(price2))/(float(price1))) + ','

			if score == 1:
				group_score = group_score + 1
			if score == -1:
				group_score = group_score - 1
	
		#print 'group score: ' + str_group_score
		#print 'total score: ' + str(group_score)
		#print 'group change rate: ' + str_group_change_rate
		if abs(group_score) > len(group['stocks']) * 3/4:
			log_file = open(today + '-log', 'a')
			if group_score > 0:
				print group['name'] + 'up!'
				log_file.write(group['name'] + 'up!\n')
				for k in stock_score_dict.keys():
					if stock_score_dict[k] == 1:
						print 'recommended stock: ' + k
						log_file.write('recommended stock: ' + k + '\n')
			if group_score < 0:
				print group['name'] + 'down!'
				log_file.write(group['name'] + 'down!\n')
				for k in stock_score_dict.keys():
					if stock_score_dict[k] == -1:
						print 'recommended stock: ' + k
						log_file.write('recommended stock: ' + k + '\n')
			current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			print current_time
			log_file.write(current_time + '\n')
			print 'group score: ' + str_group_score
			log_file.write('group score: ' + str_group_score + '\n')
			print 'group change rate: ' + str_group_change_rate
			log_file.write('group change rate: ' + str_group_change_rate + '\n')
			print 'total score: ' + str(group_score)
			log_file.write('total score: ' + str(group_score) + '\n')
			log_file.close()
	#time.sleep(1)
	#print("\a")
	#dump_file.truncate()
	#dt = datetime.now()
	#hms_str = dt.strftime('%H:%M:%S')
	hms_str = time.strftime('%H:%M:%S',time.localtime(time.time()))
	if hms_str > '15:05:00':
	        sys.exit()

	dump_file = open(today, 'wb+')
	pickle.dump(price_dict, dump_file)
	dump_file.close()

print price_dict
dump_file.close()
