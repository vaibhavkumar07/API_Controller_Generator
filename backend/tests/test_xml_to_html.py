import pytest
from xml_to_html import XmlToHtmlError, xml_to_html

BEGINNER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book id="bk101">
        <title>The Great Gatsby</title>
        <author>F. Scott Fitzgerald</author>
    </book>
</bookstore>"""

INTERMEDIATE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<medical_chart>
    <patient_file>
        <name>John Doe</name>
        <vitals>
            <blood_pressure>120/80</blood_pressure>
            <pulse>72</pulse>
        </vitals>
    </patient_file>
</medical_chart>"""

ADVANCED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<logistics_hub branch="Midwest-Central">
    <inventory_ledger>
        <item><sku>SKU-990</sku><name>Heavy Duty Pallets</name><qty>450</qty></item>
        <item><sku>SKU-112</sku><name>Industrial Forklift</name><qty>3</qty></item>
        <item><sku>SKU-405</sku><name>Shrink Wrap Rolls</name><qty>120</qty></item>
    </inventory_ledger>
    <dispatch_console>
        <driver_input type="text" placeholder="Scan Manifest Barcode Number" />
        <action_trigger method="authorizeShipment">Release Freight Carrier</action_trigger>
    </dispatch_console>
</logistics_hub>"""

COMPLEX_XML = """<?xml version="1.0" encoding="UTF-8"?>
<datacenter branch="US-West-SiliconValley">
    <network_management ui-component="tabs">
        <hardware_inventory>
            <router_ledger>
                <device><model>Cisco Nexus 9K</model><status>Active</status><ip>10.0.0.1</ip></device>
                <device><model>Juniper PTX10K</model><status>Pending</status><ip>10.0.0.2</ip></device>
                <device><model>Arista 7060X</model><status>Offline</status><ip>10.0.0.3</ip></device>
            </router_ledger>
        </hardware_inventory>
        <provisioning_console>
            <automated_tasks ui-component="accordion">
                <firewall_policies>
                    <rule_name>Block External ICMP Pings</rule_name>
                    <rule_input type="text" placeholder="Enter target IP Subnet CIDR" />
                    <action_button method="deployFirewallRule">Apply Global Rule</action_button>
                </firewall_policies>
            </automated_tasks>
        </provisioning_console>
    </network_management>
</datacenter>"""


def test_beginner_bookstore_structure():
    out = xml_to_html(BEGINNER_XML)
    assert "BOOKSTORE" in out
    assert "The Great Gatsby" in out
    assert "F. Scott Fitzgerald" in out


def test_intermediate_medical_nested():
    out = xml_to_html(INTERMEDIATE_XML)
    assert "MEDICAL_CHART" in out
    assert "John Doe" in out
    assert "120/80" in out
    assert "72" in out


def test_advanced_logistics_table_and_controls():
    out = xml_to_html(ADVANCED_XML)
    assert "INVENTORY_LEDGER DATA LEDGER" in out
    assert "SKU-990" in out
    assert "Heavy Duty Pallets" in out
    assert 'type="text"' in out
    assert "Scan Manifest Barcode Number" in out
    assert "Release Freight Carrier" in out
    assert 'data-method="authorizeShipment"' in out
    assert "Midwest-Central" in out


def test_complex_tabs_accordion_status_and_table():
    out = xml_to_html(COMPLEX_XML)
    assert "tabs-container" in out
    assert "HARDWARE_INVENTORY" in out
    assert "PROVISIONING_CONSOLE" in out
    assert "accordion-item" in out
    assert "ROUTER_LEDGER DATA LEDGER" in out
    assert "Cisco Nexus 9K" in out
    assert "state-success" in out  # Active
    assert "state-warning" in out  # Pending
    assert "state-danger" in out  # Offline
    assert "Apply Global Rule" in out
    assert "openTab" not in out  # uses addEventListener, not inline openTab
    assert "tab-lnk" in out
    assert "<script>" in out.lower()


def test_escapes_special_characters():
    out = xml_to_html("<n>a&lt;b&amp;c</n>")
    assert "a&lt;b&amp;c" in out


def test_invalid_xml_raises():
    with pytest.raises(XmlToHtmlError):
        xml_to_html("<root><unclosed>")


def test_empty_input_raises():
    with pytest.raises(XmlToHtmlError):
        xml_to_html("   ")
