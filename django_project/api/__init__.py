import pymongo

dbclient = pymongo.MongoClient("45.55.232.5:27017")
dbclient.perkkx.authenticate('perkkxAdmin', 'perkkx@123', mechanism='MONGODB-CR')
db = dbclient.perkkx