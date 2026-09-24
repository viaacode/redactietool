# -*- coding: utf-8 -*-
#
#  tests/test_input_escaping.py
#

from app.services.input_escaping import markdown_to_html


def test_markdown_list_has_no_br_tags():
    markdown = (
        "De inzichten:\n\n"
        "* Literatuur kan je redden.\n"
        "* Kijk elkaar wat vaker in de ogen.\n"
    )

    assert markdown_to_html(markdown) == (
        "<p>De inzichten:</p>"
        "<ul><li>Literatuur kan je redden.</li>"
        "<li>Kijk elkaar wat vaker in de ogen.</li></ul>"
    )


def test_markdown_paragraphs_have_no_br_tags():
    assert markdown_to_html("Eerste\n\nTweede") == "<p>Eerste</p><p>Tweede</p>"
