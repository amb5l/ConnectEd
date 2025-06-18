from typing  import Self, TextIO
from pathlib import Path
from io      import StringIO

import random

from ConnectEd.hdl.vhdl import VhdlDocument, VhdlEntity, \
                               VhdlGeneric, VhdlPortGroup, VhdlPort

from ConnectEd.hdl.vhdl.vhdl_visitor import VhdlVisitor

from tests.utils import MinMax


class TestFixtures:
    def test_design_units(self : Self):
        test_file = Path(__file__).parent.parent / 'fixtures' / 'hdl' / 'design_units.vhd'
        test_doc = VhdlDocument.FromFile(test_file)
        assert test_doc is not None, 'Document should be parsed successfully'

        assert len(test_doc.entities) == 1, 'Should detect one entity'
        assert len(test_doc.entities[0].generics) == 2, 'Should detect two generics'
        assert test_doc.entities[0].generics[0].name == 'GENERIC1', 'Should detect generic1'
        assert test_doc.entities[0].generics[1].name == 'GENERIC2', 'Should detect generic2'
        assert len(test_doc.entities[0].ports) == 3, 'Should detect three ports'
        assert test_doc.entities[0].ports[0].name == 'port1', 'Should detect port1'
        assert test_doc.entities[0].ports[1].name == 'port2', 'Should detect port2'
        assert test_doc.entities[0].ports[2].name == 'port3', 'Should detect port3'
        assert test_doc.entities[0].ports[0].mode == 'in', 'Should detect in mode for port1'
        assert test_doc.entities[0].ports[1].mode == 'out', 'Should detect out mode for port2'
        assert test_doc.entities[0].ports[2].mode == 'inout', 'Should detect inout mode for port3'
        assert test_doc.entities[0].ports[0].datatype == 'std_logic', 'Should detect std_logic datatype for port1'
        assert test_doc.entities[0].ports[1].datatype == 'std_logic', 'Should detect std_logic datatype for port2'
        assert test_doc.entities[0].ports[2].datatype == 'std_logic_vector(GENERIC1-1 downto 0)', 'Should detect full datatype with whitespace for port3'
        assert len(test_doc.entities[0].port_groups) == 1, 'Should detect one port group'
        assert test_doc.entities[0].port_groups[0].name == '', 'Should detect "" as port group name'
        assert len(test_doc.entities[0].port_groups[0].ports) == 3, 'Should detect three ports in port group'
        assert test_doc.entities[0].port_groups[0].ports[0].name == 'port1', 'Should detect port1'
        assert test_doc.entities[0].port_groups[0].ports[1].name == 'port2', 'Should detect port2'
        assert test_doc.entities[0].port_groups[0].ports[2].name == 'port3', 'Should detect port3'
        assert test_doc.entities[0].port_groups[0].ports[0].mode == 'in', 'Should detect in mode for port1'
        assert test_doc.entities[0].port_groups[0].ports[1].mode == 'out', 'Should detect out mode for port2'
        assert test_doc.entities[0].port_groups[0].ports[2].mode == 'inout', 'Should detect inout mode for port3'
        assert test_doc.entities[0].port_groups[0].ports[0].datatype == 'std_logic', 'Should detect std_logic datatype for port1'
        assert test_doc.entities[0].port_groups[0].ports[1].datatype == 'std_logic', 'Should detect std_logic datatype for port2'
        assert test_doc.entities[0].port_groups[0].ports[2].datatype == 'std_logic_vector(GENERIC1-1 downto 0)', 'Should detect full datatype with whitespace for port3'

        assert len(test_doc.architectures) == 1, 'Should detect one architecture'
        assert len(test_doc.architectures[0].components) == 1, 'Should detect one component'
        assert test_doc.architectures[0].components[0].name == 'component1', 'Should detect component1'
        assert len(test_doc.architectures[0].components[0].ports) == 3, 'Should detect three ports'
        assert test_doc.architectures[0].components[0].ports[0].name == 'port1', 'Should detect port1'
        assert test_doc.architectures[0].components[0].ports[1].name == 'port2', 'Should detect port2'
        assert test_doc.architectures[0].components[0].ports[2].name == 'port3', 'Should detect port3'
        assert test_doc.architectures[0].components[0].ports[0].mode == 'in', 'Should detect in mode for port1'
        assert test_doc.architectures[0].components[0].ports[1].mode == 'out', 'Should detect out mode for port2'
        assert test_doc.architectures[0].components[0].ports[2].mode == 'inout', 'Should detect inout mode for port3'
        assert test_doc.architectures[0].components[0].ports[0].datatype == 'std_logic', 'Should detect std_logic datatype for port1'
        assert test_doc.architectures[0].components[0].ports[1].datatype == 'std_logic', 'Should detect std_logic datatype for port2'
        assert test_doc.architectures[0].components[0].ports[2].datatype == 'std_logic_vector(GENERIC1-1 downto 0)', 'Should detect full datatype with whitespace for port3'
        assert len(test_doc.architectures[0].components[0].port_groups) == 1, 'Should detect one port group'
        assert test_doc.architectures[0].components[0].port_groups[0].name == '', 'Should detect "" as port group name'
        assert len(test_doc.architectures[0].components[0].port_groups[0].ports) == 3, 'Should detect three ports in port group'
        assert test_doc.architectures[0].components[0].port_groups[0].ports[0].name == 'port1', 'Should detect port1'
        assert test_doc.architectures[0].components[0].port_groups[0].ports[1].name == 'port2', 'Should detect port2'
        assert test_doc.architectures[0].components[0].port_groups[0].ports[2].name == 'port3', 'Should detect port3'
        assert test_doc.architectures[0].components[0].port_groups[0].ports[0].mode == 'in', 'Should detect in mode for port1'
        assert test_doc.architectures[0].components[0].port_groups[0].ports[1].mode == 'out', 'Should detect out mode for port2'
        assert test_doc.architectures[0].components[0].port_groups[0].ports[2].mode == 'inout', 'Should detect inout mode for port3'
        assert test_doc.architectures[0].components[0].port_groups[0].ports[0].datatype == 'std_logic', 'Should detect std_logic datatype for port1'
        assert test_doc.architectures[0].components[0].port_groups[0].ports[1].datatype == 'std_logic', 'Should detect std_logic datatype for port2'
        assert test_doc.architectures[0].components[0].port_groups[0].ports[2].datatype == 'std_logic_vector(GENERIC1-1 downto 0)', 'Should detect full datatype with whitespace for port3'

        assert len(test_doc.packages) == 1, 'Should detect one package'
        assert len(test_doc.packages[0].components) == 1, 'Should detect one component'
        assert test_doc.packages[0].components[0].name == 'component2', 'Should detect component2'
        assert test_doc.packages[0].components[0].ports[0].name     == 'port1', 'Should detect port1'
        assert test_doc.packages[0].components[0].ports[1].name     == 'port2', 'Should detect port2'
        assert test_doc.packages[0].components[0].ports[2].name     == 'port3', 'Should detect port3'
        assert test_doc.packages[0].components[0].ports[0].mode     == 'in', 'Should detect in mode for port1'
        assert test_doc.packages[0].components[0].ports[1].mode     == 'out', 'Should detect out mode for port2'
        assert test_doc.packages[0].components[0].ports[2].mode     == 'inout', 'Should detect inout mode for port3'
        assert test_doc.packages[0].components[0].ports[0].datatype == 'std_logic', 'Should detect std_logic datatype for port1'
        assert test_doc.packages[0].components[0].ports[1].datatype == 'std_logic', 'Should detect std_logic datatype for port2'
        assert test_doc.packages[0].components[0].ports[2].datatype == 'std_logic_vector(GENERIC1-1 downto 0)', 'Should detect full datatype with whitespace for port3'
        assert len(test_doc.packages[0].components[0].port_groups) == 2, 'Should detect two port groups'
        assert test_doc.packages[0].components[0].port_groups[0].name == 'Group 1', 'Should detect "Group 1" as port group name'
        assert len(test_doc.packages[0].components[0].port_groups[0].ports) == 3, 'Should detect three ports in port group'
        assert test_doc.packages[0].components[0].port_groups[0].ports[0].name     == 'port1', 'Should detect port1'
        assert test_doc.packages[0].components[0].port_groups[0].ports[1].name     == 'port2', 'Should detect port2'
        assert test_doc.packages[0].components[0].port_groups[0].ports[2].name     == 'port3', 'Should detect port3'
        assert test_doc.packages[0].components[0].port_groups[0].ports[0].mode     == 'in', 'Should detect in mode for port1'
        assert test_doc.packages[0].components[0].port_groups[0].ports[1].mode     == 'out', 'Should detect out mode for port2'
        assert test_doc.packages[0].components[0].port_groups[0].ports[2].mode     == 'inout', 'Should detect inout mode for port3'
        assert test_doc.packages[0].components[0].port_groups[0].ports[0].datatype == 'std_logic', 'Should detect std_logic datatype for port1'
        assert test_doc.packages[0].components[0].port_groups[0].ports[1].datatype == 'std_logic', 'Should detect std_logic datatype for port2'
        assert test_doc.packages[0].components[0].port_groups[0].ports[2].datatype == 'std_logic_vector(GENERIC1-1 downto 0)', 'Should detect full datatype with whitespace for port3'
        assert test_doc.packages[0].components[0].port_groups[1].name == 'Group 2', 'Should detect "Group 2" as port group name'
        assert len(test_doc.packages[0].components[0].port_groups[1].ports) == 3, 'Should detect three ports in port group'
        assert test_doc.packages[0].components[0].port_groups[1].ports[0].name == 'port4', 'Should detect port4'
        assert test_doc.packages[0].components[0].port_groups[1].ports[1].name == 'port5', 'Should detect port5'
        assert test_doc.packages[0].components[0].port_groups[1].ports[2].name == 'port6', 'Should detect port6'
        assert test_doc.packages[0].components[0].port_groups[1].ports[0].mode == 'in', 'Should detect in mode for port4'
        assert test_doc.packages[0].components[0].port_groups[1].ports[1].mode == 'out', 'Should detect out mode for port5'
        assert test_doc.packages[0].components[0].port_groups[1].ports[2].mode == 'inout', 'Should detect inout mode for port6'
        assert test_doc.packages[0].components[0].port_groups[1].ports[0].datatype == 'std_logic', 'Should detect std_logic datatype for port4'
        assert test_doc.packages[0].components[0].port_groups[1].ports[1].datatype == 'std_logic', 'Should detect std_logic datatype for port5'
        assert test_doc.packages[0].components[0].port_groups[1].ports[2].datatype == 'std_logic_vector(GENERIC1-1 downto 0)', 'Should detect full datatype with whitespace for port6'


