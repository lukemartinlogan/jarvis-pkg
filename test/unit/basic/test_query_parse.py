from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.query_parser.parse import QueryParser
from jarvis_pkg.basic.version import Version


def test1():
    q1 = QueryParser("a.b.hello").first()
    assert(q1.repo == "a")
    assert(q1.cls == "b")
    assert(q1.name == "hello")


def test2():
    q2 = QueryParser("a.b.hello@1.0.0").first()
    assert(q2.repo == "a")
    assert(q2.cls == "b")
    assert(q2.name == "hello")
    assert(q2.versions[0][0] == Version("1.0.0"))
    assert(q2.versions[0][1] == Version("1.0.0"))


def test3():
    q3 = QueryParser("a.b.hello@1.0.0:").first()
    assert(q3.repo == "a")
    assert(q3.cls == "b")
    assert(q3.name == "hello")
    assert(q3.versions[0][0] == Version("1.0.0"))
    assert(q3.versions[0][1] == Version("max"))


def test4():
    q4 = QueryParser("a.b.hello@:1.0.0").first()
    assert(q4.repo == "a")
    assert(q4.cls == "b")
    assert(q4.name == "hello")
    assert(q4.versions[0][0] == Version("min"))
    assert(q4.versions[0][1] == Version("1.0.0"))


def test5():
    q5 = QueryParser("a.b.hello@1.0.0:2.0.0").first()
    assert(q5.repo == "a")
    assert(q5.cls == "b")
    assert(q5.name == "hello")
    assert(q5.versions[0][0] == Version("1.0.0"))
    assert(q5.versions[0][1] == Version("2.0.0"))


def test6():
    q6 = QueryParser("a.b.hello@1.0.0:2.0.0 +hi").first()
    assert(q6.repo == "a")
    assert(q6.cls == "b")
    assert(q6.name == "hello")
    assert(q6.versions[0][0] == Version("1.0.0"))
    assert(q6.versions[0][1] == Version("2.0.0"))
    assert(q6.variants['hi'] == True)


def test7():
    q7 = QueryParser("a.b.hello@1.0.0:2.0.0 -hi").first()
    assert(q7.repo == "a")
    assert(q7.cls == "b")
    assert(q7.name == "hello")
    assert(q7.versions[0][0] == Version("1.0.0"))
    assert(q7.versions[0][1] == Version("2.0.0"))
    assert(q7.variants['hi'] == False)


def test8():
    q8 = QueryParser("a.b.hello@1.0.0:2.0.0 hi=123").first()
    assert(q8.repo == "a")
    assert(q8.cls == "b")
    assert(q8.name == "hello")
    assert(q8.versions[0][0] == Version("1.0.0"))
    assert(q8.versions[0][1] == Version("2.0.0"))
    assert(q8.variants['hi'] == '123')


def test9():
    q9 = QueryParser("a.b.hello@1.0.0:2.0.0 hi=123 % a.h2.hello2@1.0.0:2.0.0 +hi2").first()
    assert(q9.repo == "a")
    assert(q9.cls == "b")
    assert(q9.name == "hello")
    assert(q9.versions[0][0] == Version("1.0.0"))
    assert(q9.versions[0][1] == Version("2.0.0"))
    assert(q9.variants['hi'] == '123')

    q10 = q9.dependencies['h2']
    assert(q10.repo == "a")
    assert(q10.cls == "h2")
    assert(q10.name == "hello2")
    assert(q10.versions[0][0] == Version("1.0.0"))
    assert(q10.versions[0][1] == Version("2.0.0"))
    assert(q10.variants['hi2'] == True)

def test10():
    q = QueryParser("@1.0.2 +hi").first()
    assert(q.repo == None)
    assert(q.cls == None)
    assert(q.name == None)
    assert(q.versions[0][0] == Version("1.0.2"))
    assert(q.variants['hi'] == True)

def test11():
    failed = False
    try:
        q = QueryParser("hi=")
    except Exception as e:
        failed = True
    assert(failed)

# test1()
# test2()
# test3()
# test4()
# test5()
test6()
# test7()
# test8()
# test9()
# test10()
# test11()

