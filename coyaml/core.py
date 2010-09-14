from collections import OrderedDict

from .util import varname
from .load import Convert

class Option(object):
    has_argument = True
    def __init__(self, param, target):
        self.param = param
        self.target = target

    def __repr__(self):
        return '<{0} {1} {2}>'.format(self.__class__.__name__,
            self.param, self.target)

    @property
    def short(self):
        return not self.param.startswith('--')

    @property
    def char(self):
        return self.param[1] if self.short else None

    @property
    def name(self):
        return self.param[2:] if self.param else None

class IncrOption(Option):
    has_argument = False

class DecrOption(Option):
    has_argument = False

class Usertype(object):
    def __init__(self, name, members, **kw):
        self.name = name
        if '__tags__' in members:
            tags = members['__tags__']
            self.tagname = tags.get('__property__', 'tag')
            if '__default__' in tags:
                self.defaulttag = tags[tags['__default__']]
            self.tags = {k:v for k, v in tags.items()
                if not k.startswith('__')}
        self.members = {k:v for k, v in members.items()
            if not k.startswith('__')}
        if isinstance(members.get('__value__'), Convert):
            self.convert = members['__value__'].fun
        elif members.get('__value__'):
            self.convert = 'coyaml_tagged_scalar'
            self.members['value'] = members['__value__']
        for k, v in kw.items():
            setattr(self, k, v)

class ConfigMeta(object):
    def update(self, dic):
        for k, v in dic.items():
            setattr(self, varname(k), v)

class Config(object):
    def __init__(self, name, targetname):
        self.name = name
        self.targetname = targetname
        self.meta = ConfigMeta()
        self.types = OrderedDict()
        self.commandline = []

    def fill_meta(self, meta):
        self.meta.update(meta)

    def add_type(self, typ):
        assert not typ.name in self.types
        self.types[typ.name] = typ

    def fill_data(self, data):
        self.data = data
        self._visit_options(self.data)

    def _visit_options(self, data):
        for k, v in data.items():
            if isinstance(v, dict):
                self._visit_options(v)
                continue
            self._visit_option(v, 'command_line', Option)
            self._visit_option(v, 'command_line_incr', IncrOption)
            self._visit_option(v, 'command_line_decr', DecrOption)

    def _visit_option(self, ob, opt, cls):
        if hasattr(ob, opt):
            val = getattr(ob, opt)
            if not isinstance(val, (list, tuple)):
                val = (val,)
            for one in val:
                self.commandline.append(cls(one, ob))

    def print(self):
        import pprint
        pprint.pprint(self.meta.__dict__)
        pprint.pprint(self.types)
        pprint.pprint(self.data)
        pprint.pprint(self.commandline)
