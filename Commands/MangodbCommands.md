# List all documents of collection
db.getCollection("Holiday-Record").find()

# Drop Collection
db.getCollection("Holiday-Record").drop()

# Create Collection
db.createCollection(HolidayRecords)