from efootprint.builders.hardware.devices_defaults import default_smartphone, default_laptop, \
    default_box, default_screen
from efootprint.builders.hardware.network_defaults import default_wifi_network, default_mobile_network
from efootprint.builders.hardware.servers_defaults import default_serverless, default_autoscaling, \
    default_onpremise
from efootprint.builders.hardware.storage_defaults import default_ssd, default_hdd

import unittest


class TestDefaultBuilders(unittest.TestCase):
    def test_server_defaults(self):
        serverless = default_serverless("serverless")
        autoscaling = default_autoscaling("autoscaling")
        onpremise = default_onpremise("onpremise")

    def test_storage_defaults(self):
        ssd = default_ssd()
        hdd = default_hdd()

    def test_network_defaults(self):
        wifi = default_wifi_network()
        mobile = default_mobile_network()

    def test_devices_defaults(self):
        smartphone = default_smartphone()
        laptop = default_laptop()
        box = default_box()
        screen = default_screen()
