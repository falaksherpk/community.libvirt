# -*- coding: utf-8 -*-
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import unittest

from lxml import etree

# pylint: disable-next=no-name-in-module,import-error
from ansible_collections.community.libvirt.plugins.modules.virt_pool import (
    PoolElement, xml_from_pool_spec, SUPPORTED_POOL_TYPES)


class TestPoolElement(unittest.TestCase):
    """ Test PoolElement, the typed-params -> XML builder for dir pools.

    These are deliberately plain unit tests with no libvirt connection and
    no AnsibleModule involved -- PoolElement.to_xmlstr() is a pure function
    of its inputs, so it's tested directly (per AGENTS.md: "favor simple,
    short, easily testable functions ... no side effects").
    """

    def test_to_xmlstr_produces_valid_dir_pool_xml(self):
        """ The generated XML matches libvirt's documented dir-pool schema
        (https://libvirt.org/formatstorage.html): a <pool type="dir"> with
        <name> and <target><path> children. """
        element = PoolElement(
            name='vms', pool_type='dir', path='/var/lib/libvirt/images')

        xml_str = element.to_xmlstr()
        parsed = etree.fromstring(xml_str)

        self.assertEqual(parsed.tag, 'pool')
        self.assertEqual(parsed.get('type'), 'dir')
        self.assertEqual(parsed.findtext('name'), 'vms')
        self.assertEqual(
            parsed.findtext('target/path'), '/var/lib/libvirt/images')

    def test_to_xmlstr_roundtrips_different_names_and_paths(self):
        """ Different inputs produce correctly different output -- guards
        against accidentally hardcoding a field. """
        element = PoolElement(
            name='other-pool', pool_type='dir', path='/mnt/other')

        parsed = etree.fromstring(element.to_xmlstr())

        self.assertEqual(parsed.findtext('name'), 'other-pool')
        self.assertEqual(parsed.findtext('target/path'), '/mnt/other')

    def test_to_xmlstr_rejects_unsupported_type(self):
        """ PoolElement is the second line of defence against an
        unsupported pool type reaching XML generation -- argument_spec's
        choices= is the first, this guards direct callers. """
        element = PoolElement(
            name='vms', pool_type='iscsi', path='/unused')

        with self.assertRaises(ValueError):
            element.to_xmlstr()


class TestXmlFromPoolSpec(unittest.TestCase):
    """ Test the module-param -> PoolElement -> XML glue function. """

    def test_builds_xml_from_spec_dict(self):
        """ Mirrors exactly how core() calls this: name from the top-level
        'name' param, type/path from the 'spec' dict param. """
        xml_str = xml_from_pool_spec(
            'vms', {'type': 'dir', 'path': '/var/lib/libvirt/images'})

        parsed = etree.fromstring(xml_str)
        self.assertEqual(parsed.tag, 'pool')
        self.assertEqual(parsed.findtext('name'), 'vms')
        self.assertEqual(
            parsed.findtext('target/path'), '/var/lib/libvirt/images')


class TestSupportedPoolTypes(unittest.TestCase):
    """ Guard against SUPPORTED_POOL_TYPES silently growing without
    to_xmlstr() being updated to actually handle the new type -- this test
    is meant to force a deliberate decision, not to prevent expansion. """

    def test_only_dir_currently_supported(self):
        self.assertEqual(SUPPORTED_POOL_TYPES, ['dir'])


if __name__ == '__main__':
    unittest.main()
