# 

/venv/lib/python3.10/site-packages/graphql_server/
change the line 
```
from collections import namedtuple, MutableMapping
```
to 
```
from collections import namedtuple
from collections.abc import MutableMapping
```

