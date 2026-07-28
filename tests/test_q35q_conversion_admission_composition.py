import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
SCRIPT = ROOT / "scripts" / "q35q_conversion_admission.py"
spec = importlib.util.spec_from_file_location("q35q_conversion_admission", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

from q35q_stage import Q35QStageBlock
from q35q_upstream_provenance import ADMITTED_SOURCE_MEMBERS, sha256


def make_wheel(members):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


MEMBERS = {member: member.encode("utf-8") for member in ADMITTED_SOURCE_MEMBERS}
WHEEL = make_wheel(MEMBERS)


def metadata(
    url="https://files.pythonhosted.org/packages/x/transformers-5.13.1-py3-none-any.whl",
):
    return {
        "info": {"version": module.EXPECTED_VERSION},
        "urls": [
            {
                "filename": module.PINNED_UPSTREAM["wheel_name"],
                "packagetype": "bdist_wheel",
                "python_version": "py3",
                "yanked": False,
                "digests": {"sha256": module.PINNED_UPSTREAM["wheel_sha256"]},
                "url": url,
            }
        ],
    }


def test_selects_exact_frozen_wheel():
    assert module._select_pinned_wheel_url(metadata()).endswith(
        module.PINNED_UPSTREAM["wheel_name"]
    )


def test_rejects_duplicate_frozen_wheel_entries():
    payload = metadata()
    payload["urls"].append(dict(payload["urls"][0]))
    with pytest.raises(Q35QStageBlock, match="exactly one frozen wheel"):
        module._select_pinned_wheel_url(payload)


def test_rejects_untrusted_wheel_origin():
    with pytest.raises(Q35QStageBlock, match="admitted HTTPS origin"):
        module._select_pinned_wheel_url(
            metadata("https://example.com/transformers-5.13.1-py3-none-any.whl")
        )


def test_rejects_registry_digest_disagreement():
    payload = metadata()
    payload["urls"][0]["digests"]["sha256"] = "0" * 64
    with pytest.raises(Q35QStageBlock, match="disagrees with the frozen identity"):
        module._select_pinned_wheel_url(payload)


class Response:
    def __init__(self, data, final_url, content_length=None):
        self._stream = io.BytesIO(data)
        self._url = final_url
        self.headers = {}
        if content_length is not None:
            self.headers["Content-Length"] = str(content_length)

    def read(self, size=-1):
        return self._stream.read(size)

    def geturl(self):
        return self._url

    def close(self):
        pass


def test_bounded_fetch_rejects_cross_origin_redirect():
    def opener(_request, timeout):
        assert timeout == 60
        return Response(b"x", "https://example.com/final")

    with pytest.raises(Q35QStageBlock, match="admitted HTTPS origin"):
        module._bounded_fetch(
            module.PYPI_JSON_URL,
            expected_host="pypi.org",
            max_bytes=10,
            opener=opener,
        )


def test_bounded_fetch_rejects_oversize_body_without_content_length():
    def opener(_request, timeout):
        return Response(b"12345", module.PYPI_JSON_URL)

    with pytest.raises(Q35QStageBlock, match="exceeds the size bound"):
        module._bounded_fetch(
            module.PYPI_JSON_URL,
            expected_host="pypi.org",
            max_bytes=4,
            opener=opener,
        )


def test_compose_upstream_binding_uses_verified_wheel_bytes(monkeypatch):
    synthetic_sha = sha256(WHEEL)
    monkeypatch.setitem(module.PINNED_UPSTREAM, "wheel_sha256", synthetic_sha)
    installed = {name: sha256(data) for name, data in MEMBERS.items()}
    upstream, verdict = module._compose_upstream_binding(WHEEL, installed)
    assert upstream == installed
    assert verdict["installed_bound_to_upstream"] is True


def test_compose_upstream_binding_fails_closed_on_installed_mismatch(monkeypatch):
    synthetic_sha = sha256(WHEEL)
    monkeypatch.setitem(module.PINNED_UPSTREAM, "wheel_sha256", synthetic_sha)
    installed = {name: sha256(data) for name, data in MEMBERS.items()}
    installed[ADMITTED_SOURCE_MEMBERS[0]] = sha256(b"tampered")
    _, verdict = module._compose_upstream_binding(WHEEL, installed)
    assert verdict["installed_bound_to_upstream"] is False
    assert verdict["mismatch_count"] == 1


def test_fetch_upstream_wheel_binds_registry_then_file(monkeypatch):
    payload = metadata()
    payload["urls"][0]["digests"]["sha256"] = sha256(WHEEL)
    monkeypatch.setitem(module.PINNED_UPSTREAM, "wheel_sha256", sha256(WHEEL))
    metadata_bytes = json.dumps(payload).encode("utf-8")
    calls = []

    def opener(request, timeout):
        calls.append(request.full_url)
        if request.full_url == module.PYPI_JSON_URL:
            return Response(metadata_bytes, module.PYPI_JSON_URL, len(metadata_bytes))
        return Response(WHEEL, payload["urls"][0]["url"], len(WHEEL))

    downloaded, binding = module._fetch_upstream_wheel(opener=opener)
    assert downloaded == WHEEL
    assert binding == {
        "registry_metadata_bound": True,
        "wheel_filename_bound": True,
        "wheel_sha256_metadata_bound": True,
    }
    assert calls == [module.PYPI_JSON_URL, payload["urls"][0]["url"]]


def test_isolated_environment_drops_python_and_model_overrides(monkeypatch):
    monkeypatch.setenv("PATH", "/bin")
    monkeypatch.setenv("PYTHONPATH", "/attacker")
    monkeypatch.setenv("HF_HOME", "/private")
    environment = module._isolated_environment()
    assert environment["PATH"] == "/bin"
    assert "PYTHONPATH" not in environment
    assert "HF_HOME" not in environment
