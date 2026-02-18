import datetime
d1=datetime.datetime(2026, 2, 18, 22, 0, 0)
d2=datetime.datetime(2026, 2, 17, 20, 30, 0)
diff=d1-d2
seconds=diff.total_seconds()
print(seconds)