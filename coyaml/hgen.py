
from . import load
from .cutil import varname, typename, string_types, makevar
from .cast import *
from .textast import VSpace

class GenHCode(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.prefix = self.cfg.name
        self._visited = set()

    def make(self, ast):
        ast(CommentBlock(
            'THIS IS AUTOGENERATED FILE',
            'DO NOT EDIT!!!',
            ))
        ast(Ifndef('_H_'+self.cfg.targetname.upper()))
        ast(Define('_H_'+self.cfg.targetname.upper()))
        ast(StdInclude('coyaml_hdr.h'))
        for i in getattr(self.cfg.meta, 'c_std_include', []):
            ast(StdInclude(i))
        for i in getattr(self.cfg.meta, 'c_include', []):
            ast(Include(i))
        ast(VSpace())
        for sname, struct in self.cfg.types.items():
            if hasattr(struct, 'tags'):
                tagtyp = self.prefix+'_'+sname+'_tag_t'
                with ast(TypeDef(Enum(ast.block()), tagtyp)) as enum:
                    for k, v in struct.tags.items():
                        enum(EnumVal(self.prefix.upper()+'_'+makevar(k), v))
                ast(VSpace())
            cname = self.prefix+'_'+sname
            with ast(TypeDef(Struct(cname+'_s', ast.block()),
                cname+'_t')) as s:
                if hasattr(struct, 'tags'):
                    s(Var(tagtyp, struct.tagname))
                self._struct_body(s, struct.members, root=ast)
            ast(VSpace())
        with ast(TypeDef(Struct(self.prefix+'_main_s', ast.block()),
            self.prefix+'_main_t')) as ms:
            ms(Var('coyaml_head_t', 'head'))
            self._struct_body(ms, self.cfg.data, root=ast)
        ast(VSpace())
        ast(Var(Typename('coyaml_cmdline_t'), self.prefix+'_cmdline'))
        ast(Func(Typename(self.prefix+'_main_t *'), self.prefix+'_init', [
            Param(Typename(self.prefix+'_main_t *'), 'target'),
            ]))
        ast(Func(Typename('coyaml_context_t *'), self.prefix+'_context', [
            Param(Typename('coyaml_context_t *'), 'ctx'),
            Param(Typename(self.prefix+'_main_t *'), 'target'),
            ]))
        ast(Func(Void(), self.prefix+'_free', [
            Param(Typename(self.prefix+'_main_t *'), 'target'),
            ]))
        ast(Func(Typename(self.prefix+'_main_t *'), self.prefix+'_load', [
            Param(Typename(self.prefix+'_main_t *'), 'target'),
            Param(Typename('int'), 'argc'),
            Param(Typename('char **'), 'argv'),
            ]))
        ast(Endif('_H_'+self.cfg.targetname.upper()))

    def _simple_type(self, ast, typ, name):
        if isinstance(typ, load.Struct):
            ast(Var(Typename(self.prefix+'_'+typ.type+'_t'), varname(name)))
        elif isinstance(typ, string_types):
            ast(Var(Typename('char *'), varname(name)))
            ast(Var(Typename('size_t'), varname(name)+'_len'))
        else:
            ast(Var(Typename(typename(typ)), varname(name)))

    def _struct_body(self, ast, dic, root):
        for k, v in dic.items():
            if isinstance(v, dict):
                with ast(Var(AnonStruct(ast.block()), varname(k))) as ss:
                    self._struct_body(ss, v, root=root)
            elif isinstance(v, load.Mapping):
                tname = '{0}_m_{1}_{2}'.format(self.prefix,
                    typename(v.key_element), typename(v.value_element))
                ast(Var(Typename('struct '+tname+'_s *'), varname(k)))
                ast(Var('size_t', varname(k)+'_len'))
                if tname in self._visited:
                    continue
                self._visited.add(tname)
                root(VSpace())
                with root(TypeDef(Struct(tname+'_s', ast.block()),
                    tname+'_t')) as sub:
                    sub(Var(Typename('coyaml_mappingel_head_t'), 'head'))
                    self._simple_type(sub, v.key_element, 'key')
                    self._simple_type(sub, v.value_element, 'value')
                root(Macro(tname.replace('_m_', '_').upper()+'_LOOP',
                    [Ident('name'), Ident('source')],
                    'for({0}_t *name = source; name; name = name->head.next)'
                    .format(tname)))
            elif isinstance(v, load.Array):
                tname = '{0}_a_{1}'.format(self.prefix,
                    typename(v.element))
                ast(Var(Typename('struct '+tname+'_s *'), varname(k)))
                ast(Var('size_t', varname(k)+'_len'))
                if tname in self._visited:
                    continue
                self._visited.add(tname)
                root(VSpace())
                with root(TypeDef(Struct(tname+'_s', ast.block()),
                    tname+'_t')) as sub:
                    sub(Var(Typename('coyaml_arrayel_head_t'), 'head'))
                    self._simple_type(sub, v.element, 'value')
                root(Macro(tname.replace('_a_', '_').upper()+'_LOOP',
                    [Ident('name'), Ident('source')],
                    'for({0}_t *name = source; name; name = name->head.next)'
                    .format(tname)))
            else:
                self._simple_type(ast, v, k)

def main():
    from .cli import simple
    from .load import load
    from .textast import Ast
    cfg, inp, opt = simple()
    with inp:
        load(inp, cfg)
    with Ast() as ast:
        GenHCode(cfg).make(ast)
    print(str(ast))

if __name__ == '__main__':
    from .hgen import main
    main()
