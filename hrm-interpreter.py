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
    def address_test(addr, target_must_exist=True):
        assert isinstance(addr, int), "Address should be an integer"
        assert addr < memory_size and addr >= 0, "Memory address out of bound"
        if target_must_exist:
            assert addr in memory, "The referenced memory is empty"

    def current_value_test(val):
        assert val is not None, "Value expected"

    def read_address(raw_addr):
        if raw_addr[-1] == ']':
            point_to = int(raw_addr[1:-1])
            address_test(point_to)
            address = memory[point_to]
        else:
            address = int(raw_addr)
        address_test(address, target_must_exist=False)
        return address

    # check head
    assert (raw_code[0] == '-- HUMAN RESOURCE MACHINE PROGRAM'
            and raw_code[1] == ''), "Invalid code head"

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
            current_value_test(current_value)
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
            current_value_test(current_value)
            address = read_address(current_line[1])
            memory[address] = current_value
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'ADD':
            current_value_test(current_value)
            address = read_address(current_line[1])
            assert isinstance(current_value, int) and isinstance(
                memory[address], int), "You can only add integers"
            current_value = current_value + memory[address]
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'SUB':
            current_value_test(current_value)
            address = read_address(current_line[1])
            if (isinstance(current_value, str) and
                    isinstance(memory[address], str)):
                current_value = ord(current_value) - ord(memory[address])
            elif (isinstance(current_value, int) and
                    isinstance(memory[address], int)):
                current_value = current_value - memory[address]
            else:
                assert False, "You can only subtract letters and integers"
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'BUMPUP':
            address = read_address(current_line[1])
            assert isinstance(
                memory[address], int), "You can only bump up an integer"
            memory[address] += 1
            current_value = memory[address]
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'BUMPDN':
            address = read_address(current_line[1])
            assert isinstance(
                memory[address], int), "You can only bump down an integer"
            memory[address] -= 1
            current_value = memory[address]
            program_counter += 1
            program_steps += 1

        elif current_line[0] == 'JUMP':
            jump_label = current_line[1]
            program_counter = labels[jump_label]
            program_steps += 1

        elif current_line[0] == 'JUMPZ':
            current_value_test(current_value)
            jump_label = current_line[1]
            if current_value == 0:
                program_counter = labels[jump_label]
            else:
                program_counter += 1
            program_steps += 1

        elif current_line[0] == 'JUMPN':
            current_value_test(current_value)
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
    """Read Human Resource Machine Code File.

    filename -- path of the code file
    """
    with open(filename) as f:
        code = f.readlines()
    return [x.strip() for x in code]
