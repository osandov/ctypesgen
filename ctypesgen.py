#!/usr/bin/env python3
import argparse
import ctypes
import clang.cindex
from clang.cindex import CursorKind, StorageClass, TypeKind
import distutils.spawn
import os.path
import re
import sys


anon_structs = {}
anon_unions = {}
anon_enums = {}
declared = set()


def main():
    global args
    global lib

    parser = argparse.ArgumentParser(description='Generate ctypes bindings by parsing C headers')
    parser.add_argument('--library', metavar='LIBRARY', help='shared library file (e.g., libc.so.6)', 
        type=str)
    parser.add_argument('--headers', metavar='HEADER', nargs='+', help='headers to parse')
    parser.add_argument('--clang-path', metavar='PATH', help='path to clang executable')
    parser.add_argument(
        '--clang-flags', metavar='FLAGS',
        help='extra flags to pass to clang (e.g., -I)', nargs="*", default=[])
    parser.add_argument(
        '--ignore-included', action='store_true',
        help="don't generate bindings for declarations in included files")
    parser.add_argument('--std', choices=('c89', 'c99', 'c11'), default='c11')
    args = parser.parse_args()

    if not args.clang_path:
        args.clang_path = distutils.spawn.find_executable('clang')
    args.clang_path = os.path.abspath(args.clang_path)
    clang_prefix = os.path.dirname(os.path.dirname(args.clang_path))

    clang.cindex.Config.set_library_path(os.path.join(clang_prefix, 'lib'))
    index = clang.cindex.Index.create()

    # We need to find the internal clang header files, which live in
    # $PREFIX/lib/clang/$VERSION/include. This is gross and fragile but I can't
    # think of a better way to do it.
    clang.cindex.conf.lib.clang_getClangVersion.restype = ctypes.c_char_p
    version_string = clang.cindex.conf.lib.clang_getClangVersion()
    if type(version_string) == type(b''):
        version_string = version_string.decode("utf-8")
    match = re.search(r'\d+(\.\d+)+', version_string)
    assert match
    version = match.group(0)

    internal_includes = '%s/lib/clang/%s/include' % (clang_prefix, version)

    print("import ctypes")
    print()
    lib = os.path.basename(args.library).split('.', 1)[0]
    print("%s = ctypes.CDLL('%s')" % (lib, args.library))

    args.headers = [os.path.abspath(header) for header in args.headers]
    unsaved_file = '\n'.join('#include "%s"' % header for header in args.headers)

    clang_args = ['-x', 'c', '-std=%s' % args.std, '-I', internal_includes]
    if args.clang_flags:
        for flag in args.clang_flags:
            if not " " in flag:
                flag = flag.replace("\"", "")
            clang_args.append(flag)
    translation_unit = index.parse(
        'unsaved', args=clang_args, unsaved_files=[('unsaved', unsaved_file)])

    have_error = False
    for diag in translation_unit.diagnostics:
        if diag.severity > clang.cindex.Diagnostic.Warning:
            # libclang has clang_formatDiagnostic(), but it's not exposed
            # in the Python bindings.
            print(diag, file=sys.stderr)
            have_error = True
    if not have_error:
        walk(translation_unit.cursor)


class Function(object):
    def __init__(self, location, name, return_type, params, has_proto, is_variadic):
        self.location = location
        self.name = name
        self.return_type = return_type
        self.params = params
        self.has_proto = has_proto
        self.is_variadic = is_variadic

    def print(self):
        print("%s.%s.restype = %s" % (lib, self.name, clang_type_to_ctype(self.return_type)))
        argtypes = [clang_type_to_ctype(param.type) for param in self.params]
        if self.has_proto and not self.is_variadic:
            print("%s.%s.argtypes = [%s]" % (lib, self.name, ', '.join(argtypes)))


class Param(object):
    def __init__(self, type):
        self.type = type


