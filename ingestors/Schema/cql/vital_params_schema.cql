-- vital_params_schema.cql
CREATE TABLE IF NOT EXISTS vital_params (
    Patient_ID UUID,
    timestamp TIMESTAMP,
    source TEXT,
    oxygen_saturation INT,
    systolic INT,
    diastolic INT,
    etco2 INT,
    bispectral_index INT,
    PRIMARY KEY (Patient_ID, timestamp)
);