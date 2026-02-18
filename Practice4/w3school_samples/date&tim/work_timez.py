import datetime
import pytz

# defining the object and localising it to a timezone
dt = datetime.datetime(2001, 11, 15, 1, 20, 25)
tz = pytz.timezone('Asia/Almaty')
dt = tz.localize(dt)

# Creating a new timezone
new_tz = pytz.timezone('America/New_York')

# Changing the timezone of our object
converted = dt.astimezone(new_tz)

# Printing out new time
print(converted)