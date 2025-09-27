from smbus2 import SMBus
import math
from time import sleep
from typing import Final, List


class BMP180:
    """
    A class to interact with the BMP180 temperature and pressure sensor.
    """

    # BMP180 registers (internal constants)
    _CONTROL_REG: Final[int] = 0xF4
    _DATA_REG: Final[int] = 0xF6
    _CAL_AC1_REG: Final[int] = 0xAA
    _CAL_AC2_REG: Final[int] = 0xAC
    _CAL_AC3_REG: Final[int] = 0xAE
    _CAL_AC4_REG: Final[int] = 0xB0
    _CAL_AC5_REG: Final[int] = 0xB2
    _CAL_AC6_REG: Final[int] = 0xB4
    _CAL_B1_REG: Final[int] = 0xB6
    _CAL_B2_REG: Final[int] = 0xB8
    _CAL_MB_REG: Final[int] = 0xBA
    _CAL_MC_REG: Final[int] = 0xBC
    _CAL_MD_REG: Final[int] = 0xBE

    # Instance attributes with type hints
    address: int
    bus: SMBus
    mode: int

    # Calibration data variables
    _cal_ac1: int = 0
    _cal_ac2: int = 0
    _cal_ac3: int = 0
    _cal_ac4: int = 0
    _cal_ac5: int = 0
    _cal_ac6: int = 0
    _cal_b1: int = 0
    _cal_b2: int = 0
    _cal_mb: int = 0
    _cal_mc: int = 0
    _cal_md: int = 0

    def __init__(self, address: int = 0x77, bus_number: int = 1, mode: int = 1) -> None:
        """
        Initialize the BMP180 sensor.

        Args:
            address: The I2C address of the sensor (default is 0x77).
            bus_number: The I2C bus number (default is 1 for most Pis).
            mode: The oversampling setting (0-3), affecting accuracy and speed.
        """
        self.address = address
        self.bus = SMBus(bus_number)
        if not 0 <= mode <= 3:
            raise ValueError("Mode must be between 0 and 3.")
        self.mode = mode

        # Get the calibration data from the BMP180
        self._read_calibration_data()

    def _read_signed_16_bit(self, register: int) -> int:
        """Reads a signed 16-bit value from two adjacent registers."""
        msb = self.bus.read_byte_data(self.address, register)
        lsb = self.bus.read_byte_data(self.address, register + 1)

        # Combine bytes into a 16-bit value
        value = (msb << 8) + lsb

        # If the most significant bit is 1, it's a negative number
        if value > 32767:
            value -= 65536
        return value

    def _read_unsigned_16_bit(self, register: int) -> int:
        """Reads an unsigned 16-bit value from two adjacent registers."""
        msb = self.bus.read_byte_data(self.address, register)
        lsb = self.bus.read_byte_data(self.address, register + 1)
        return (msb << 8) + lsb

    def _read_calibration_data(self) -> None:
        """Reads and stores the factory calibration data from the sensor."""
        self._cal_ac1 = self._read_signed_16_bit(self._CAL_AC1_REG)
        self._cal_ac2 = self._read_signed_16_bit(self._CAL_AC2_REG)
        self._cal_ac3 = self._read_signed_16_bit(self._CAL_AC3_REG)
        self._cal_ac4 = self._read_unsigned_16_bit(self._CAL_AC4_REG)
        self._cal_ac5 = self._read_unsigned_16_bit(self._CAL_AC5_REG)
        self._cal_ac6 = self._read_unsigned_16_bit(self._CAL_AC6_REG)
        self._cal_b1 = self._read_signed_16_bit(self._CAL_B1_REG)
        self._cal_b2 = self._read_signed_16_bit(self._CAL_B2_REG)
        self._cal_mb = self._read_signed_16_bit(self._CAL_MB_REG)
        self._cal_mc = self._read_signed_16_bit(self._CAL_MC_REG)
        self._cal_md = self._read_signed_16_bit(self._CAL_MD_REG)

    def get_raw_temp(self) -> int:
        """Reads and returns the uncompensated (raw) temperature data."""
        self.bus.write_byte_data(self.address, self._CONTROL_REG, 0x2E)
        sleep(0.005)  # Wait 4.5ms+, 5ms is safe
        return self._read_unsigned_16_bit(self._DATA_REG)

    def get_raw_pressure(self) -> int:
        """Reads and returns the uncompensated (raw) pressure data."""
        write_val = 0x34 + (self.mode << 6)
        self.bus.write_byte_data(self.address, self._CONTROL_REG, write_val)

        wait_times: List[float] = [0.005, 0.008, 0.014, 0.026]
        sleep(wait_times[self.mode])

        msb = self.bus.read_byte_data(self.address, self._DATA_REG)
        lsb = self.bus.read_byte_data(self.address, self._DATA_REG + 1)
        xlsb = self.bus.read_byte_data(self.address, self._DATA_REG + 2)

        raw_pressure = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.mode)
        return raw_pressure

    def _calculate_b5(self, ut: int) -> int:
        """Calculate the B5 parameter used in both temp and pressure calculations."""
        x1 = (ut - self._cal_ac6) * self._cal_ac5 // (2**15)
        # Prevent division by zero
        if x1 + self._cal_md == 0:
            return 0
        x2 = self._cal_mc * (2**11) // (x1 + self._cal_md)
        return x1 + x2

    def get_temperature(self) -> float:
        """Reads the raw temperature and calculates the actual temperature.

        Returns:
            The actual temperature in degrees Celsius.
        """
        ut = self.get_raw_temp()
        b5 = self._calculate_b5(ut)
        temp_int = (b5 + 8) // (2**4)
        return temp_int / 10.0

    def get_pressure(self) -> int:
        """Reads and calculates the actual pressure.

        Returns:
            The actual pressure in Pascals.
        """
        up = self.get_raw_pressure()
        ut = self.get_raw_temp()
        b5 = self._calculate_b5(ut)

        b6 = b5 - 4000
        x1 = (self._cal_b2 * (b6 * b6 // (2**12))) // (2**11)
        x2 = self._cal_ac2 * b6 // (2**11)
        x3 = x1 + x2
        b3 = (((self._cal_ac1 * 4 + x3) << self.mode) + 2) // 4

        x1 = self._cal_ac3 * b6 // (2**13)
        x2 = (self._cal_b1 * (b6 * b6 // (2**12))) // (2**16)
        x3 = ((x1 + x2) + 2) // 4
        b4 = self._cal_ac4 * (x3 + 32768) // (2**15)
        b7 = (up - b3) * (50000 >> self.mode)

        p: int
        if b7 < 0x80000000:
            p = (b7 * 2) // b4
        else:
            p = (b7 // b4) * 2

        x1 = (p // (2**8)) ** 2
        x1 = (x1 * 3038) // (2**16)
        x2 = (-7357 * p) // (2**16)

        pressure = p + (x1 + x2 + 3791) // (2**4)
        return pressure

    def get_altitude(self, sea_level_pressure: int = 101325) -> float:
        """Calculates the altitude in meters from the pressure.

        Args:
            sea_level_pressure: The current sea-level atmospheric pressure in Pascals.

        Returns:
            The altitude in meters.
        """
        pressure = float(self.get_pressure())
        # Formula from BMP180 datasheet
        altitude = 44330.0 * (1.0 - pow(pressure / sea_level_pressure, 1 / 5.255))
        # HACK: annoyingly, an overload of `pow` can return Any, so we marshall the type here
        # on the bright side, this is the only of these hacks needed to make mypy pass on strict!
        assert isinstance(
            altitude, float
        ), "If this happened, you are in for an immense world of pain. Hi!"
        return altitude


if __name__ == "__main__":
    try:
        # Initialize sensor on I2C bus 1 with default address 0x77
        bmp = BMP180(bus_number=1)

        temp = bmp.get_temperature()
        pressure = bmp.get_pressure()
        altitude = bmp.get_altitude()

        print(f"Temperature: {temp:.2f} °C")
        print(
            f"Pressure: {pressure / 100.0:.2f} hPa"
        )  # Convert Pa to hPa for readability
        print(f"Altitude: {altitude:.2f} m")

    except (IOError, FileNotFoundError) as e:
        print("Error: I2C bus not found or BMP180 sensor not connected.")
        print(f"Details: {e}")
