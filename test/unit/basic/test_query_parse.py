from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.query_parser.parse import QueryParser
from jarvis_pkg.basic.version import Version


def assert_id(q, text):
    if text is not None:
        id = text.split('.')
        assert(q.repo == id[0])
        assert(q.cls == id[1])
        assert(q.name == id[2])
    else:
        assert (q.repo == None)
        assert (q.cls == None)
        assert (q.name == None)


def test1():
    q1 = QueryParser("a.b.hello").first()
    assert_id(q1, "a.b.hello")


def test2():
    q = QueryParser("a.b.hello@1.0.0").first()
    assert_id(q, "a.b.hello")
    assert(q.versions[0][0] == Version("1.0.0"))
    assert(q.versions[0][1] == Version("1.0.0"))


def test3():
    q = QueryParser("a.b.hello@1.0.0:").first()
    assert_id(q, "a.b.hello")
    assert(q.versions[0][0] == Version("1.0.0"))
    assert(q.versions[0][1] == Version("max"))


def test4():
    q = QueryParser("a.b.hello@:1.0.0").first()
    assert_id(q, "a.b.hello")
    assert(q.versions[0][0] == Version("min"))
    assert(q.versions[0][1] == Version("1.0.0"))


def test5():
    q = QueryParser("a.b.hello@1.0.0:2.0.0").first()
    assert_id(q, "a.b.hello")
    assert(q.versions[0][0] == Version("1.0.0"))
    assert(q.versions[0][1] == Version("2.0.0"))


def test6():
    q = QueryParser("a.b.hello@1.0.0:2.0.0 +hi").first()
    assert_id(q, "a.b.hello")
    assert(q.versions[0][0] == Version("1.0.0"))
    assert(q.versions[0][1] == Version("2.0.0"))
    assert(q.variants['hi'] == True)


def test7():
    q = QueryParser("a.b.hello@1.0.0:2.0.0 -hi").first()
    assert_id(q, "a.b.hello")
    assert(q.versions[0][0] == Version("1.0.0"))
    assert(q.versions[0][1] == Version("2.0.0"))
    assert(q.variants['hi'] == False)


def test8():
    q = QueryParser("a.b.hello@1.0.0:2.0.0 hi=123").first()
    assert_id(q, "a.b.hello")
    assert(q.versions[0][0] == Version("1.0.0"))
    assert(q.versions[0][1] == Version("2.0.0"))
    assert(q.variants['hi'] == '123')


def test9():
    q1 = QueryParser("a.b.hello@1.0.0:2.0.0 hi=123 % a.h2.hello2@1.0.0:2.0.0 +hi2").first()
    assert_id(q1, "a.b.hello")
    assert(q1.versions[0][0] == Version("1.0.0"))
    assert(q1.versions[0][1] == Version("2.0.0"))
    assert(q1.variants['hi'] == '123')

    q2 = q1.dependencies['h2']
    assert_id(q2, "a.h2.hello2")
    assert(q2.versions[0][0] == Version("1.0.0"))
    assert(q2.versions[0][1] == Version("2.0.0"))
    assert(q2.variants['hi2'] == True)


def test10():
    q = QueryParser("@1.0.2 +hi").first()
    assert_id(q, None)
    assert(q.versions[0][0] == Version("1.0.2"))
    assert(q.variants['hi'] == True)


def test11():
    q1 = QueryParser("a.b.c%c.d.e%f.g.h%i.j.k").first()
    assert_id(q1, "a.b.c")
    q2 = q1.dependencies['d']
    assert_id(q2, "c.d.e")
    q3 = q1.dependencies['g']
    assert_id(q3, "f.g.h")
    q4 = q1.dependencies['j']
    assert_id(q4, "i.j.k")


def test12():
    q1 = QueryParser("a.b.c%(c.d.e%f.g.h)%i.j.k").first()
    assert_id(q1, "a.b.c")
    q2 = q1.dependencies['d']
    assert_id(q2, "c.d.e")
    q3 = q2.dependencies['g']
    assert_id(q3, "f.g.h")
    q4 = q1.dependencies['j']
    assert_id(q4, "i.j.k")


def test13():
    q1 = QueryParser("a.b.c%(c.d.e@1.0.0:%f.g.h)%i.j.k").first()
    assert_id(q1, "a.b.c")
    q2 = q1.dependencies['d']
    assert_id(q2, "c.d.e")
    assert(q2.versions[0][0] == Version("1.0.0"))
    assert(q2.versions[0][1] == Version("max"))
    q3 = q2.dependencies['g']
    assert_id(q3, "f.g.h")
    q4 = q1.dependencies['j']
    assert_id(q4, "i.j.k")


def test14():
    failed = False
    try:
        q = QueryParser("hi=")
    except Exception as e:
        failed = True
    assert(failed)

test1()
test2()
test3()
test4()
test5()
test6()
test7()
test8()
test9()
test10()
test11()
test12()
test13()
test14()