class TestRandom:
    def test_random_entities(self):
        for n in range(1, 100):
            stream = StringIO()

            expected_entity = self.generateRandomEntity(stream, f'entity{n}')
            assert expected_entity is not None, 'expected_entity should be generated successfully'
            assert expected_entity.name == f'entity{n}', 'expected_entity name should be correct'

            stream.seek(0)
            parsed_doc = VhdlDocument.fromStream(stream)
            assert parsed_doc is not None, 'parsed_doc should be parsed successfully'
            assert len(parsed_doc.entities) == 1, '1 entity expected'
            assert parsed_doc.entities[0].name == expected_entity.name, 'parsed vs expected: name should be correct'
            assert len(parsed_doc.entities[0].generics) == len(expected_entity.generics), 'parsed vs expected: number of generics should be correct'
            for i in range(len(expected_entity.generics)):
                assert parsed_doc.entities[0].generics[i].name     == expected_entity.generics[i].name,     'parsed vs expected: generic name should be correct'
                assert parsed_doc.entities[0].generics[i].datatype == expected_entity.generics[i].datatype, 'parsed vs expected: generic datatype should be correct'
                assert parsed_doc.entities[0].generics[i].default  == expected_entity.generics[i].default,  'parsed vs expected: generic default should be correct'
            assert len(parsed_doc.entities[0].port_groups) == len(expected_entity.port_groups), 'parsed vs expected: number of port groups should be correct'
            for g in range(len(expected_entity.port_groups)):
                assert len(parsed_doc.entities[0].port_groups[g].ports) == len(expected_entity.port_groups[g].ports), 'parsed vs expected: number of ports in port group should be correct'
                for i in range(len(expected_entity.port_groups[g].ports)):
                    assert parsed_doc.entities[0].port_groups[g].ports[i].name     == expected_entity.port_groups[g].ports[i].name,     'parsed vs expected: port name should be correct'
                    assert parsed_doc.entities[0].port_groups[g].ports[i].mode     == expected_entity.port_groups[g].ports[i].mode,     'parsed vs expected: port mode should be correct'
                    assert parsed_doc.entities[0].port_groups[g].ports[i].datatype == expected_entity.port_groups[g].ports[i].datatype, 'parsed vs expected: port datatype should be correct'
                    assert parsed_doc.entities[0].port_groups[g].ports[i].default  == expected_entity.port_groups[g].ports[i].default,  'parsed vs expected: port default should be correct'

    def generateRandomEntity(
        self        : Self,
        stream      : TextIO,
        name        : str,
        generics    : MinMax = MinMax(0, 5),
        port_groups : MinMax = MinMax(0, 5),
        ports       : MinMax = MinMax(1, 5)
    ) -> VhdlEntity:
        stream.write(f'entity {name} is\n')
        entity = VhdlEntity(name)
        n_generics = random.randint(generics.min, generics.max)
        if n_generics > 0:
            stream.write(f'  generic (\n')
            for n_generic in range(n_generics):
                generic_name = f'GENERIC{n_generic}'
                stream.write(f'    {generic_name} : ')
                datatype_choice = random.choice([1, 2, 3])
                match datatype_choice:
                    case  1: datatype = f'bit'
                    case  2: datatype = f'std_logic_vector(3 downto 0)'
                    case  3: datatype = 'integer'
                match datatype_choice:
                    case  1: default = "'1'"
                    case  2: default = '"0101"'
                    case  3: default = '99'
                stream.write(f'{datatype} := {default};\n')
                entity.addGeneric(VhdlGeneric(generic_name, datatype, default))
            stream.write(f'  );\n')
        n_port_groups = random.randint(port_groups.min, port_groups.max)
        if n_port_groups > 0:
            stream.write(f'  port (\n')
            for n_port_group in range(n_port_groups):
                port_group_name = f'Group {n_port_group + 1}' \
                    if n_port_groups > 1 else ''
                port_group = VhdlPortGroup(port_group_name, [])
                n_before = random.randint(0, 2)
                n_comment = random.randint(0, 2)
                n_after = random.randint(0, 2)
                stream.write('\n' * n_before)
                if n_comment > 0:
                    stream.write(f'    -- {port_group_name}\n')
                if n_comment > 1:
                    stream.write(f'    --\n' * (n_comment - 1))
                stream.write(f'\n' * n_after)
                if n_port_group > 0 and n_before + n_comment + n_after == 0:
                    stream.write('\n') # ensure >=1 empty line between groups
                n_ports = random.randint(ports.min, ports.max)
                for n_port in range(n_ports):
                    port_name = f'port{n_port + 1}'
                    stream.write(f'    {port_name} : ')
                    mode = random.choice(['in', 'out', 'inout'])
                    stream.write(f'{mode} ')
                    datatype_choice = random.choice([1, 2, 3])
                    match datatype_choice:
                        case  1: datatype = f'bit'
                        case  2: datatype = f'std_logic_vector(3 downto 0)'
                        case  3: datatype = 'integer'
                    if random.choice([True, False]):
                        match datatype_choice:
                            case  1: default = "'1'"
                            case  2: default = '"0101"'
                            case  3: default = '99'
                    else:
                        default = ''
                    stream.write(f'{datatype}{' := ' if default else ''}{default};\n')
                    port_group.addPort(VhdlPort(port_name, mode, datatype, default))
                if n_port_group == n_port_groups - 1:
                    stream.write(f'\n' * random.randint(0, 2))
                entity.addPortGroup(port_group)
            stream.write(f'  );\n')
        stream.write(f'end')
        if random.choice([True, False]):
            stream.write(f' entity')
        if random.choice([True, False]):
            stream.write(f' {entity.name}')
        stream.write(f';\n')
        return entity


