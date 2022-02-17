import struct

import numpy
from umodbus import conf, functions
from umodbus.exceptions import IllegalDataValueError


def unpack_bits(resp_pdu, req_pdu):
    count = struct.unpack(">H", req_pdu[-2:])[0]
    byte_count = struct.unpack(">B", resp_pdu[1:2])[0]
    packed = numpy.frombuffer(resp_pdu, dtype="u1", offset=2, count=byte_count)
    return numpy.unpackbits(packed, count=count, bitorder="little")


def pack_bits(function_code, starting_address, values):
    if not isinstance(values, numpy.ndarray):
        values = numpy.array(values, dtype="u1")
    packed = numpy.packbits(values, bitorder="little")
    count = values.size
    header = struct.pack(
        ">BHHB", function_code, starting_address, count, (count + 7) // 8
    )
    return header + packed.tobytes()


def unpack_16bits(resp_pdu, req_pdu):
    count = struct.unpack(">H", req_pdu[-2:])[0]
    dtype = ">{}2".format("i" if conf.SIGNED_VALUES else "u")
    return numpy.frombuffer(resp_pdu, dtype=dtype, count=count, offset=2)


def pack_16bits(function_code, starting_address, values):
    dtype = ">{}2".format("i" if conf.SIGNED_VALUES else "u")
    values = numpy.array(values, dtype=dtype, copy=False)
    header = struct.pack(
        ">BHHB", function_code, starting_address, values.size, values.nbytes
    )
    return header + values.tobytes()


class ReadCoils(functions.ReadCoils):
    @classmethod
    def create_from_response_pdu(cls, resp_pdu, req_pdu):
        """Create instance from response PDU.

        Response PDU is required together with the quantity of coils read.

        :param resp_pdu: Byte array with request PDU.
        :param quantity: Number of coils read.
        :return: Instance of :class:`ReadCoils`.
        """
        read_coils = cls()
        read_coils.data = unpack_bits(resp_pdu, req_pdu)
        read_coils.quantity = read_coils.data.size
        return read_coils


class ReadDiscreteInputs(functions.ReadDiscreteInputs):
    @classmethod
    def create_from_response_pdu(cls, resp_pdu, req_pdu):
        """Create instance from response PDU.

        Response PDU is required together with the quantity of inputs read.

        :param resp_pdu: Byte array with request PDU.
        :param quantity: Number of inputs read.
        :return: Instance of :class:`ReadDiscreteInputs`.
        """
        read_discrete_inputs = cls()
        read_discrete_inputs.data = unpack_bits(resp_pdu, req_pdu)
        read_discrete_inputs.quantity = read_discrete_inputs.data.size
        return read_discrete_inputs


class ReadHoldingRegisters(functions.ReadHoldingRegisters):
    @classmethod
    def create_from_response_pdu(cls, resp_pdu, req_pdu):
        """Create instance from response PDU.

        Response PDU is required together with the number of registers read.

        :param resp_pdu: Byte array with request PDU.
        :param quantity: Number of registers to read.
        :return: Instance of :class:`ReadHoldingRegisters`.
        """
        read_holding_registers = cls()
        read_holding_registers.data = unpack_16bits(resp_pdu, req_pdu)
        read_holding_registers.quantity = read_holding_registers.data.size
        return read_holding_registers


class ReadInputRegisters(functions.ReadInputRegisters):
    @classmethod
    def create_from_response_pdu(cls, resp_pdu, req_pdu):
        """Create instance from response PDU.

        Response PDU is required together with the number of registers read.

        :param resp_pdu: Byte array with request PDU.
        :param quantity: Number of coils read.
        :return: Instance of :class:`ReadCoils`.
        """
        read_input_registers = cls()
        read_input_registers.data = unpack_16bits(resp_pdu, req_pdu)
        read_input_registers.quantity = read_input_registers.data.size
        return read_input_registers


def request_pdu_coils(self):
    if self.starting_address is None or self._values is None:
        raise IllegalDataValueError
    return pack_bits(self.function_code, self.starting_address, self._values)


def request_pdu_registers(self):
    if self.starting_address is None or self._values is None:
        raise IllegalDataValueError
    return pack_16bits(self.function_code, self.starting_address, self._values)


# Patch umodbus to do our biding (which is to handle numpy arrays)
functions.WriteMultipleCoils.request_pdu = property(request_pdu_coils)
functions.WriteMultipleRegisters.request_pdu = property(request_pdu_registers)

function_code_to_function_map = {
    functions.READ_COILS: ReadCoils,
    functions.READ_DISCRETE_INPUTS: ReadDiscreteInputs,
    functions.READ_HOLDING_REGISTERS: ReadHoldingRegisters,
    functions.READ_INPUT_REGISTERS: ReadInputRegisters,
}

functions.function_code_to_function_map.update(function_code_to_function_map)
