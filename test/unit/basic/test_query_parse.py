from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.basic.version import Version

q1 = PackageQuery("hello")
assert(q1.name == "hello")

q2 = PackageQuery("hello@1.0.0")
assert(q2.name == "hello")
assert(q2.versions[0][0] == Version("1.0.0"))
assert(q2.versions[0][1] == Version("1.0.0"))

q3 = PackageQuery("hello@1.0.0:")
assert(q3.name == "hello")
assert(q3.versions[0][0] == Version("1.0.0"))
assert(q3.versions[0][1] == Version("max"))

q4 = PackageQuery("hello@:1.0.0")
assert(q4.name == "hello")
assert(q4.versions[0][0] == Version("min"))
assert(q4.versions[0][1] == Version("1.0.0"))

q5 = PackageQuery("hello@1.0.0:2.0.0")
assert(q5.name == "hello")
assert(q5.versions[0][0] == Version("1.0.0"))
assert(q5.versions[0][1] == Version("2.0.0"))

q6 = PackageQuery("hello@1.0.0:2.0.0 +hi")
assert(q6.name == "hello")
assert(q6.versions[0][0] == Version("1.0.0"))
assert(q6.versions[0][1] == Version("2.0.0"))
assert(q6.variants['hi'] == True)

q7 = PackageQuery("hello@1.0.0:2.0.0 -hi")
assert(q7.name == "hello")
assert(q7.versions[0][0] == Version("1.0.0"))
assert(q7.versions[0][1] == Version("2.0.0"))
assert(q7.variants['hi'] == False)

q8 = PackageQuery("hello@1.0.0:2.0.0 hi=123")
assert(q8.name == "hello")
assert(q8.versions[0][0] == Version("1.0.0"))
assert(q8.versions[0][1] == Version("2.0.0"))
assert(q8.variants['hi'] == '123')

q9 = PackageQuery("hello@1.0.0:2.0.0 hi=123 % hello2@1.0.0:2.0.0 +hi2")
assert(q9.name == "hello")
assert(q9.versions[0][0] == Version("1.0.0"))
assert(q9.versions[0][1] == Version("2.0.0"))
assert(q9.variants['hi'] == '123')

q10 = q9.dependencies['hello2']
assert(q10.name == "hello2")
assert(q10.versions[0][0] == Version("1.0.0"))
assert(q10.versions[0][1] == Version("2.0.0"))
assert(q10.variants['hi2'] == True)