class TestMisc:
    def test_extract_constraint(self):
        good_test_cases = [
            ("WIDTH-1 downto 0", ("width-1", "downto", "0")),
            ("WIDTH-1downto0", ("width-1", "downto", "0")),
            ("(WIDTH-1)downto(0)", ("(width-1)", "downto", "(0)")),
            ("(WIDTH-1) downto (START+1)", ("(width-1)", "downto", "(start+1)")),
            ("42 downto 5", ("42", "downto", "5")),
            ("2*WIDTH-1   downto   0", ("2*width-1", "downto", "0")),
            ("7 to 0", ("7", "to", "0")),
            ("7to0", ("7", "to", "0")),
            ("(BASE+1) to (END-1)", ("(base+1)", "to", "(end-1)")),
            ("BASE_ADDR to OFFSET", ("base_addr", "to", "offset")),
            ("downto_val downto 0", ("downto_val", "downto", "0"))
        ]
        bad_test_cases = [
            ("WIDTH-1 0", (None, None, None)),  # No downto or to
            ("WIDTH-1downto", (None, None, None))  # Missing right bound
        ]
        for test_case in good_test_cases:
            s, (e_left, e_direction, e_right) = test_case
            extracted = VhdlVisitor.extractConstraint(s)
            assert extracted is not None, 'extracted should be not None'
            left, direction, right = extracted
            assert left is not None, 'left should be extracted'
            assert direction is not None, 'direction should be extracted'
            assert right is not None, 'right should be extracted'
            assert left == e_left, 'left should be correct'
            assert direction == e_direction, 'direction should be correct'
            assert right == e_right, 'right should be correct'
        for test_case in bad_test_cases:
            s, (_, _, _) = test_case
            extracted = VhdlVisitor.extractConstraint(s)
            assert extracted is None, 'extracted should be None'
