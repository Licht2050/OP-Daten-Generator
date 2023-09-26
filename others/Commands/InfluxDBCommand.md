# show databases
show databases

# create database
create database <database_name>

# delete database
drop database <database_name>

# show measurements
show measurements

# create measurement
create measurement <measurement_name>

# delete measurement
drop measurement <measurement_name>

# query data
select * from <measurement_name>

# query data with condition
select * from <measurement_name> where <tag_key> = '<tag_value>'

# query data with condition
select * from <measurement_name> where <tag_key> = '<tag_value>' and <tag_key> = '<tag_value>'

# query data with condition
select * from <measurement_name> where <tag_key> = '<tag_value>' or <tag_key> = '<tag_value>'

# query data with condition
select * from <measurement_name> where <tag_key> = '<tag_value>' and <tag_key> = '<tag_value>' or <tag_key> = '<tag_value>'

# query data with condition
select * from <measurement_name> where <tag_key> = '<tag_value>' and <tag_key> = '<tag_value>' or <tag_key> = '<tag_value>' and <tag_key> = '<tag_value>'

# query data with condition
select * from <measurement_name> where <tag_key> = '<tag_value>' and <tag_key> = '<tag_value>' or <tag_key> = '<tag_value>' and <tag_key> = '<tag_value>' or <tag_key> = '<tag_value>'

# query data with condition
select * from <measurement_name> where <tag_key> = '<tag_value>' and <tag_key> = '<tag_value>' or <tag_key> = '<tag_value>' and <tag_key> = '<tag_value>' or <tag_key> = '<tag_value>' and <tag_key> = '<tag_value>'


# show tag values from <measurement_name>
show tag values from <measurement_name> with key = <tag_key>

# show tag values
show tag values with key = <tag_key>

# show tag keys
show tag keys

# show field keys
show field keys

# show series
show series

# show retention policies
show retention policies

# show continuous queries
show continuous queries

# show stats
show stats

# show diagnostics
show diagnostics

# show subscriptions
show subscriptions

# show shard groups
show shard groups