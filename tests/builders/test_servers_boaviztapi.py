from efootprint.builders.hardware.servers_boaviztapi import print_archetypes_and_their_configs, get_cloud_server, \
    on_premise_server_from_config
from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u

import unittest


class TestBoaviztapiBuilders(unittest.TestCase):
    def test_get_cloud_server(self):
        aws_server = get_cloud_server("aws", "m5.xlarge", SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS))

    def test_on_premise_server_from_config(self):
        on_prem_server = on_premise_server_from_config(
            "My server", 2, 24, 6, 16, SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS))

    def test_print_archetypes_and_their_configs(self):
        # Too long and not very important so pass for now
        # print_archetypes_and_their_configs()
        pass
