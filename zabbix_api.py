#!/usr/bin/env python
#This script get the zabbix item value according to the
#groupid,hostid adn itemid you select,also the begin
#date and end date you specified in the command line.

import urllib2
import json
import argparse
import time

# To have access to zabbix api, you need to get the auth string first.
def authenticate(url, username, password):
    values = {'jsonrpc': '2.0',
              'method': 'user.login',
              'params': {
                  'user': username,
                  'password': password
              },
              'id': '0'
              }

    data = json.dumps(values)
    req = urllib2.Request(url, data, {'Content-Type': 'application/json-rpc'})
    response = urllib2.urlopen(req, data)
    output = json.loads(response.read())

    try:
        message = output['result']
    except:
        message = output['error']['data']
        print message
        quit()

    return output['result']

# Return the groupids in you zabbix server
def getGroupid(url,auth):
	""" Return group ids """
	header = {"Content-Type":"application/json"}
	# request json
	data = json.dumps(
	{
   	"jsonrpc":"2.0",
   	"method":"hostgroup.get",
   	"params":{
       "output":["groupid","name"],
   },
   "auth":auth, # theauth id is what auth script returns, remeber it is string
   "id":0,
	})
	# create request object
	request = urllib2.Request(url,data)
	for key in header:
   		request.add_header(key,header[key])
	# get group id list
	try:
   		result = urllib2.urlopen(request)
	except urllib2.URLError as e:
   		if hasattr(e, 'reason'):
       			print 'We failed to reach a server.'
       			print 'Reason: ', e.reason
   		elif hasattr(e, 'code'):
       			print 'The server could not fulfill the request.'
       			print 'Error code: ', e.code
	else:
   		response = json.loads(result.read())
   		result.close()
   		print "Number Of Groups: ", len(response['result'])
   	  for group in response['result']:
      			print "Group ID:",group['groupid'],"\tGroupName:",group['name']
    #Yeah, you must select the group id manually.Maybe you can let it be automatic. =_=
    #Remember what you input will be stored in string.
		se_groupid = raw_input('Please Select Group ID: ')
		return se_groupid.strip()

def getHostid(groupid,url,auth):
	""" Return hostids according the groupid """
	#The same thing in every function.
	header = {"Content-Type":"application/json"}
	# request json
	data = json.dumps(
	{
   	"jsonrpc":"2.0",
   	"method":"host.get",
   	"params":{
       "output":["hostid","name"],
       "groupids":groupid
   	},
   	"auth":auth, # theauth id is what auth script returns, remeber it is string
   	"id":0,
	})
	# create request object
	request = urllib2.Request(url,data)
	for key in header:
   		request.add_header(key,header[key])
	# get host list
	try:
   		result = urllib2.urlopen(request)
	except urllib2.URLError as e:
   		if hasattr(e, 'reason'):
       			print 'We failed to reach a server.'
       			print 'Reason: ', e.reason
   		elif hasattr(e, 'code'):
       			print 'The server could not fulfill the request.'
       			print 'Error code: ', e.code
	else:
   		response = json.loads(result.read())
   		result.close()
   		print "Number Of Hosts: ", len(response['result'])
   		for host in response['result']:
       			print "Host ID:",host['hostid'],"HostName:",host['name']
		se_hostid = raw_input('Please select Host ID: ')
		return se_hostid.strip()

