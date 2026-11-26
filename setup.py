from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):
    def build_extensions(self):
        # Triangle's exact-arithmetic predicates need unfused floating
        # point. GCC (aarch64) and clang contract a*b+c into FMA by
        # default, which breaks them and can hang mergehulls().
        if self.compiler.compiler_type != 'msvc':
            for ext in self.extensions:
                ext.extra_compile_args.append('-ffp-contract=off')
        super().build_extensions()


define_macros = [
    ('VOID', 'void'),
    ('REAL', 'double'),
    ('NO_TIMER', 1),
    ('TRILIBRARY', 1),
    ('ANSI_DECLARATORS', 1),
]

ext_modules = [
    Extension(
        'triangle.core',
        ['c/triangle.c', 'triangle/core.c'],
        include_dirs=['c'],
        define_macros=define_macros,
        # extra_compile_args=['-g'],
    ),
]

# see pyproject.toml for other metadata
setup(
    name='triangle',
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext},
)
