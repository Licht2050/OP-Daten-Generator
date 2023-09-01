-- oxygen_saturation
CREATE TABLE IF NOT EXISTS oxygen_saturation (
    Patient_ID UUID,
    bucket_date DATE,
    timestamp TIMESTAMP,
    oxygen_saturation INT,
    status TEXT,
    PRIMARY KEY ((patient_id, bucket_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp ASC);

-- blood_pressure
CREATE TABLE IF NOT EXISTS blood_pressure (
    Patient_ID UUID,
    bucket_date DATE,
    timestamp TIMESTAMP,
    systolic INT,
    diastolic INT,
    status TEXT,
    PRIMARY KEY ((patient_id, bucket_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp ASC);

-- etco2
CREATE TABLE IF NOT EXISTS etco2 (
    Patient_ID UUID,
    bucket_date DATE,
    timestamp TIMESTAMP,
    etco2 INT,
    status TEXT,
    PRIMARY KEY ((patient_id, bucket_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp ASC);

-- bispectral_index
CREATE TABLE IF NOT EXISTS bispectral_index (
    Patient_ID UUID,
    bucket_date DATE,
    timestamp TIMESTAMP,
    bispectral_index DECIMAL,
    status TEXT,
    PRIMARY KEY ((patient_id, bucket_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp ASC);

-- heart_rate
CREATE TABLE IF NOT EXISTS heart_rate (
    Patient_ID UUID,
    bucket_date DATE,
    timestamp TIMESTAMP,
    heart_rate INT,
    status TEXT,
    PRIMARY KEY ((patient_id, bucket_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp ASC);