import pytest
from xml_to_html import xml_to_html, XmlToHtmlError


def test_simple_element_becomes_html_document():
    html = xml_to_html("<root>hello</root>")
    assert html.startswith("<!DOCTYPE html>")
    assert "<html" in html
    assert "root" in html
    assert "hello" in html


def test_nested_elements_and_attributes():
    xml = '<catalog><book id="1" lang="en">The Hobbit</book></catalog>'
    html = xml_to_html(xml)
    assert "catalog" in html
    assert "book" in html
    assert 'id="1"' in html
    assert "1" in html
    assert "The Hobbit" in html


def test_escapes_special_characters_in_text():
    html = xml_to_html("<n>a&lt;b&amp;c</n>")
    # Parsed text is "a<b&c"; must be escaped in HTML output
    assert "a&lt;b&amp;c" in html
    assert "<script" not in html.lower()


def test_script_like_text_is_escaped_not_executed():
    html = xml_to_html("<code>MsgBox \"hi\"</code>")
    assert "MsgBox" in html
    assert "<script>" not in html.lower()


def test_invalid_xml_raises():
    with pytest.raises(XmlToHtmlError):
        xml_to_html("<root><unclosed>")


def test_empty_input_raises():
    with pytest.raises(XmlToHtmlError):
        xml_to_html("   ")
