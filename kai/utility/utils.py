import datetime


# return the current date-time as a string
def current_datetime_as_string() -> str:
    return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
