
from jarvis_pkg.util.argparse import ArgParse
from enum import Enum


class ArgOpts(Enum):
    CHOICE1 = "CHOICE1"
    CHOICE2 = "CHOICE2"


class Args1(ArgParse):
    def define_options(self):
        self.add_menu()
        self.start_required()
        self.add_arg("arg1",
                     argtype=int,
                     default=0,
                     msg="First argument")
        self.end_required()
        self.add_arg("arg2")
        self.add_arg("arg3",
                     msg="Third argument")

        self.add_menu("repo/add", use_remainder=True)
        self.start_required()
        self.add_arg("arg1", msg="Repo first")
        self.end_required()
        self.add_arg("arg2", msg="Repo second")
        self.add_arg("--bool",
                     argtype=bool,
                     default=True,
                     msg="test bool")
        self.add_arg("--test-choices",
                     argtype=ArgOpts,
                     choices=ArgOpts,
                     msg="enum test")


def test1():
    """
    Test positional arguments (required + optional)

    :return:
    """
    args = Args1("25 hello", exit_on_fail=False)
    assert(args.arg1 == 25)
    assert(args.arg2 == 'hello')


def test2():
    """
    Test help message on error

    :return:
    """
    failed = False
    try:
        args = Args1("", exit_on_fail=False)
    except:
        failed = True
    assert(failed)


def test3():
    """
    Test nondefault menus with required + optional positional args

    :return:
    """
    args = Args1("repo add 25 hello", exit_on_fail=False)
    assert(args.arg1 == '25')
    assert(args.arg2 == 'hello')


def test4():
    """
    Test nondefault menu help

    :return:
    """
    args = Args1("repo add 25 hello -h", exit_on_fail=False)
    assert(args.arg1 == '25')
    assert(args.arg2 == 'hello')


def test5():
    """
    Test nondefault menu kwarg choices

    :return:
    """
    args = Args1("repo add 25 hello --test-choices CHOICE1",
                 exit_on_fail=False)
    assert(args.arg1 == '25')
    assert(args.arg2 == 'hello')
    assert(args.test_choices == ArgOpts.CHOICE1)


def test6():
    """
    Test boolean choices

    :return:
    """
    args = Args1("repo add 25 hello --with-bool --test-choices CHOICE1",
                 exit_on_fail=False)
    assert (args.arg1 == '25')
    assert (args.arg2 == 'hello')
    assert (args.test_choices == ArgOpts.CHOICE1)
    assert (args.bool == True)


def test7():
    """
    Test boolean choices

    :return:
    """
    args = Args1("repo add 25 hello --with-bool "
                 "--test-choices CHOICE1 "
                 "--no-bool",
                 exit_on_fail=False)
    assert (args.arg1 == '25')
    assert (args.arg2 == 'hello')
    assert (args.test_choices == ArgOpts.CHOICE1)
    assert (args.bool == False)


test1()
test2()
test3()
test4()
test5()
test6()
test7()

