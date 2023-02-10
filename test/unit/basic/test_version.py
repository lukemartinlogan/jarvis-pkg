from jarvis_pkg.basic.version import Version

v1 = Version("1.2.3")
assert(v1.vtuple[0] == 1)
assert(v1.vtuple[1] == 2)
assert(v1.vtuple[2] == 3)

v2 = Version("1.2")
assert(v2.vtuple[0] == 1)
assert(v2.vtuple[1] == 2)

assert(Version.is_version("1.2.3"))
assert(Version.is_version("1.2"))
assert(Version.is_version("1"))

assert(Version("1.2.3") > Version("1.2"))
assert(Version("1.2") < Version("1.2.3"))
assert(Version("1.2") == Version("1.2"))
assert(Version("1.2.3") == Version("1.2.3"))
assert(Version("1") > Version("min"))
assert(Version("1") < Version("max"))
