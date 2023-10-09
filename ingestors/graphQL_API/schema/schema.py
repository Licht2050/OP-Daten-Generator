from ariadne import load_schema_from_path, make_executable_schema
from schema.query_resolvers.patient_resolvers import patient_query
from schema.query_resolvers.environment_resolvers import environment_data_query
from schema.query_resolvers.root_query import root_query
from ariadne import gql
from schema.subscribtion_resolver.environment_data_sub_resolver import subscription
from schema.query_resolvers.vital_params_resolvers import vital_params_query
from schema.query_resolvers.op_details_resolvers import op_details_query



# Load GraphQL schema from .graphql file
patient_type_defs = load_schema_from_path("types/patient_types.graphql")
# environment_type_defs = load_schema_from_path("types/environment_data_types.graphql")
base_type_defs = load_schema_from_path("types/base_type_defs.graphql")
vital_params_type_defs = load_schema_from_path("types/vital_params.graphql")
combined_type_defs = load_schema_from_path("types/LayeredPatientData.graphql")
op_details_query = load_schema_from_path("types/op_details.graphql")

# Merge type definitions
# combined_type_defs = base_type_defs + '\n' + patient_type_defs + '\n' + environment_type_defs
combined_type_defs = base_type_defs + '\n' + patient_type_defs + '\n' + vital_params_type_defs + '\n' + combined_type_defs + '\n' + op_details_query
schema = make_executable_schema(combined_type_defs, [root_query, vital_params_query] )

# Create executable GraphQL schema and use gql() to convert string to GraphQL language object
# schema = make_executable_schema(combined_type_defs, [root_query, environment_data_query, patient_query], subscription )


