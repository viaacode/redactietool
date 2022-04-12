#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/services/input_escaping.py
#
#   Escape content for richtext editor so it works with markup instead of html
#   also sanitize html server side. These module methods are used inside the MetaMapping
#   class.
#

import markdown2
from markupsafe import escape


def unescape_tag(content, tag):
    content = content.replace(f'&lt;{tag}&gt;', f'<{tag}>')
    content = content.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
    return content


def secure_unescape(html_content):
    safe_content = str(escape(html_content))
    safe_content = unescape_tag(safe_content, 'p')
    safe_content = unescape_tag(safe_content, 'h2')
    safe_content = unescape_tag(safe_content, 'br')
    safe_content = unescape_tag(safe_content, 'strong')
    safe_content = unescape_tag(safe_content, 'em')
    safe_content = unescape_tag(safe_content, 'u')

    # editor also supports lists
    safe_content = unescape_tag(safe_content, 'ol')
    safe_content = unescape_tag(safe_content, 'ul')
    safe_content = unescape_tag(safe_content, 'li')

    # sanitize a href tags and add target = _blank
    safe_content = safe_content.replace("&lt;a href=&#34;", '<a href="')

    # href tag escaping in case of html edit mode:
    # safe_content = safe_content.replace(
    #     '&#34; target=&#34;_blank&#34;&gt;',
    #     '" target="_blank">'
    # )

    # href tags in markdown mode:
    safe_content = safe_content.replace("&lt;a href=&#34;", '<a href="')
    safe_content = safe_content.replace(
        '&#34;&gt;',
        '" target="_blank">'
    )
    safe_content = safe_content.replace('&lt;/a&gt;', '</a>')

    # allow regular < and > to still work
    safe_content = safe_content.replace("&amp;lt;", "&lt;")
    safe_content = safe_content.replace("&amp;gt;", "&gt;")
    safe_content = safe_content.replace("&lt;br&gt;", "<br>")
    safe_content = safe_content.replace("&amp;", "&")

    return safe_content


def cleanup_markdown(markdown_text):
    markdown_text = markdown_text.replace("&#13;\n", "").replace("\r", "")

    return markdown_text


def markdown_to_html(markdown_content):
    markdown_text = cleanup_markdown(markdown_content)
    html_content = markdown2.markdown(markdown_text)
    html_content = html_content.replace("\n\n", "<br>")
    html_content = html_content.replace("\n", "")

    return secure_unescape(html_content)
