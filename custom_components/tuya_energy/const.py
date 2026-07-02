DOMAIN = "tuya_energy"
DEFAULT_NAME = "Tuya Energy Device"
DEFAULT_SCAN_INTERVAL = 30
FAST_SCAN_INTERVAL = 1

CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_IP_ADDRESS = "ip_address"
CONF_PROTOCOL_VERSION = "protocol_version"

# DP IDs from the user's device analysis
DP_ID_SWITCH = 1
DP_ID_COUNTDOWN = 9
DP_ID_ENERGY = 17
DP_ID_CURRENT = 18
DP_ID_POWER = 19
DP_ID_VOLTAGE = 20
DP_ID_TEST_BIT = 21
DP_ID_VOLTAGE_COE = 22
DP_ID_ELECTRIC_COE = 23
DP_ID_POWER_COE = 24
DP_ID_ELECTRICITY_COE = 25
DP_ID_FAULT = 26
DP_ID_RELAY_STATUS = 38
DP_ID_LIGHT_MODE = 40
DP_ID_CHILD_LOCK = 41 # User identified this as child_lock, not maintenance_lock
DP_ID_CYCLE_TIME = 42
DP_ID_ALARM_SET_1 = 48
DP_ID_ALARM_SET_2 = 49
DP_ID_ONLINE_STATE = 66

# Tuya device categories to support
TUYA_DEVICE_CATEGORIES = ["znjdq", "zndb", "dlq", "tdq"]

# Scales for sensor values
VOLTAGE_SCALE = 10
POWER_SCALE = 10
CURRENT_SCALE = 1000
ENERGY_SCALE = 1000
