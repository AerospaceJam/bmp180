# bmp180

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

A modern, typed, and robust Python library for the Bosch BMP180 barometric pressure and temperature sensor, designed for use with Raspberry Pi.

Modernized by **Henry Martin** for the **Aerospace Jam**.

## 1. Prerequisites

### Hardware

- A Raspberry Pi (any model with GPIO pins).
- A BMP180 sensor breakout board.
- Jumper wires to connect the sensor to your Pi.

### Software

- Python 3.10 or newer.
- `git` installed on your Raspberry Pi.

### Enable I2C on Your Raspberry Pi

Before you can use the sensor, you must enable the I2C interface.

1. Open a terminal on your Raspberry Pi.
2. Run the Raspberry Pi configuration tool:

    ```bash
    sudo raspi-config
    ```

3. Navigate to `3 Interface Options` -> `I5 I2C`.
4. Select `<Yes>` to enable the ARM I2C interface.
5. Reboot your Pi when prompted.

## 2. Installation

This package is not published on PyPI. The recommended way to install it is directly from the GitHub repository using `pip`.

Open your terminal and run the following command:

```bash
pip install git+https://github.com/AerospaceJam/bmp180.git
```

If you're competing in Aerospace Jam and using the [SDK](https://github.com/AerospaceJam/sdk), this is already preinstalled on your Pi and needs no other action.

## 3. Quick Start & Usage

Using the library is straightforward. Connect your BMP180 sensor to the I2C pins on your Raspberry Pi (SDA, SCL, 3.3V, GND) and run the following Python code.

Create a file named `test_sensor.py`:

```python
from bmp180 import BMP180

try:
    # Initialize the sensor.
    # The I2C bus number is 1 for most modern Raspberry Pi models.
    bmp = BMP180(bus_number=1)

    # Get sensor data
    temperature = bmp.get_temperature()
    pressure = bmp.get_pressure()
    altitude = bmp.get_altitude()

    # Print the data in a friendly format
    print(f"Temperature: {temperature:.2f} °C")
    print(f"Pressure: {pressure / 100.0:.2f} hPa") # Convert Pa to hPa
    print(f"Altitude: {altitude:.2f} m")

except (IOError, FileNotFoundError):
    print("Error: Could not find the BMP180 sensor.")
    print("Please check your I2C connections and ensure the interface is enabled.")

```

Run the script from your terminal:

```bash
python test_sensor.py
```

**Expected Output:**

```txt
Temperature: 24.50 °C
Pressure: 1012.34 hPa
Altitude: 12.34 m
```

## Acknowledgments

- This library is a modernized version of the original [BMP180-Python library](https://github.com/Tijndagamer/BMP180-Python) created by **MrTijn/Tijndagamer**. Thanks for the original logic and implementation.

## License

This project is distributed under the MIT License. See the `LICENSE` file for more details.
