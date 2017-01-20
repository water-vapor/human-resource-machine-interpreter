import itertools
import re


def hmri(raw_code, inputs=[], memory_size=16, memory={}):
    """Interpret human resource machine program.

    Keyword arguments:
    raw_code -- HRM code in a list, each element containing a line
    memory_size -- total number of blocks
    memory -- given memory state, dictionary

    """
    # helper function
    def read_address(raw_addr):
        if raw_addr[-1] == ']':
            point_to = int(raw_addr[1:-1])
            assert point_to < memory_size
            assert point_to in memory
            address = memory[point_to]
            assert isinstance(address, int)
        else:
            address = int(raw_addr)
        assert address < memory_size
        return address

    # check head
    assert raw_code[0] == '-- HUMAN RESOURCE MACHINE PROGRAM --'
    assert raw_code[1] == ''
    # remove tail comments and spaces
    code = list(itertools.takewhile(lambda x: x != '', raw_code[2:]))

    program_length = len(code)
    program_counter = 0
    program_steps = 0
    program_finished = program_counter >= program_length

    # mark jump labels
    label_pattern = re.compile('.+:')
    labels = {}
    for i in range(program_length):
        if label_pattern.fullmatch(code[i]) is not None:
            labels[code[i][:-1]] = i

    # comment lines
    comment_pattern = re.compile("comment.+")
    comment_counts = 0
    for i in range(program_length):
        if comment_pattern.fullmatch(code[i]) is not None:
            comment_counts += 1

    program_size = program_length - len(labels) - comment_counts
    current_value = None
    outputs = []
    while not program_finished:
        current_line = code[program_counter].split()

        if current_line[0] == 'INBOX':
            # the end of infinite loop program in HRM
            if inputs == []:
                break
            current_value = inputs.pop(0)
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'OUTBOX':
            # cannot output an empty value
            assert current_value is not None
            outputs.insert(0, current_value)
            current_value = None
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'COPYFROM':
            address = read_address(current_line[1])
            assert address in memory
            current_value = memory[address]
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'COPYTO':
            assert current_value is not None
            address = read_address(current_line[1])
            memory[address] = current_value
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'ADD':
            assert current_value is not None
            address = read_address(current_line[1])
            assert isinstance(current_value, int) and isinstance(
                memory[address], int)
            current_value = current_value + memory[address]
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'SUB':
            assert current_value is not None
            address = read_address(current_line[1])
            if (isinstance(current_value, str) and
                    isinstance(memory[address], str)):
                current_value = ord(current_value) - ord(memory[address])
            elif (isinstance(current_value, int) and
                    isinstance(memory[address], int)):
                current_value = current_value - memory[address]
            else:
                assert False
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'BUMPUP':
            address = read_address(current_line[1])
            assert isinstance(memory[address], int)
            memory[address] += 1
            current_value = memory[address]
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'BUMPDN':
            address = read_address(current_line[1])
            assert isinstance(memory[address], int)
            memory[address] -= 1
            current_value = memory[address]
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'JUMP':
            jump_label = current_line[1]
            program_counter = labels[jump_label]
            program_steps += 1

        elif current_line[0] == 'JUMPZ':
            assert current_value is not None
            jump_label = current_line[1]
            if current_value == 0:
                program_counter = labels[jump_label]
            else:
                program_counter += 1
            program_steps += 1

        elif current_line[0] == 'JUMPN':
            assert current_value is not None
            jump_label = current_line[1]
            if current_value < 0:
                program_counter = labels[jump_label]
            else:
                program_counter += 1
            program_steps += 1

        else:
            program_counter += 1

        program_finished = program_counter >= program_length

    return [outputs, program_steps, program_size]

def read_file(filename):
    """Read Human Resource Machine Code File

    filename -- path of the code file
    """
    with open(filename) as f:
        code = f.readlines()
    return [x.strip() for x in code]
