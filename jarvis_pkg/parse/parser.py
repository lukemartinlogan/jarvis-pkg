from jarvis_cd import *
import re

class ParseTree:
    def __init__(self, schema_path):
        self.schema = YAMLFile(schema_path).Load()
        self.aliases = {}
        self.lex_rules = {}
        self.parse_rules = {}
        self.search_rules = {}
        if 'ALIASES' in self.schema:
            self.aliases = self.schema['ALIASES']
        if 'LEX' in self.schema:
            self.lex_rules = self.schema['LEX']
        if 'PARSE' in self.schema:
            self.parse_rules = self.schema['PARSE']
        if 'SEARCH' in self.schema:
            self.search_rules = self.schema['SEARCH']

    @staticmethod
    def _string_rule_deps(rule):
        is_dep = '(\[[a-zA-Z0-9]+])'
        select_dep = '([a-zA-Z0-9])+'
        escaped_dep = '(\[\[[a-zA-Z0-9]+]])'
        builtin = {'all', 'any'}
        deps = re.split(f"{is_dep}|{escaped_dep}", rule)
        deps = [dep for dep in deps if dep is not None and len(dep)]
        deps = [dep for dep in deps if re.match(is_dep, dep) and not re.match(escaped_dep,dep)]
        deps = [re.search(select_dep,dep).group(0) for dep in deps]
        deps = [dep for dep in deps if dep not in builtin]
        return deps

    @staticmethod
    def _list_rule_deps(ruleset):
        deps = []
        for rule in ruleset:
            deps += ParseTree._rule_deps(rule)
        return deps

    @staticmethod
    def _dict_rule_deps(ruledict):
        deps = []
        if 'chars' in ruledict:
            rule = ruledict['chars']
        elif 'strs' in ruledict:
            rule = ruledict['strs']
        elif 'rep' in ruledict:
            rule = ruledict['rep']
        elif 'not' in ruledict:
            rule = ruledict['not']
        else:
            raise 1
        deps += ParseTree._rule_deps(rule)
        return deps

    @staticmethod
    def _rule_deps(rule):
        deps = []
        if isinstance(rule, str):
            deps += ParseTree._string_rule_deps(rule)
        if isinstance(rule, list):
            deps += ParseTree._list_rule_deps(rule)
        if isinstance(rule, dict):
            deps += ParseTree._dict_rule_deps(rule)
        return list(set(deps))

    def _to_re(self, regex_dict):
        pass

    def _find_def(self, dep_name, rule_stack):
        for ruleset in rule_stack.reverse():
            if dep_name in ruleset:
                return ruleset[dep_name]
        if dep_name in self.aliases:
            return self.aliases[dep_name]
        if dep_name in self.lex_rules:
            return self.lex_rules[dep_name]
        if dep_name in self.parse_rules:
            return self.parse_rules[dep_name]
        if dep_name in self.search_rules:
            return self.search_rules[dep_name]
        raise 1

    def _compile(self, ruleset, rule_stack=[{}]):
        for rule_name,rule_def in ruleset:
            if not isinstance(rule_def, dict) or 'match' not in rule_def:
                raise 1

            #Get all aliases that need to be compiled
            dep_names = self._rule_deps(rule_def['match'])

            #Compile all internal aliases
            for sub_rule_name, sub_rule_def in rule_def.items():
                if sub_rule_name == 'match':
                    continue
                rule_stack.append({})
                self._compile(sub_rule_def, rule_stack)

            #Compile all dependencies
            for dep_name in dep_names:
                dep_def = self._find_def(dep_name, rule_stack)
                if '_re' not in dep_def:
                    rule_stack.append({})
                    self._compile(dep_def, rule_stack)

            #Compile self

        """
        ALIASES:
            text:
                depends_on: nondigit,withdigit
                re: ([a-zA-Z_]{1,})([a-zA-Z0-9_]{0,})
                nondigit:
                    re: ([a-zA-Z_]{1,})
                withdigit:
                    re: ([a-zA-Z0-9_]{0,})
            spaces:


        LEX:
            tokens:
                depends_on: spaces,text\
        """
        pass

    def _preprocess(self):
        """
        Convert the parser schema into a series of regular expressions

        :return:
        """
        for rule_name,rule_def in self.schema['ALIASES'].items():
            self._preprocess_deps('ALIASES', rule_name, rule_def)
        return

    def lex(self, text):
        pass

    def parse(self, text):
        pass