def getItemid(hostid,url,auth):
	"""Return the item ids according to the hostids"""
	header = {"Content-Type":"application/json"}
	data = json.dumps(
	{
   	"jsonrpc":"2.0",
   	"method":"item.get",
   	"params":{
       "output":["itemids","key_"],
       "hostids":hostid,
  #Because the item id is too much, I filter cpu idle,disk,memory utilization and network traffic.
	"filter":{
		'key_':["system.cpu.util[,idle]","vfs.fs.size[/,pfree]","vm.memory.size[pavailable]","net.if.in[eth0]","net.if.out[eth0]"],
	},
   	},
   	"auth":auth, # theauth id is what auth script returns, remeber it is string
   	"id":0,
	})
	# create request object
	request = urllib2.Request(url,data)
	for key in header:
   		request.add_header(key,header[key])
	# get host list
	try:
   		result = urllib2.urlopen(request)
	except urllib2.URLError as e:
   		if hasattr(e, 'reason'):
       			print 'We failed to reach a server.'
       			print 'Reason: ', e.reason
	   	elif hasattr(e, 'code'):
    	   		print 'The server could not fulfill the request.'
       	   		print 'Error code: ', e.code
	else:
   		response = json.loads(result.read())
   		result.close()
   		print "Number Of Items: ", len(response['result'])
   		for item in response['result']:
       			print item
		se_itemid = raw_input('Please select item id: ')
		#When get the item value, I can not figure out whether the value is float or unsigned.
		#just the four items it filter above,only the network traffic value is float, So It
		#let you specify.
		flag = raw_input('If You Want Network Traffic Value Input 3,else Input 0.')
		return (se_itemid.strip(),flag)

def getHistory(itemid,url,auth,timefrom,timetill):
	header = {"Content-Type":"application/json"}
	# request json
	data = json.dumps(
	{
   	"jsonrpc":"2.0",
   	"method":"history.get",
   	"params":{
       "output":"extend",
       "history":itemid[1],
       "itemids":itemid[0],
       "time_from":timefrom,
        "time_till":timetill
   	},
   	"auth":auth, # theauth id is what auth script returns, remeber it is string
   	"id":0,
	})
	# create request object
	request = urllib2.Request(url,data)
	for key in header:
   		request.add_header(key,header[key])
	# get host list
	try:
   		result = urllib2.urlopen(request)
	except urllib2.URLError as e:
   		if hasattr(e, 'reason'):
       			print 'We failed to reach a server.'
       			print 'Reason: ', e.reason
   		elif hasattr(e, 'code'):
       			print 'The server could not fulfill the request.'
       			print 'Error code: ', e.code
	else:
   		response = json.loads(result.read())
   		result.close()
		len_value=len(response['result'])
		value=[]
		#the value is integer
		#well,the algorithm is not good, it takes some time.
		if itemid[1] == '3':
			for key in response['result']:
              value.append(int(key['value']))
      value=sorted(value) 
			max_value=value[len_value-1]/1024.0
			min_value=value[0]/1024.0
			sum=0
			for i in range(len_value):
				sum+=int(value[i])
			aver_value=sum/len_value/1024.0
			print "Max Value: %f kbps,Average Value: %f kbps,Min Value: %f kbps" % (max_value,aver_value,min_value)
		#the value is float
		if itemid[1] == '0':
			for key in response['result']:
                value.append(float(key['value']))
      value=sorted(value)
			max_value=float(value[len_value-1])
      min_value=float(value[0])
      sum=0.0
      for i in range(len_value):
      sum+=value[i]
      aver_value=sum/len_value
      print "Max Value: %f,Average Value: %f,Min Value: %f" % (max_value,aver_value,min_value)

def getTimestamp(timestring):
	timetuple = time.strptime(timestring,"%Y-%m-%d %H:%M:%S")
	return time.mktime(timetuple)
	
def main():
    url = 'http://10.101.88.99/api_jsonrpc.php'
    username = "admin"
    password = "zabbix"

    parser = argparse.ArgumentParser(description='Create Zabbix screen from all of a host Items or Graphs.')
    parser.add_argument('-b', dest='begintime', type=str,
                        help='the begin time, eg: 2016-05-02 00:00:00')
    parser.add_argument('-e', dest='endtime', type=str,
                        help='the end time, eg: 2016-05-03 00:00:00')
    args = parser.parse_args()
    timefrom = getTimestamp(args.begintime)
    timetill = getTimestamp(args.endtime)
    auth = authenticate(url, username, password)
    while True:
	  se_exit = raw_input('q to quit,c to continue: ')
  	if se_exit.strip() == 'q':break
    groupids = getGroupid(url,auth)
    hostids = getHostid(groupids,url,auth)
    itemids = getItemid(hostids,url,auth)
    getHistory(itemids,url,auth,timefrom,timetill)

if __name__ == '__main__':
    main()
