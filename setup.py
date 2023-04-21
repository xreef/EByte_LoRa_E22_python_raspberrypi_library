import sys
sys.path.pop(0)
from setuptools import setup

setup(
    name="raspberrypi-lora-e22",
    package_dir={'': 'src'},
    py_modules=["lora_e22", "lora_e22_constants", "lora_e22_operation_constant"],
    version="0.0.2",
    description="RaspberryPi LoRa EBYTE E22 device library complete and tested. sx1262/sx1268",
    long_description="RaspberryPi Ebyte E22 LoRa (Long Range) library device very cheap and very long range (from 4Km to 10Km). LoRa EBYTE E22 device library complete and tested. sx1262/sx1268",
    keywords="LoRa, UART, EByte, RaspberryPi,sx1262, sx1268, e22",
    url="https://github.com/xreef/EByte_LoRa_E22_raspberrypi_library",
    author="Renzo Mischianti",
    author_email="renzo.mischianti@gmail.com",
    maintainer="Renzo Mischianti",
    maintainer_email="renzo.mischianti@gmail.com",
    license="MIT",
    install_requires=[],
    project_urls={
        'Documentation': 'https://www.mischianti.org/category/my-libraries/ebyte-lora-e22-devices/',
        'Documentazione': 'https://www.mischianti.org/it/category/le-mie-librerie/dispositivi-ebyte-lora-e22/',
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: Implementation :: RaspberryPi",
        "License :: OSI Approved :: MIT License",
    ],
)
