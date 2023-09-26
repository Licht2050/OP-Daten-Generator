# schema/schema.py
import asyncio
import logging
import graphene
from graphql import GraphQLField, GraphQLInt, GraphQLObjectType

# from pub_sub.async_iterable_wrapper import AsyncIterableWrapper
from .types.patient_types import (PatientType, AddressType, IllnessRecordType, 
                                  HolidayRecordType, OPTeamType, OperationRecordType)
from resolvers.patient_resolvers import (resolve_get_all_patient_by_op_type, resolve_get_patient_by_id, 
                                 resolve_get_all_patient, resolve_get_all_patient_by_op_date, 
                                 resolve_get_all_patient_by_op_room,
                                 resolve_get_all_patient_by_anesthesia_type
                                )
from .types.environment_types import IndoorEnvironmentData
from resolvers.environment_resolvers import resolve_get_all_indoor_environment_data   
# from pub_sub.pub_sub import async_iterable_wrapper

import asyncio
from datetime import datetime
from graphene import ObjectType, String, Schema, Field
from rx import Observable
from ariadne import QueryType
from ariadne import make_executable_schema



query = QueryType()


class Query(graphene.ObjectType):
    get_patient_by_id = graphene.Field(PatientType, patient_id=graphene.String(required=True), resolver=resolve_get_patient_by_id)
    get_all_patients = graphene.List(PatientType, resolver=resolve_get_all_patient)
    get_all_patient_by_op_room = graphene.List(PatientType, op_room=graphene.String(required=True), resolver=resolve_get_all_patient_by_op_room)
    get_all_patients_by_op_date = graphene.List(PatientType, op_date=graphene.String(required=True), resolver=resolve_get_all_patient_by_op_date)
    get_all_patients_by_op_type = graphene.List(PatientType, op_type=graphene.String(required=True), resolver=resolve_get_all_patient_by_op_type)
    get_all_patients_by_anesthesia_type = graphene.List(PatientType, anesthesia_type=graphene.String(required=True), resolver=resolve_get_all_patient_by_anesthesia_type)


    # environment data
    get_all_environment_data = graphene.List(IndoorEnvironmentData, resolver=resolve_get_all_indoor_environment_data)

logging.basicConfig(level=logging.INFO)






graphene_schema = graphene.Schema(query=Query)
schema = make_executable_schema()
