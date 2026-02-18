from datetime import datetime

start = datetime.strptime("4:25:40", "%H:%M:%S")
end = datetime.strptime("11:40:10", "%H:%M:%S")

difference = end - start

seconds = difference.total_seconds()
print('difference in seconds is:', seconds)

minutes = seconds / 60
print('difference in minutes is:', minutes)

hours = seconds / (60 * 60)
print('difference in hours is:', hours)