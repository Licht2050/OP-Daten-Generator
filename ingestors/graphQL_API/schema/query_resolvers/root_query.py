from ariadne import QueryType


root_query = QueryType()

@root_query.field("patient")
def resolve_patient(root, info):
    return {}

@root_query.field("environmentData")
def resolve_environment_data(root, info):
    return {}