class StructOrUnion(object):
    def __init__(self, location, name, fields, is_union, is_definition, anon_num=None):
        self.location = location
        self.name = name
        self.fields = fields
        self.is_union = is_union
        self.is_definition = is_definition
        self.anon_num = anon_num

        if self.is_union:
            if self.name:
                self.class_name = 'union_%s' % self.name
            else:
                self.class_name = '__anon_union%d' % self.anon_num
        else:
            if self.name:
                self.class_name = 'struct_%s' % self.name
            else:
                self.class_name = '__anon_struct%d' % self.anon_num

    def print(self):
        self.print_declaration()
        self.print_definition()

    def print_declaration(self):
        type = 'Union' if self.is_union else 'Structure'
        print()
        print("class %s(ctypes.%s):" % (self.class_name, type))
        print("    pass")

    def print_definition(self):
        if self.fields:
            print("%s._fields_ = [" % self.class_name)
            for field in self.fields:
                ctype = clang_type_to_ctype(field.type)
                if field.width is None:
                    print("    ('%s', %s)," % (field.name, ctype))
                else:
                    print("    ('%s', %s, %s)," % (field.name, ctype, field.width))
            print("]")


class Field(object):
    def __init__(self, name, type, width):
        self.name = name
        self.type = type
        self.width = width


class Typedef(object):
    def __init__(self, location, name, type):
        self.location = location
        self.name = name
        self.type = type

    def print(self):
        print("typedef_%s = %s" % (self.name, clang_type_to_ctype(self.type)))


class Enum(object):
    def __init__(self, location, name, enum_type, constants, anon_num=None):
        self.location = location
        self.name = name
        self.enum_type = enum_type
        self.constants = constants
        self.anon_num = anon_num

    def print(self):
        if self.name:
            print("enum_%s = %s" % (self.name, clang_type_to_ctype(self.enum_type)))
        else:
            print("__anon_enum%d = %s" % (self.anon_num, clang_type_to_ctype(self.enum_type)))
        for constant in self.constants:
            print("enum_constant_%s = %d" % (constant.name, constant.value))


