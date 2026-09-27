import json
import os
import re


SUBROUTINE_PATTERN = re.compile(
    r'^\s*(constructor|function|method)\s+\S+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\('
)
CLASS_PATTERN = re.compile(r'^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\b')
VM_FUNCTION_PATTERN = re.compile(r'^\s*function\s+(\S+)\s+(\d+)\s*$')
ASM_LABEL_PATTERN = re.compile(r'^([A-Za-z_][A-Za-z0-9_.$]*):')
VM_SOURCE_PATTERN = re.compile(r'^\s*//\s*source\s+(\d+)\s+(\S+)')
ASM_SOURCE_PATTERN = re.compile(r'^\s*;\s*source\s+(\d+)\s+(\S+)\s+(\d+)\s*$')
LISTING_ADDRESS_PATTERN = re.compile(r'^\s*([0-9A-Fa-f]{4,6}):')
LISTING_LABEL_PATTERN = re.compile(
    r'^\s*([0-9A-Fa-f]{4,6}):\s+(?:\S+\s+)?([A-Za-z_][A-Za-z0-9_.$]*):'
)
RUNTIME_LABELS = {
    'heap',
    'sys_SP',
    'sys_LOCAL',
    'sys_ARGUMENT',
    'sys_POINTER',
    'sys_THIS',
    'sys_THAT',
    'sys_TEMP',
    'mem_free_list',
}


class DebugMetadataWriter:
    def __init__(self, project_root=None):
        self.project_root = project_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        )

    def write(self, asm_file, source_files, vm_files, output_file=None):
        if output_file is None:
            output_file = os.path.splitext(asm_file)[0] + '.symbols.json'

        functions = {}
        self.labels = {}
        for source_file in source_files:
            self._read_source(source_file, functions)

        for vm_file in vm_files:
            self._read_vm(vm_file, functions)

        self._read_asm(asm_file, functions)
        metadata = {
            'version': 1,
            'program': os.path.splitext(os.path.basename(asm_file))[0],
            'assembly': self._relative_path(asm_file),
            'functions': functions,
            'labels': self.labels,
        }
        with open(output_file, 'w') as file:
            json.dump(metadata, file, indent=2, ensure_ascii=False)
            file.write('\n')
        return output_file

    def attach_listing(self, metadata_file, listing_file):
        with open(metadata_file) as file:
            metadata = json.load(file)

        functions = metadata.get('functions', {})
        labels = metadata.setdefault('labels', {})
        pending_source = None
        with open(listing_file) as file:
            for line_number, line in enumerate(file, start=1):
                source_match = ASM_SOURCE_PATTERN.match(line)
                if source_match:
                    source_line, function, vm_line = source_match.groups()
                    pending_source = {
                        'source_line': int(source_line),
                        'function': function,
                        'vm_line': int(vm_line),
                    }
                    continue

                address_match = LISTING_ADDRESS_PATTERN.match(line)
                label_match = LISTING_LABEL_PATTERN.match(line)
                if label_match:
                    address, label = label_match.groups()
                    if label in labels:
                        labels[label]['address'] = '0x%04X' % int(address, 16)
                        labels[label]['listing_line'] = line_number
                if not pending_source or not address_match:
                    continue

                address = int(address_match.group(1), 16)
                entry = functions.setdefault(
                    pending_source['function'],
                    {'locations': []},
                )
                locations = entry.setdefault('locations', [])
                location = next(
                    (
                        item for item in locations
                        if item['vm_line'] == pending_source['vm_line']
                    ),
                    None,
                )
                if location is None:
                    location = dict(pending_source)
                    locations.append(location)
                location['address'] = '0x%04X' % address
                location['listing_line'] = line_number
                pending_source = None

        with open(metadata_file, 'w') as file:
            json.dump(metadata, file, indent=2, ensure_ascii=False)
            file.write('\n')

    def _read_source(self, source_file, functions):
        class_name = None
        with open(source_file) as file:
            for line_number, line in enumerate(file, start=1):
                class_match = CLASS_PATTERN.match(line)
                if class_match:
                    class_name = class_match.group(1)
                subroutine_match = SUBROUTINE_PATTERN.match(line)
                if not class_name or not subroutine_match:
                    continue
                kind, name = subroutine_match.groups()
                label = '%s.%s' % (class_name, name)
                functions[label] = {
                    'source': self._relative_path(source_file),
                    'source_line': line_number,
                    'kind': kind,
                    'locations': [],
                }

    def _read_vm(self, vm_file, functions):
        pending_source = None
        with open(vm_file) as file:
            for line_number, line in enumerate(file, start=1):
                source_match = VM_SOURCE_PATTERN.match(line)
                if source_match:
                    pending_source = {
                        'source_line': int(source_match.group(1)),
                        'function': source_match.group(2),
                        'vm_line': line_number + 1,
                    }
                    continue
                match = VM_FUNCTION_PATTERN.match(line)
                if match:
                    label, local_count = match.groups()
                    entry = functions.setdefault(label, {'locations': []})
                    entry['vm_file'] = self._relative_path(vm_file)
                    entry['vm_line'] = line_number
                    entry['local_count'] = int(local_count)
                elif pending_source and line.strip() and not line.strip().startswith('//'):
                    label = pending_source['function']
                    entry = functions.setdefault(label, {'locations': []})
                    entry.setdefault('vm_file', self._relative_path(vm_file))
                    entry['locations'].append(pending_source)
                pending_source = None

    def _read_asm(self, asm_file, functions):
        labels = {}
        with open(asm_file) as file:
            for line_number, line in enumerate(file, start=1):
                source_match = ASM_SOURCE_PATTERN.match(line)
                if source_match:
                    source_line, function, vm_line = source_match.groups()
                    entry = functions.setdefault(function, {'locations': []})
                    locations = entry.setdefault('locations', [])
                    location = next(
                        (item for item in locations if item['vm_line'] == int(vm_line)),
                        None,
                    )
                    if location is None:
                        location = {
                            'source_line': int(source_line),
                            'function': function,
                            'vm_line': int(vm_line),
                        }
                        locations.append(location)
                    location['asm_line'] = line_number
                match = ASM_LABEL_PATTERN.match(line)
                if match:
                    label = match.group(1)
                    labels[label] = line_number
                    if label in RUNTIME_LABELS:
                        self.labels[label] = {'asm_line': line_number}
        for label, line_number in labels.items():
            if label in functions:
                functions[label]['asm_label'] = label
                functions[label]['asm_line'] = line_number

    def _relative_path(self, path):
        absolute_path = os.path.abspath(path)
        try:
            return os.path.relpath(absolute_path, self.project_root)
        except ValueError:
            return absolute_path
