# schema/types/patient_types.py

import graphene


class AddressType(graphene.ObjectType):
    street = graphene.String()
    city = graphene.String()
    state = graphene.String()
    postal_code = graphene.String()


class IllnessRecordType(graphene.ObjectType):
    illness = graphene.String()
    diagnosis_date = graphene.String()
    treatment = graphene.String()
    treatment_date = graphene.String()
    additional_info = graphene.String()


class HolidayRecordType(graphene.ObjectType):
    destination = graphene.String()
    activity = graphene.String()
    duration = graphene.Int()
    start_date = graphene.String()
    end_date = graphene.String()


class OPTeamType(graphene.ObjectType):
    doctors = graphene.List(graphene.String)
    nurses = graphene.List(graphene.String)
    anesthetists = graphene.List(graphene.String)


class PreOPRecordType(graphene.ObjectType):
    operation_type = graphene.String()
    operation_room = graphene.String()
    duration = graphene.Int()
    operation_date = graphene.String()
    anesthesia_type = graphene.String()
    medical_devices = graphene.List(graphene.String)

class PostOPRecordType(graphene.ObjectType):
    operation_outcome = graphene.String()
    notes = graphene.String()

class OperationRecordType(graphene.ObjectType):
    pre_op_record = graphene.Field(PreOPRecordType)
    post_op_record = graphene.Field(PostOPRecordType)


class PatientType(graphene.ObjectType):
    patient_id = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    gender = graphene.String()
    birthdate = graphene.String()
    blood_group = graphene.String()
    weight = graphene.Float()
    height = graphene.Int()
    address = graphene.Field(AddressType)
    illness_records = graphene.List(IllnessRecordType)
    holiday_records = graphene.List(HolidayRecordType)
    op_team = graphene.List(OPTeamType)
    operation_records = graphene.Field(OperationRecordType)

    