class EnumConstant(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Var(object):
    def __init__(self, location, name, type):
        self.location = location
        self.name = name
        self.type = type

    def print(self):
        ctype = clang_type_to_ctype(self.type)
        print("var_%s = %s.in_dll(%s, '%s')" % (self.name, ctype, lib, self.name))


def isValidSpelling(spelling):
    # If the spleeing is none or has spaces it isn't valid
    return spelling and ' ' not in spelling

def walk(node):
    print_decl(StructOrUnion(None, '__va_list_tag', [], False, False))

    if node.kind == CursorKind.TRANSLATION_UNIT:
        for c in node.get_children():
            top = walk(c)
            if top and hasattr(top, 'print'):
                print_decl(top)
    elif node.kind == CursorKind.FUNCTION_DECL:
        params = []
        for c in node.get_arguments():
            if c.kind == CursorKind.PARM_DECL:
                params.append(walk(c))
        if node.type.kind == TypeKind.FUNCTIONPROTO:
            has_proto = True
            is_variadic = node.type.is_function_variadic()
        else:
            has_proto = False
            is_variadic = None
        if node.storage_class != StorageClass.STATIC:
            return Function(node.location, node.spelling, node.result_type,
                            params, has_proto, is_variadic)
    elif node.kind == CursorKind.PARM_DECL:
        return Param(node.type)
    elif node.kind in [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]:
        fields = []
        for c in node.get_children():
            if c.kind == CursorKind.FIELD_DECL:
                fields.append(walk(c))
        is_union = node.kind == CursorKind.UNION_DECL
        is_definition = node.is_definition()
        if isValidSpelling(node.spelling):
            return StructOrUnion(node.location, node.spelling, fields, is_union, is_definition)
        else:
            anon_records = anon_unions if is_union else anon_structs
            record = StructOrUnion(node.location, None, fields, is_union,
                                   is_definition, len(anon_records) + 1)
            anon_records[node.hash] = record
            return record
    elif node.kind == CursorKind.FIELD_DECL:
        for c in node.get_children():
            top = walk(c)
            if top and hasattr(top, 'print'):
                print_decl(top)
        width = node.get_bitfield_width() if node.is_bitfield() else None
        return Field(node.spelling, node.type, width)
    elif node.kind == CursorKind.ENUM_DECL:
        constants = []
        for c in node.get_children():
            if c.kind == CursorKind.ENUM_CONSTANT_DECL:
                constants.append(walk(c))
        if isValidSpelling(node.spelling):
            return Enum(node.location, node.spelling, node.enum_type, constants)
        else:
            enum = Enum(node.location, None, node.enum_type, constants, len(anon_enums) + 1)
            anon_enums[node.hash] = enum
            return enum
    elif node.kind == CursorKind.ENUM_CONSTANT_DECL:
        return EnumConstant(node.spelling, node.enum_value)
    elif node.kind == CursorKind.TYPEDEF_DECL:
        if node.spelling not in SPECIAL_TYPEDEFS:
            return Typedef(node.location, node.spelling, node.underlying_typedef_type)
    elif node.kind == CursorKind.VAR_DECL:
        return Var(node.location, node.spelling, node.type)


def print_decl(decl):
    if not decl.location or decl.location.file.name not in args.headers:
        if isinstance(decl, Function) or isinstance(decl, Var) or args.ignore_included:
            return

    if isinstance(decl, StructOrUnion):
        printed = False
        if decl.class_name not in declared:
            print()
            printed = True
            decl.print_declaration()
        if decl.is_definition:
            if not printed:
                print()
            decl.print_definition()
        declared.add(decl.class_name)
    else:
        print()
        decl.print()


SPECIAL_TYPEDEFS = {
    'int8_t': 'ctypes.c_int8',
    'int16_t': 'ctypes.c_int16',
    'int32_t': 'ctypes.c_int32',
    'int64_t': 'ctypes.c_int64',
    'uint8_t': 'ctypes.c_uint8',
    'uint16_t': 'ctypes.c_uint16',
    'uint32_t': 'ctypes.c_uint32',
    'uint64_t': 'ctypes.c_uint64',
    'size_t': 'ctypes.c_size_t',
    'ssize_t': 'ctypes.c_ssize_t',
    'wchar_t': 'ctypes.c_wchar',
    'ptrdiff_t': 'ctypes.c_void_p',
    'uintptr_t': 'ctypes.c_void_p',
    # It's not nice to be so intimate with the va_list internals, but oh
    # well, you do what you have to.
    'va_list': 'ctypes.POINTER(struct___va_list_tag)',
    '__builtin_va_list': 'ctypes.POINTER(struct___va_list_tag)',
}


def clang_type_to_ctype(type):
    if type.kind == TypeKind.BOOL:
        return 'ctypes.c_bool'
    elif type.kind == TypeKind.CHAR_S:
        return 'ctypes.c_char'
    elif type.kind == TypeKind.CHAR_U:
        return 'ctypes.c_char'
    elif type.kind == TypeKind.CONSTANTARRAY or type.kind == TypeKind.COMPLEX:
        # Until ctypes supports complex numbers natively, treat them as an
        # array with two elements, which is guaranteed to be valid by the
        # standard.
        element_count = type.element_count if type.kind == TypeKind.CONSTANTARRAY else 2
        return '(%s * %d)' % (clang_type_to_ctype(type.element_type), element_count)
    elif type.kind == TypeKind.DOUBLE:
        return 'ctypes.c_double'
    elif type.kind == TypeKind.ENUM:
        decl = type.get_declaration()
        if decl.spelling:
            return 'enum_%s' % decl.spelling
        else:
            return '__anon_enum%d' % anon_enums[decl.hash].anon_num
    elif type.kind == TypeKind.FLOAT:
        return 'ctypes.c_float'
    elif type.kind == TypeKind.FUNCTIONPROTO or type.kind == TypeKind.FUNCTIONNOPROTO:
        ctypes = [clang_type_to_ctype(type.get_result())]
        if type.kind == TypeKind.FUNCTIONPROTO:
            # For FUNCTIONNOPROTO, the best we can do is assume there are no
            # arguments.
            ctypes.extend(clang_type_to_ctype(t) for t in type.argument_types())
        return 'ctypes.CFUNCTYPE(%s)' % ', '.join(ctypes)
    elif type.kind == TypeKind.INT:
        return 'ctypes.c_int'
    elif type.kind == TypeKind.INT128 or type.kind == TypeKind.UINT128:
        # Just treat an int128 as a bag of bytes.
        return '(ctypes.c_ubyte * 16)'
    elif type.kind == TypeKind.LONG:
        return 'ctypes.c_long'
    elif type.kind == TypeKind.LONGDOUBLE:
        return 'ctypes.c_longdouble'
    elif type.kind == TypeKind.LONGLONG:
        return 'ctypes.c_longlong'
    elif type.kind == TypeKind.POINTER or type.kind == TypeKind.INCOMPLETEARRAY:
        type2 = type.get_pointee() if type.kind == TypeKind.POINTER else type.element_type
        if type2.kind == TypeKind.UNEXPOSED:
            type2 = type2.get_canonical()
        if type2.kind == TypeKind.CHAR_S or type2.kind == TypeKind.CHAR_U:
            return 'ctypes.c_char_p'
        elif type2.kind == TypeKind.TYPEDEF and type2.get_declaration().spelling == 'wchar_t':
            return 'ctypes.c_wchar_p'
        elif type2.kind == TypeKind.VOID:
            return 'ctypes.c_void_p'
        elif type2.kind in [TypeKind.FUNCTIONPROTO, TypeKind.FUNCTIONNOPROTO]:
            return clang_type_to_ctype(type2)
        else:
            return 'ctypes.POINTER(%s)' % clang_type_to_ctype(type2)
    elif type.kind == TypeKind.RECORD:
        decl = type.get_declaration()
        if decl.kind == CursorKind.STRUCT_DECL:
            kind = 'struct'
            anon_records = anon_structs
        elif decl.kind == CursorKind.UNION_DECL:
            kind = 'union'
            anon_records = anon_unions
        else:
            assert False, decl.kind
        if isValidSpelling(decl.spelling):
            return '%s_%s' % (kind, decl.spelling)
        else:
            return '__anon_%s%d' % (kind, anon_records[decl.hash].anon_num)
    elif type.kind == TypeKind.SCHAR:
        return 'ctypes.c_byte'
    elif type.kind == TypeKind.SHORT:
        return 'ctypes.c_short'
    elif type.kind == TypeKind.TYPEDEF:
        decl = type.get_declaration()
        try:
            return SPECIAL_TYPEDEFS[decl.spelling]
        except KeyError:
            return 'typedef_%s' % decl.spelling
    elif type.kind == TypeKind.UCHAR:
        return 'ctypes.c_ubyte'
    elif type.kind == TypeKind.UINT:
        return 'ctypes.c_uint'
    elif type.kind == TypeKind.ULONG:
        return 'ctypes.c_ulong'
    elif type.kind == TypeKind.ULONGLONG:
        return 'ctypes.c_ulonglong'
    elif type.kind == TypeKind.UNEXPOSED:
        return clang_type_to_ctype(type.get_canonical())
    elif type.kind == TypeKind.USHORT:
        return 'ctypes.c_ushort'
    elif type.kind == TypeKind.VOID:
        return 'None'
    elif type.kind == TypeKind.ELABORATED:
        return clang_type_to_ctype(type.get_named_type())
    else:
        assert False, type.kind


if __name__ == '__main__':
    main()
