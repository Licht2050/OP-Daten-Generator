# Open Mongodb shell
mongosh

# List all db
show dbs

# create db
use db_name

# Drop db
db.dropDatabase()

# Create Collection
db.createCollection(HolidayRecords)

# List all collections
show collections

# exit db
exit

exit
# Select db
use db_name

# List all collections
show collections


# List all documents of collection
db.getCollection("Holiday-Record").find()

# List all documents of collection with pretty
db.getCollection("Holiday-Record").find().pretty()


# query document with condition
db.getCollection("Holiday-Record").find({"name":"Raj"}).pretty()

# query document with condition
db.getCollection("Holiday-Record").find({"name":"Raj","age":21}).pretty()

# Drop Collection
db.getCollection("Holiday-Record").drop()

# Create Collection
db.createCollection(HolidayRecords)
