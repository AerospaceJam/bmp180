"""
A modern, typed Python module for the BMP180 temperature and pressure sensor.

This package provides a simple and robust interface for interacting with the
Bosch BMP180 barometric pressure and temperature sensor over an I2C bus on
devices like the Raspberry Pi. It offers straightforward methods to read
calibrated temperature, pressure, and calculate altitude.

The library is designed with modern Python features, including type hints,
and is a `mypy` compliant fork of the original work by MrTijn/Tijndagamer.

Example:
    >>> from bmp180 import BMP180
    >>>
    >>> try:
    ...     # Initialize the sensor on I2C bus 1 (default for most Pis)
    ...     bmp = BMP180(bus_number=1)
    ...
    ...     temperature = bmp.get_temperature()
    ...     pressure = bmp.get_pressure()
    ...     altitude = bmp.get_altitude()
    ...
    ...     print(f"Temperature: {temperature:.2f} °C")
    ...     print(f"Pressure: {pressure / 100.0:.2f} hPa")
    ...     print(f"Altitude: {altitude:.2f} m")
    ...
    ... except (IOError, FileNotFoundError):
    ...     print("Error: Could not find BMP180 sensor on I2C bus.")

Modernized by Henry Martin for the Aerospace Jam.
https://github.com/AerospaceJam/bmp180
"""

from .bmp180 import BMP180
