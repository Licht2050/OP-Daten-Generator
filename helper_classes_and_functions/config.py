

import os



# === Allgemeine Konfigurationen ===

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json') # Path to the main configuration file.


# === Source-Namen ===

OP_TEAM_INFO_NAME = "op_team_info"
ENTRY_EXIT_EVENT_SOURCE_NAME = "entry_exit_events"
OP_DETAILS_NAME = 'op_details'
OP_ROOM_STATE_SOURCE_NAME = "op_room_state"
OP_RECORD_SOURCE_NAME = "op_record"
POST_RECORD_SOURCE_NAME = "post_op_record"
OP_TEAM_SOURCE_NAME = "op_team"
OUTDOOR_SOURCE_NAME = "outdoor_environment"
PATIENT_RECORD_SOURCE_NAME = "patient_records"
BIS_SOURCE_NAME = "bispectral_index"
BLOOD_PRESSURE_SOURCE_NAME = "blood_pressure"
ETCO2_SOURCE_NAME = "etco2"
HEART_RATE_SOURCE_NAME = "heart_rate"
OXYGEN_SATURATION_SOURCE_NAME = "oxygen_saturation"


PATIENT_INFO_NAME = "patient_details"
OPERATION_DETAILS_NAME = "operation_details"


# === Pfade ===

OP_TEAM_INFO_PATH = os.path.join(os.path.dirname(__file__), '../consume_op_team_info/op_team_info.json')
OP_CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '../config/op_config.json')
PATIENT_INFO_PATH = os.path.join(os.path.dirname(__file__), '../consume_patient_details/patient_info.json')
OP_RECORD_PATH = os.path.join(os.path.dirname(__file__), '../consume_op_record/op_record.json')




# === OP Room State Generator ===

TEMP_RANGE = (20.0, 25.0) # Range of temperature values for operation room.
HUMIDITY_RANGE = (30.0, 60.0) # Range of humidity values for operation room.
PRESSURE_RANGE = (980.0, 1020.0) # Range of pressure values for operation room.
ILLUMINATION_RANGE = (200.0, 1000.0)  # Range of illumination values for operation room.
DOOR_STATES = ["Offen", "Geschlossen"] # Possible door states for operation room.

# === Outdoor Generator ===

OUTDOOR_TEMP_RANGE = (-10.0, 40.0) # Range of temperature values for outdoor environment.
OUTDOOR_HUMIDITY_RANGE = (30.0, 80.0) # Range of humidity values for outdoor environment.
OUTDOOR_PRESSURE_RANGE = (980.0, 1050.0) # Range of pressure values for outdoor environment.
OUTDOOR_WIND_SPEED_RANGE = (0.0, 30.0) # Range of wind speed values for outdoor environment.


# === blood_pressure Generator ===

SYSTOLIC_RANGE = (80, 160) # Range of systolic values for blood pressure.
DIASTOLIC_RANGE = (40, 120) # Range of diastolic values for blood pressure.

# === bispiral_index Generator ===

BISPIRAL_INDEX_RANGE = (30, 70) # Range of bispiral index values.

# === etco2 Generator ===

ETCO2_RANGE = (20, 60) # Range of etco2 values.

# === heart_rate Generator ===

HEART_RATE_RANGE = (40, 120) # Range of heart rate values.

# === oxygen_saturation Generator ===

OXYGEN_SATURATION_RANGE = (80, 110) # Range of oxygen saturation values.

# === Sonstige Konstanten ===

SECONDS_IN_YEAR = 365 * 24 * 60 * 60 # Number of seconds in a year, used for time calculations.
REQUIRED_TEAM_KEYS = ["doctors", "nurses", "anesthetists"]


# === Holiday Record Generator ===

HOLIDAY_DURATION_RANGE = (3, 14) # Range of holiday durations in days.
START_DATE_RANGE = (30, 180) # Range of start dates for holidays within the last 6 months.


PLACES = [
    "Paris", "Malediven", "New York City", "Trolltunga", 
    "Grand Canyon", "Sambia und Malawi", "Botswana und Simbabwe",
    "Bali", "Dschungel-Bungalows an der Nordküste"
] # List of places for holiday records.
ACTIVITIES = {
    "Grand Canyon": ["Wandern", "Campingtouren", "Skywalk"],
    "Trolltunga": ["Campingtouren", "Spaziergänge"],
    "New York City": ["Times Square besucht", "Broadway-Show gesehen", "Central Park erkundet"],
    "Paris": ["Eiffelturm besichtigt", "Louvre Museum besucht"],
    "Malediven": ["Strandspaziergang gemacht", "Schnorcheln", "Tauchen"],
    "Tokio": ["Asakusa Tempel besichtigt", "Shinjuku Gyoen Park besucht", "Sushi gegessen"],
    "Bali": ["Wandern", "Buschwanderungen", "Wildbeobachtung zu Fuß"],
    "Sambia und Malawi": ["Abenteuerliche Kanufahrt", "Wildbeobachtung zu Fuß", "Schnorcheln"],
    "Botswana und Simbabwe": ["Pirschfahrt", "Buschwanderungen", "Helikopterflug", "Wild Water Rafting", "Bungee Jumping"],
    "Dschungel-Bungalows an der Nordküste": ["Wandern"]
} # Dictionary mapping places to possible activities.



# === Patient Record Generator ===

NAMES = ["Müller", "Bäcker", "Schmidt", "Schneider", "Hoffman", "Ajadi", "Weber", "Fischer", "Meyer", "Maier", "Kraus", "Herrmann"]  # List of possible last names for patients.
NAME_BY_GENDER = {
    "weiblich": ["Maria", "Elisabeth", "Ruth", "Hilde", "Eva", "Charlotte", "Erika"],
    "männlich": ["Hans", "Karl", "Walter", "Kurt", "Friedrich", "Fritz", "Heinrich"]
} # Dictionary mapping genders to first names.
GENDERS= ["weiblich", "männlich"]  # List of genders.
STREETS = ["Banhofstraße 1", "Goebenstraße 40", "Am Rastpfuhl 3", "St. Johanner Str.", "Breite Str."] # List of possible streets for patient addresses.
CITIES = ["Saarbreucken"] # List of cities.
POSTAL_CODES = [66113, 66117, 6123, 66111]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-"]
WEIGHT_RANGE = (45, 120)
HEIGHT_RANGE = (140, 195)



# === Pre-existing Illness Generator ===

ILLNESSES = [
    "Herzinsuffizienz", "Schlaganfall", "Herzinfarkt", "Lungenembolie",
    "Nierenversagen", "Diabetes mellitus", "Asthma", "Bluthochdruck"
]
TREATMENTS = ["Medikamente", "Operation", "Physiotherapie", "Dialyse"]
DIAGNOSED_RANGE = (SECONDS_IN_YEAR*3, SECONDS_IN_YEAR*15) # Zeitraum für Diagnosedatum: 3 bis 15 Jahre zurück
TREATED_RANGE = (SECONDS_IN_YEAR*1, SECONDS_IN_YEAR*6) # Zeitraum für Behandlungsdatum: 1 bis 6 Jahre nach Diagnose
