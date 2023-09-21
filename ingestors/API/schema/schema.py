# schema/schema.py
import asyncio
import logging
import graphene
from graphql import GraphQLField, GraphQLInt, GraphQLObjectType

from pub_sub.async_iterable_wrapper import AsyncIterableWrapper
from .types.patient_types import (PatientType, AddressType, IllnessRecordType, 
                                  HolidayRecordType, OPTeamType, OperationRecordType)
from resolvers.patient_resolvers import (resolve_get_all_patient_by_op_type, resolve_get_patient_by_id, 
                                 resolve_get_all_patient, resolve_get_all_patient_by_op_date, 
                                 resolve_get_all_patient_by_op_room,
                                 resolve_get_all_patient_by_anesthesia_type
                                )
from .types.environment_types import IndoorEnvironmentData
from resolvers.environment_resolvers import resolve_get_all_indoor_environment_data   
from pub_sub.pub_sub import async_iterable_wrapper

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


class IndoorEnvironmentDataSubscription(graphene.ObjectType):
    indoor_environment_data_update = graphene.Field(
        IndoorEnvironmentData,
        op_room=graphene.String(required=True),
    )

    @staticmethod
    async def resolve_indoor_environment_data_update(root, info, op_room):
        print("Resolver called")  # Add this print statement
        if info is not None:
            info.context['logger'].info(f"Started subscription for op_room: {op_room}")

        async_iter_wrapper = AsyncIterableWrapper()
        print(f"Async iterable wrapper before generating test data: {async_iter_wrapper}")  # Add this print statement
        asyncio.create_task(generate_test_data(async_iter_wrapper, op_room))
        
        print(f"Returning async iterable: {async_iter_wrapper}")  # Add this print statement
        return async_iter_wrapper


async def generate_test_data(async_iter_wrapper, op_room):
    for i in range(10):
        async_iter_wrapper.on_next({'opRoom': op_room, 'co2': i})
        await asyncio.sleep(1)

schema = graphene.Schema(query=Query, subscription=IndoorEnvironmentDataSubscription)