import io, re
src = io.open("sap-a2a-mcp.svg", encoding="utf-8").read()
i = src.find("<svg")
j = src.rfind("</svg>") + len("</svg>")
svg = src[i:j]
ids = sorted(set(re.findall(r'id="([^"]+)"', svg)), key=len, reverse=True)
for old in ids:
    new = "sapd-" + old
    svg = svg.replace('id="%s"' % old, 'id="%s"' % new)
    svg = svg.replace("url(#%s)" % old, "url(#%s)" % new)
    svg = svg.replace('href="#%s"' % old, 'href="#%s"' % new)
    svg = svg.replace("beginElement('%s')" % old, "beginElement('%s')" % new)
io.open("sap_svg_inline.frag", "w", encoding="utf-8").write(svg)
print("ids prefixed:", len(ids), "frag bytes:", len(svg))
