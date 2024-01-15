from efootprint.builders.hardware.servers_boaviztapi import print_archetypes_and_their_configs, get_cloud_server, \
    on_premise_server_from_config
from efootprint.constants.sources import SourceValue, Sources
from efootprint.constants.units import u

import unittest


class TestBoaviztapiBuilders(unittest.TestCase):
    def test_boaviztapi_builders_get_cloud_server(self):
        print_archetypes_and_their_configs()

        aws_server = get_cloud_server("aws", "m5.xlarge", SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS))

        on_prem_server = on_premise_server_from_config(
            "My server", 2, 24, 6, 16, SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS))
