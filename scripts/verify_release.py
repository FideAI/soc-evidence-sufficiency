"""Check the preserved study package, the frontier run files and portable documentation. No network."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
required = ["VERSION", "CITATION.cff", "DATA-DICTIONARY.md", "LICENSING.md",
            "LICENSES/CC-BY-4.0.txt", "RELEASE.md", "CHANGELOG.md"]
for name in required:
    assert (ROOT / name).is_file(), name
version = (ROOT / "VERSION").read_text().strip()
assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-rc\.[0-9]+)?", version), version
citation = (ROOT / "CITATION.cff").read_text()
assert f'version: "{version}"' in citation
assert version in (ROOT / "README.md").read_text()
assert version in (ROOT / "CHANGELOG.md").read_text()
provenance = json.loads((ROOT / "PACKAGE-PROVENANCE.json").read_text())
expected = provenance["files"]
original = provenance["original_files"]
editorial = {"README.md", "publication/INSIGHT.md", "publication/TECHNICAL-PAPER.md", "MANIFEST.json"}
assert set(expected) == set(original)
changed = {name for name in expected if expected[name] != original[name]}
assert changed <= editorial, sorted(changed - editorial)
assert changed == set(provenance["editorial_revision"]["changed_files"])
actual = {str(p.relative_to(ROOT / "study")) for p in (ROOT / "study").rglob("*")
          if p.is_file() and "__pycache__" not in p.parts}
assert actual == set(expected), {"extra": sorted(actual - set(expected)),
                                 "missing": sorted(set(expected) - actual)}
for name, digest in expected.items():
    path = ROOT / "study" / name
    assert path.resolve().is_relative_to(ROOT / "study"), name
    assert not path.is_symlink(), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
frontier = ROOT / "frontier"
fmanifest = json.loads((frontier / "MANIFEST.json").read_text())
assert hashlib.sha256((frontier / "MANIFEST.json").read_bytes()).hexdigest() == provenance["frontier"]["manifest_sha256"]
factual = {str(p.relative_to(frontier)) for p in frontier.rglob("*")
           if p.is_file() and "__pycache__" not in p.parts and p.name != "MANIFEST.json"}
assert factual == set(fmanifest["files"]), {"extra": sorted(factual - set(fmanifest["files"])),
                                            "missing": sorted(set(fmanifest["files"]) - factual)}
assert len(factual) == provenance["frontier"]["files"]
for name, digest in fmanifest["files"].items():
    path = frontier / name
    assert path.resolve().is_relative_to(frontier) and not path.is_symlink(), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
assert fmanifest["preregistration"]["sha256"] == fmanifest["files"]["PROTOCOL.md"]
for path in list(ROOT.glob("*.md")) + list((ROOT / "study").rglob("*.md")) + list(frontier.rglob("*.md")):
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
        parsed = urlparse(target)
        if parsed.scheme or not parsed.path:
            continue
        local = (path.parent / unquote(parsed.path)).resolve()
        assert local.is_relative_to(ROOT), (str(path.relative_to(ROOT)), target)
        assert local.exists(), (str(path.relative_to(ROOT)), target)
print(json.dumps({"passed": True, "verified_package_files": len(expected),
                  "unchanged_original_files": len(expected) - len(changed),
                  "editorial_revision_files": sorted(changed),
                  "verified_frontier_files": len(factual),
                  "local_documentation_links": "valid", "new_inference": False}))
