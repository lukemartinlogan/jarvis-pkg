import sys
import os
from abc import ABC, abstractmethod
import shlex
from tabulate import tabulate


class ArgParse(ABC):
    def __init__(self, args=None):
        if args is None:
            args = sys.argv[1:]

        args = " ".join(args[1:])
        self.binary_name = os.path.basename(sys.argv[0])
        self.args = shlex.split(args)
        self.error = None
        self.menus = []
        self.vars = {}
        self.pos_required = True
        self.use_remainder = False

        self.menu = None
        self.define_options()
        self.menus.sort(key=lambda x: len(x['name']), reverse=True)
        self._parse()

    @abstractmethod
    def define_options(self):
        pass

    def add_menu(self, name=None, msg=None,
                 use_remainder=False):
        toks = []
        if name is not None:
            toks = name.split('/')
        self.menus.append({
            'name_str': " ".join(toks),
            'name': toks,
            'msg': msg,
            'num_required': 0,
            'pos_opts': [],
            'kw_opts': {},
            'use_remainder': use_remainder
        })
        self.pos_required = True

    def start_required(self):
        self.pos_required = True

    def end_required(self):
        self.pos_required = False

    def add_arg(self,
                name,
                argtype=None,
                choices=None,
                default=None,
                msg=None,
                action=None,
                aliases=None):
        menu = self.menus[-1]
        arg = {
            'name': name,
            'dict_name': self._get_opt_name(name),
            'type': argtype,
            'choices': choices,
            'default': default,
            'action': action,
            'msg': msg,
            'required': self.pos_required
        }
        if aliases is not None:
            for alias in aliases:
                if '-' in alias:
                    self.add_arg(alias, argtype, choices, default, msg)
                else:
                    raise f"Can't have a non-keyword alias: {alias}"
        if '-' in name:
            self.pos_required = False
            menu['kw_opts'][name] = arg
        else:
            if self.pos_required:
                menu['num_required'] += 1
            menu['pos_opts'].append(arg)

    def _parse(self):
        self._parse_menu()

    def _parse_menu(self):
        self.menu = None
        for menu in self.menus:
            menu_name = menu['name']
            if len(menu_name) > len(self.args):
                continue
            if menu_name == self.args[0:len(menu_name)]:
                self.menu = menu
                break
        if self.menu is None:
            self._invalid_menu()
        self.add_arg('-h',
                     default=True,
                     msg='print help message',
                     action=self._print_help,
                     aliases=['--help'])
        menu_name = self.menu['name']
        self.use_remainder = self.menu['use_remainder']
        self._parse_args(self.args[len(menu_name):])

    def _parse_args(self, args):
        self._set_defaults()
        i = self._parse_pos_args(args)
        self._parse_kw_args(args, i)

    def _set_defaults(self):
        all_opts = self.menu['pos_opts'] + list(self.menu['kw_opts'].values())
        for opt_info in all_opts:
            if opt_info['default'] is None:
                continue
            self.__dict__[opt_info['dict_name']] = opt_info['default']

    def _parse_pos_args(self, args):
        i = 0
        menu = self.menu
        while i < len(menu['pos_opts']):
            # Get the positional arg info
            opt_name = menu['pos_opts'][i]['name']
            opt_dict_name = menu['pos_opts'][i]['dict_name']
            opt_type = menu['pos_opts'][i]['type']
            if i >= len(args) and i < menu['num_required']:
                self._missing_positional(opt_name)

            # Get the arg value
            arg = args[i]
            if arg in menu['kw_opts']:
                break
            if opt_type is not None:
                try:
                    arg = opt_type(arg)
                except:
                    self._invalid_type(opt_name, opt_type)

            # Set the argument
            self.__dict__[opt_dict_name] = arg
            i += 1
        return i

    def _parse_kw_args(self, args, i):
        menu = self.menu
        while i < len(args):
            # Get argument name
            opt_name = args[i]
            if opt_name not in menu['kw_opts']:
                if self.use_remainder:
                    self.remainder = " ".join(args[i:])
                else:
                    self._invalid_kwarg(opt_name)

            # Get argument type
            opt_dict_name = menu['kw_opts'][opt_name]['dict_name']
            opt_type = menu['kw_opts'][opt_name]['type']
            opt_default = menu['kw_opts'][opt_name]['default']
            opt_action = menu['kw_opts'][opt_name]['action']
            if self._next_is_kw_value(i):
                arg = self.args[i + 1]
                i += 2
            elif opt_default is not None:
                arg = opt_default
                i += 1
            elif opt_action is not None:
                opt_action()
                arg = None
                i += 1
            else:
                arg = None
                self._invalid_kwarg_default(opt_name)

            # Convert argument to type
            if opt_type is not None:
                try:
                    arg = opt_type(arg)
                except:
                    self._invalid_type(opt_name, opt_type)

            # Set the argument
            self.__dict__[opt_dict_name] = arg

    def _next_is_kw_value(self, i):
        if i + 1 >= len(self.args):
            return False
        return self.args[i + 1] not in self.menu['kw_opts']

    def _get_opt_name(self, opt_name):
        return opt_name.strip('-').replace('-', '_')

    def _invalid_menu(self):
        self._print_error(f"Could not find a menu")

    def _missing_positional(self, opt_name):
        self._print_menu_error(f"{opt_name} was required, but not defined")

    def _invalid_kwarg(self, opt_name):
        self._print_menu_error(f"{opt_name} is not a valid key-word argument")

    def _invalid_kwarg_default(self, opt_name):
        self._print_menu_error(f"{opt_name} was not given a value, but requires one")

    def _invalid_type(self, opt_name, opt_type):
        self._print_menu_error(f"{opt_name} was not of type {opt_type}")

    def _print_menu_error(self, msg):
        self._print_error(f"{self.menu['name_str']} {msg}")

    def _print_error(self, msg):
        print(f"{msg}")
        self._print_help()
        exit(1)

    def _print_help(self):
        if self.menu is not None:
            self._print_menu_help()
        else:
            self._print_menus()

    def _print_menus(self):
        for menu in self.menus:
            self.menu = menu
            self._print_menu_help(True)

    def _print_menu_help(self, only_usage=False):
        print(self.menu['msg'])
        print()
        pos_args = []
        for arg in self.menu['pos_opts']:
            if arg['required']:
                pos_args.append(f"[{arg}]")
            else:
                pos_args.append(f"[{arg} (opt)]")
        pos_args = " ".join(pos_args)
        menu_str = self.menu['name_str']
        print(f"USAGE: {self.binary_name} {menu_str} {pos_args} ...")
        if only_usage:
            return

        headers = ['Name', 'Default', 'Type', 'Description']
        table = []
        all_opts = self.menu['pos_opts'] + list(self.menu['kw_opts'].values())
        for arg in all_opts:
            table.append(
                [arg['name'], arg['default'], arg['type'], arg['msg']])
        print(tabulate(table, headers=headers))
