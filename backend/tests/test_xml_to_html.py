import pytest
from xml_to_html import xml_to_html, XmlToHtmlError


def test_catalog_book_matches_expected_table():
    xml = """<catalog>
  <book id="1">The Hobbit</book>
</catalog>"""
    expected = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "    <head>\n"
        "        <meta charset='UTF-8'>\n"
        "        <title>XML To HTML</title>\n"
        "    </head>\n"
        "    <body>\n"
        "        <table border='1'><tr><th>_</th><th>$</th></tr>"
        "<tr><td>The Hobbit</td><td>1</td></tr>"
        "<tr><td>&nbsp;</td><td>&nbsp;</td></tr></table>\n"
        "    </body>\n"
        "</html>"
    )
    assert xml_to_html(xml) == expected


def test_simple_element_becomes_html_document():
    out = xml_to_html("<root>hello</root>")
    assert out.startswith("<!DOCTYPE html>")
    assert "<title>XML To HTML</title>" in out
    assert "<th>_</th>" in out
    assert "<th>$</th>" in out
    assert "<td>hello</td>" in out


def test_nested_elements_and_attributes():
    xml = '<catalog><book id="1" lang="en">The Hobbit</book></catalog>'
    out = xml_to_html(xml)
    assert "<td>The Hobbit</td>" in out
    assert "<td>1 en</td>" in out
    assert "<tr><td>&nbsp;</td><td>&nbsp;</td></tr>" in out


def test_escapes_special_characters_in_text():
    out = xml_to_html("<n>a&lt;b&amp;c</n>")
    assert "a&lt;b&amp;c" in out
    assert "<script" not in out.lower()


def test_script_like_text_is_escaped_not_executed():
    out = xml_to_html("<code>MsgBox \"hi\"</code>")
    assert "MsgBox" in out
    assert "<script>" not in out.lower()


def test_invalid_xml_raises():
    with pytest.raises(XmlToHtmlError):
        xml_to_html("<root><unclosed>")


def test_empty_input_raises():
    with pytest.raises(XmlToHtmlError):
        xml_to_html("   ")
