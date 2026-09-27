import os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BUILD_DIR = os.path.join(PROJECT_ROOT, 'build')
LIB_DIR = os.path.join(PROJECT_ROOT, 'Lib')


ELISE_ENV = {
    'directory': None,
    'asm_name': None,
    'org': 0x8100,
    'stack': 0xDC60,
    'heap_start': 0x0000,
    'heap_size': 0x1000,
    'lib': LIB_DIR,
    'output': BUILD_DIR,
    'clean': False,
    'db': True,
    'verbose': 1,
    'assembler': 'zasm',
    'auto_link_libs': True,
    'openmsx': 'openmsx',
    'machine': None,
    'media': 'msxpen',
    'size': 0x4000,
}

ELISE_ENV_CARTRIDGE = dict(ELISE_ENV)
ELISE_ENV_CARTRIDGE.update({
    'org': 0x4000,
    'heap_size': 0x2000,
    'media': 'cartridge',
})
