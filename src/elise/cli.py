import argparse

from .Compiler import Compiler
from .config import ELISE_ENV


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='Directory to compile')
    parser.add_argument('-N', '--asm_name', default=ELISE_ENV['asm_name'], help='Output .asm filename')
    parser.add_argument('-O', '--org', type=int, default=ELISE_ENV['org'], help='Assembler ORG command')
    parser.add_argument('-S', '--stack', type=int, default=ELISE_ENV['stack'], help='Initial Stack Pointer address')
    parser.add_argument('-H', '--heap', type=int, default=ELISE_ENV['heap_start'], help='Start address of Heap')
    parser.add_argument('-HS', '--heap_size', type=int, default=ELISE_ENV['heap_size'], help='Size of Heap')
    parser.add_argument('-L', '--lib', default=ELISE_ENV['lib'], help='Path to Library folder')
    parser.add_argument('-B', '--build', default=ELISE_ENV['output'], help='Path to build output folder')
    parser.add_argument('-C', '--clean', type=bool, default=ELISE_ENV['clean'], help='Clean .vm file after compile')
    parser.add_argument('-DB', '--db', type=bool, default=ELISE_ENV['db'], help='Link Debug command')
    parser.add_argument('-VB', '--verbose', type=int, default=ELISE_ENV['verbose'], help='Message level')
    parser.add_argument('-A', '--assemble', action='store_true', help='Assemble generated .asm with zasm')
    parser.add_argument('--assembler', default=ELISE_ENV['assembler'], help='Assembler executable')
    parser.add_argument('--run', action='store_true', help='Run the assembled ROM in openMSX')
    parser.add_argument('--openmsx', default=ELISE_ENV['openmsx'], help='openMSX executable')
    parser.add_argument('--machine', default=ELISE_ENV['machine'], help='openMSX machine name')
    parser.add_argument(
        '--breakpoint',
        action='append',
        default=[],
        help='Function name for an openMSX breakpoint (repeatable)',
    )
    parser.add_argument(
        '-MD',
        '--media',
        type=str,
        default=ELISE_ENV['media'],
        choices=('msxpen', 'cartridge'),
        help='Output asm type. "msxpen" or "cartridge"',
    )
    parser.add_argument(
        '-CS',
        '--cartridge_size',
        type=int,
        default=ELISE_ENV['size'],
        help='Cartridge memory size.',
    )
    args = parser.parse_args()

    # Cartridge images require the ROM header and must start at 0x4000.
    # Keep explicit address overrides intact.
    org = args.org
    heap_size = args.heap_size
    if args.media == 'cartridge':
        if org == ELISE_ENV['org']:
            org = 0x4000
        if heap_size == ELISE_ENV['heap_size']:
            heap_size = 0x2000

    env = {
        'directory': args.directory,
        'asm_name': args.asm_name,
        'org': org,
        'stack': args.stack,
        'heap_start': args.heap,
        'heap_size': heap_size,
        'lib': args.lib,
        'output': args.build,
        'clean': args.clean,
        'db': args.db,
        'verbose': args.verbose,
        'assembler': args.assembler,
        'openmsx': args.openmsx,
        'machine': args.machine,
        'script': None,
        'media': args.media,
        'size': args.cartridge_size,
    }

    compiler = Compiler(env)
    asm_file = compiler.compile()
    if (args.assemble or args.run or args.breakpoint) and asm_file:
        result = compiler.assemble(asm_file)
        if result.stderr:
            print(result.stderr, end='')
        if not result.success:
            raise SystemExit(result.returncode or 1)
        print('assembled: %s' % result.output_file)
        print('listing: %s' % result.list_file)
        if args.breakpoint:
            try:
                env['script'] = compiler.debug_script(args.breakpoint)
            except ValueError as error:
                raise SystemExit(str(error))
            print('debug script: %s' % env['script'])
        if args.run:
            try:
                run_result = compiler.run(result.output_file)
            except FileNotFoundError as error:
                raise SystemExit(str(error))
            print('openMSX started (pid=%s)' % run_result.pid)
            print('emulator log: %s' % run_result.log_file)
