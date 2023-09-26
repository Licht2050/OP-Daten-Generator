# connect to Cassandra shell
cqlsh
# create keyspace
CREATE KEYSPACE IF NOT EXISTS test WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
# create table
CREATE TABLE IF NOT EXISTS test.users (id int PRIMARY KEY, name text, age int);
# insert data
INSERT INTO test.users (id, name, age) VALUES (1, 'John', 42);
INSERT INTO test.users (id, name, age) VALUES (2, 'Jane', 36);
# select data
SELECT * FROM test.users;
# delete data
DELETE FROM test.users WHERE id = 1;
# drop table
DROP TABLE test.users;
# drop keyspace
DROP KEYSPACE test;
```



# show keyspace
```bash
cqlsh> DESCRIBE KEYSPACES;
```

# show tables
```bash
cqlsh> DESCRIBE TABLES;
```