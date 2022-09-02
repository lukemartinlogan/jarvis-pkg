from jarvis_pkg import Version

min = Version('v0.0.0')
max = Version('v1.0.0')
v = Version('v1.5.0')

print(v <= max)
print(v >= min)
