
Tuya Energy Custom Component for Home Assistant

This custom component provides local control and monitoring for Tuya-based energy devices (e.g., circuit breakers, smart meters) that use Protocol 3.5 and expose specific Data Points (DPs) for energy monitoring and control.
Features

    Local Communication: Communicates directly with your Tuya device over the local network, without relying on the Tuya cloud.
    Protocol 3.5 Support: Specifically designed to work with Tuya devices using Protocol 3.5.
    Energy Monitoring: Provides sensors for Voltage, Current, Power, and Total Energy Consumption.
    Control: Switch entity for main power control and child lock.
    Configuration: Select entities for Relay Status and Light Mode, Number entity for Countdown, and Text entity for Cycle Time.
    Diagnostic: Binary sensor for Online State and Fault status.
    Energy Dashboard Integration: Energy sensors are properly configured for seamless integration with Home Assistant's Energy Dashboard.
    Intelligent Polling: Automatically adjusts polling frequency based on power consumption to optimize network traffic.

Supported Devices

This integration is designed to support Tuya devices in categories like znjdq, zndb, dlq, tdq, and other similar energy monitoring/protection devices that expose the DPs identified during the development process.
Installation
Manual Installation

    Download the latest release from the GitHub repository.
    Extract the tuya_energy folder from the downloaded ZIP file.
    Copy the tuya_energy folder into your Home Assistant's custom_components directory. Your Home Assistant configuration directory is typically located at /config. The final path should look like this: /config/custom_components/tuya_energy/.
    Restart Home Assistant.

HACS (Home Assistant Community Store) - Planned

Support for HACS is planned for future releases, which will simplify installation and updates.
Configuration

After installation and restarting Home Assistant:

    Go to Settings -> Devices & Services.
    Click on ADD INTEGRATION.
    Search for "Tuya Energy" and select it.
    You will be prompted to enter the following information:
        Name: A friendly name for your device (e.g., "Geladeira Breaker").
        IP Address: The local IP address of your Tuya device.
        Device ID: The Device ID obtained from the Tuya IoT Platform.
        Local Key: The Local Key obtained from the Tuya IoT Platform.
        Protocol Version: Select 3.5 (or 3.3 if your device uses an older protocol).
    Click Submit.

If the connection is successful, your device entities will be automatically created in Home Assistant.
Obtaining Device ID and Local Key

To obtain the Device ID and Local Key, you typically need to use the Tuya IoT Platform. Refer to the official Tuya documentation or community guides for detailed steps on how to extract these credentials for your device.
Troubleshooting

    Connection Failed: Double-check the IP Address, Device ID, Local Key, and Protocol Version. Ensure your Home Assistant instance can reach the device on the local network.
    Entities Not Appearing: Ensure you have restarted Home Assistant after copying the custom component files. Check the Home Assistant logs for any errors related to tuya_energy.
    Reauthentication: If your Local Key changes or the device becomes unreachable, you might need to reauthenticate the integration via the Home Assistant UI.

Development Roadmap (Future Enhancements)

    Alarm Configuration: Decode and expose alarm_set_1 and alarm_set_2 DPs as configurable entities for setting voltage, current, and power protection limits.
    Advanced Diagnostics: Implement more detailed diagnostics for fault codes and device information.
    Dynamic Entity Creation: Enhance the integration to dynamically create entities based on the device's Data Model, making it compatible with a wider range of Tuya energy devices without code changes.
    Translations: Add more language translations.
    Testing: Implement automated tests (pytest) and full type hinting (mypy) for robustness.

Contributing

Contributions are welcome! If you have suggestions, bug reports, or want to contribute code, please open an issue or submit a pull request on the GitHub repository.
License

This project is licensed under the MIT License - see the LICENSE file for details. (Note: LICENSE file not yet created, will be added in future.)

Author: Tiago Santos Version: 1.0.0 Last Updated: June 30, 2026
