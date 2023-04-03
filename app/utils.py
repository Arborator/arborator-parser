import datetime
import pytz

def get_readable_current_time_paris_ms():
    # Universal timestamp now
    now = datetime.datetime.now()
    # Create a timezone object for Paris
    paris_tz = pytz.timezone('Europe/Paris')
    # Convert the datetime object to the Paris timezone
    now_paris = now.astimezone(paris_tz)
    # Format datetime object as string with two digits for %f
    dt_string = now_paris.strftime('%Y-%m-%d_%H:%M:%S.%f')[:23]
    return dt_string