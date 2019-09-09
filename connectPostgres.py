import psycopg2
import configparser
from datetime import date, timedelta, datetime

#create a dictionary of parameter using configparser
def config (configFile = 'config/db.txt', section = 'postgresql'):
	parser = configparser.ConfigParser()
	parser.read(configFile)
	return dict(parser.items(section))

def insertSQL (table,**fieldsValues):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	fieldState =str()
	valueState =str()
	for field, value in fieldsValues.items():
		fieldState = fieldState + "%s, "%(field)
		valueState = valueState + "%s, "%(value)
	state = "INSERT INTO " + table + ' (' + fieldState[0:-2] + ') VALUES (' + valueState[0:-2] + ')'
	print (state)
	cur.execute(state)
	conn.commit()
	conn.close()

def selectAll (table):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	cur.execute("SELECT * FROM %s"%(table))
	records = cur.fetchall()
	conn.close()
	return records

#select column normal
def selectCol (table, *fields, where):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	fieldState =str()
	for field in fields:
		fieldState = fieldState + "%s, "%(field)
	state = 'SELECT ' + fieldState[0:-2] + ' FROM ' + table + ' WHERE ' + where
	cur.execute(state)
	records = cur.fetchall()
	conn.close()
	return records
#select column between 2 date
#selectCol_2_date ('thistable', *[list 2 date])
def selectCol_2_date (table, *fields, date1, date2):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	fieldState =str()
	for field in fields:
		fieldState = fieldState + "%s, "%(field)
	state = 'SELECT ' + fieldState[0:-2] + ' FROM ' + table + ' WHERE date between  \'%s\' and \'%s\''%(date1,date2)
	print (state)
	cur.execute(state)
	records = cur.fetchall()
	conn.close()
	return records

#usage: update ('hehe',*{a = 1, b = 2}, where = "he = 'him'")
#or: update ('hehe',a = 1, b = 2, where = "he = 'him'")

def update (table,where,**fieldsValues):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	fieldValueState = str()
	for field, value in fieldsValues.items():
		fieldValueState = fieldValueState + field + ' = ' + "'%s', " %(value)
	state = 'UPDATE ' + table + ' SET ' + fieldValueState[0:-2] +' WHERE ' + where
	cur.execute(state)
	conn.commit()
	conn.close()

def getGeom(Xmin,Ymin,Xmax,Ymax,Projection):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	state = 'SELECT ST_MakeEnvelope('+ str(Xmin) +',' + str(Ymin) +','+ str(Xmax) +','+ str(Ymax) +','+ str(Projection)  +')'
	cur.execute(state)
	records = cur.fetchall()
	conn.close()
	return records[0][0]

def select_since_6months(table, today = None):
	if today == None:
		today = date.today()
	else:
		today = datetime.strptime(today, "%Y%m%d").date()

	back_7months = today - timedelta(210)
	today = today.strftime("%Y-%m-%d")
	back_7months = back_7months.strftime("%Y-%m-%d")
	paths_1 = selectCol_2_date('%s'%(table), 'path', date1 = '%s'%(back_7months), date2 = '%s'%(today))
	paths_2 = list()
	for path in paths_1:
		paths_2.append(path[0])
	return paths_2
