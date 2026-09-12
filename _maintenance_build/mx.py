"""Chapter helper for the AssetOps course: enforces the 17-section chapter format."""
from common import mod, layer, callout, code, table, grid, steps, qa, quiz, mermaid, depth, adr

ORDER = [
    "What are we learning?",
    "Why is this important?",
    "Where does this fit in the architecture?",
    "Prerequisites",
    "Folder/file changes",
    "Exact commands",
    "Complete code",
    "Explanation of every important line",
    "Expected output",
    "How to test it",
    "Negative test cases",
    "Common mistakes",
    "How to troubleshoot",
    "Production considerations",
    "Security considerations",
    "What we have completed",
    "What comes next",
]

PWR = "<p><b>Windows PowerShell</b> unless stated otherwise. Linux/macOS differences are noted inline.</p>"
PREV = "<p>All previous chapters completed in order. Each chapter builds on the last — do not skip ahead.</p>"

def ch(cid, num, title, tag, d):
    d = dict(d)
    if "What comes next" not in d:
        d["What comes next"] = "<p>Covered in 'What we have completed' above — the handoff names the next chapter explicitly.</p>"
    missing = [s for s in ORDER if s not in d]
    if missing:
        raise ValueError("Chapter %s missing sections: %s" % (cid, missing))
    body = []
    for s in ORDER:
        body.append("<h3>%s</h3>" % s)
        body.append(d[s])
    return mod(cid, num, tag, title, "\n".join(body))

def neg(rows):
    return table(["Negative case", "What you do", "Expected result"], rows)

def std_test(manual, auto="npm test"):
    return "<p><b>Manual:</b> %s</p><p><b>Automated:</b> <code>%s</code></p>" % (manual, auto)

def done(have, nxt):
    return ("<p><b>What should exist now?</b> %s</p>"
            "<p><b>How do I run it?</b> <code>npm start</code> from the project root.</p>"
            "<p><b>What could go wrong?</b> See Common mistakes + How to troubleshoot above.</p>"
            "<p><b>What comes next?</b> %s</p>") % (have, nxt)
