import math

base_address = 0xC000
mem_size = 0x1000


class Memory:
    def __init__(self):
        self.memory = [x * 0 for x in range(0, mem_size + 4)]
        self.mem_free_list = base_address + 64
        self.memory[self.mem_free_list - base_address] = base_address % 256
        self.memory[self.mem_free_list - base_address + 1] = math.floor(base_address / 256)
        self.prev_block_link = self.mem_free_list
        free_size = mem_size - 4
        self.memory[2] = free_size % 256
        self.memory[3] = math.floor(free_size / 256)

    def mem_alloc(self, req_size):
        block_p = self.ld16(self.mem_free_list)
        req_size_2 = req_size * 2
        while True:
            next_block_p = self.ld16(block_p)
            size = self.ld16(block_p + 2)
            if size >= req_size_2:
                self.st16(block_p + 2, req_size_2)
                if (size - req_size_2) > 4:
                    new_block_p = block_p + 4 + req_size_2
                    self.st16(new_block_p, next_block_p)
                    block_p_size = req_size_2 + 4
                    self.st16(new_block_p + 2, size - block_p_size)
                    self.st16(self.prev_block_link, new_block_p)
                else:
                    self.st16(self.prev_block_link, next_block_p)
                self.st16(block_p, 0)
                return block_p + 4
            else:
                if next_block_p == 0:   # defect
                    break
                else:
                    self.prev_block_link = block_p
                    block_p = next_block_p

    def mem_dealloc(self, o):
        next_bloc_p = self.ld16(self.mem_free_list)
        self.st16(self.mem_free_list, o - 4)
        self.st16(o - 4, next_bloc_p)

    def ld16(self, address):
        zero_address = address - base_address
        val = self.memory[zero_address] + self.memory[zero_address + 1] * 256
        return val

    def st16(self, address, value):
        zero_address = address - base_address
        l_val = value & 0x00FF
        h_val = math.floor((value & 0xFF00) / 256)
        self.memory[zero_address] = l_val
        self.memory[zero_address + 1] = h_val

    def dump_em(self):
        print('     00 01 02 03 04 05 06 07')
        for i in range(0, 9):
            row_value = []
            for j in range(0, 8):
                address = i * 8 + j
                row_value.append(format(self.memory[address], '02x'))
            row_value_string = ' '.join(row_value)
            print('%s %s' % (format(base_address + i * 8, '04x'), row_value_string))
        print()
