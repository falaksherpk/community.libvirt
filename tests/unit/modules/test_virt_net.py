# -*- coding: utf-8 -*-
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import unittest

from lxml import etree

# pylint: disable-next=no-name-in-module,import-error
from ansible_collections.community.libvirt.plugins.modules.virt_net import (
    DhcpHostElement, xml_from_dhcp_host_spec)


class TestDhcpHostElement(unittest.TestCase):
    """ Test DhcpHostElement, the typed-params -> XML fragment builder for
    virt_net's 'modify' command.

    Deliberately plain unit tests with no libvirt connection and no
    AnsibleModule involved -- to_xmlstr() is a pure function of its inputs
    (per AGENTS.md: "favor simple, short, easily testable functions ...
    no side effects"). Mirrors tests/unit/modules/test_virt_pool.py.
    """

    def test_to_xmlstr_with_name(self):
        """ Matches the exact <host mac='...' name='...' ip='.../> shape
        the module's own EXAMPLES block hand-writes. """
        element = DhcpHostElement(
            mac='FC:C2:33:00:6c:3c', ip='192.168.122.30', name='my_vm')

        parsed = etree.fromstring(element.to_xmlstr())

        self.assertEqual(parsed.tag, 'host')
        self.assertEqual(parsed.get('mac'), 'FC:C2:33:00:6c:3c')
        self.assertEqual(parsed.get('ip'), '192.168.122.30')
        self.assertEqual(parsed.get('name'), 'my_vm')

    def test_to_xmlstr_without_name_omits_name_attribute(self):
        """ 'name' is optional on a DHCP host reservation -- the generated
        fragment must not include a name="None" or name="" attribute when
        it wasn't supplied. """
        element = DhcpHostElement(mac='AA:BB:CC:DD:EE:FF', ip='192.168.122.99')

        parsed = etree.fromstring(element.to_xmlstr())

        self.assertEqual(parsed.tag, 'host')
        self.assertIsNone(parsed.get('name'))

    def test_to_xmlstr_different_inputs_produce_different_output(self):
        """ Guards against accidentally hardcoding a field. """
        element = DhcpHostElement(
            mac='11:22:33:44:55:66', ip='10.0.0.5', name='other-host')

        parsed = etree.fromstring(element.to_xmlstr())

        self.assertEqual(parsed.get('mac'), '11:22:33:44:55:66')
        self.assertEqual(parsed.get('ip'), '10.0.0.5')
        self.assertEqual(parsed.get('name'), 'other-host')


class TestXmlFromDhcpHostSpec(unittest.TestCase):
    """ Test the module-param -> DhcpHostElement -> XML glue function. """

    def test_builds_xml_from_dhcp_host_dict_with_name(self):
        xml_str = xml_from_dhcp_host_spec(
            {'mac': 'FC:C2:33:00:6c:3c', 'ip': '192.168.122.30', 'name': 'my_vm'})

        parsed = etree.fromstring(xml_str)
        self.assertEqual(parsed.tag, 'host')
        self.assertEqual(parsed.get('mac'), 'FC:C2:33:00:6c:3c')
        self.assertEqual(parsed.get('ip'), '192.168.122.30')
        self.assertEqual(parsed.get('name'), 'my_vm')

    def test_builds_xml_from_dhcp_host_dict_without_name(self):
        """ 'name' is not required in the suboptions -- mirrors that via
        .get('name') rather than ['name'] in the glue function. """
        xml_str = xml_from_dhcp_host_spec(
            {'mac': 'AA:BB:CC:DD:EE:FF', 'ip': '192.168.122.99'})

        parsed = etree.fromstring(xml_str)
        self.assertIsNone(parsed.get('name'))


if __name__ == '__main__':
    unittest.main()
