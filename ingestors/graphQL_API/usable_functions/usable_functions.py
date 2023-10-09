from datetime import datetime, timedelta


def str_to_datetime(timestamp_str):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(timestamp_str, datetime_format)

def calculate_time_range(timestamp_datetime, seconds_range):
    start_timestamp = timestamp_datetime - timedelta(seconds=seconds_range)
    end_timestamp = timestamp_datetime + timedelta(seconds=seconds_range)
    return start_timestamp, end_timestamp



def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
