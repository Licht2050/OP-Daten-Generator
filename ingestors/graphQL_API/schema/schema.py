from ariadne import load_schema_from_path, make_executable_schema
from schema.resolvers.patient_resolvers import query




# Load GraphQL schema from .graphql file
type_defs = load_schema_from_path("types/patient_types.graphql")



schema = make_executable_schema(type_defs, query)

