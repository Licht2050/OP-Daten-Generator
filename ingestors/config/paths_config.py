

import os


# === constants ===
MICROSECONDS_IN_A_SECOND = 1e6 
POLL_TIMEOUT = 1.0
STATUS_LOW = 'LOW'
STATUS_HIGH = 'HIGH'
STATUS_NORMAL = 'NORMAL'
STATUS_UNKNOWN = 'UNKNOWN'

# === Keyspace names ===
MEDICAL_DATA_KEYSPACE = "medical_data"



# === paths ===

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json')
VITAL_PARAMS_TABLE_DEFFINATION_PATH = os.path.join(os.path.dirname(__file__), '../schema/cql/vital_params_schema.cql')



# === Thresholds ===

BLOOD_PRESSURE_SYSTOLIC_LOW = 90
BLOOD_PRESSURE_DIASTOLIC_LOW = 60

BLOOD_PRESSURE_SYSTOLIC_HIGH = 140
BLOOD_PRESSURE_DIASTOLIC_HIGH = 90

BISPIRAL_INDEX_LOW = 40
BISPIRAL_INDEX_HIGH = 60

ETCO2_LOW = 30
ETCO2_HIGH = 50

HEART_RATE_LOW = 60
HEART_RATE_HIGH = 100

OXYGEN_SATURATION_LOW = 90
OXYGEN_SATURATION_HIGH = 100


# === Table names ===

# VITAL_PARAMS_MAPPING = {
#     'oxygen_saturation': 'oxygen_saturation',
#     'systolic': 'blood_pressure',
#     'diastolic': 'blood_pressure',
#     'etco2': 'etco2',
#     'bispectral_index': 'bispectral_index',
#     'heart_rate': 'heart_rate',
# }