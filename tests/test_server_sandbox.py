import json

import server
import sandbox
import pytest
import sandbox_audit


class _CompletedProcess:
    def __init__(self, returncode=0, stdout=b"", stderr=b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_build_docker_command_hardens_sandbox():
    cmd = server.build_docker_command("/tmp/workdir")

    assert cmd[:3] == ["docker", "run", "--rm"]
    assert "--network" in cmd
    assert cmd[cmd.index("--network") + 1] == "none"
    assert "--read-only" in cmd
    assert "--cap-drop" in cmd
    assert cmd[cmd.index("--cap-drop") + 1] == "ALL"
    assert "--security-opt" in cmd
    assert "--pids-limit" in cmd
    assert cmd[cmd.index("--pids-limit") + 1] == "64"
    assert "--user" in cmd
    assert cmd[cmd.index("--user") + 1] == "65534:65534"
    assert "--userns" not in cmd
    assert "--tmpfs" in cmd
    assert "/work:rw,nosuid,nodev,noexec,size=64m" in cmd
    assert "-v" in cmd
    assert cmd[cmd.index("-v") + 1] == "/tmp/workdir:/src:ro"
    assert "cp -R /src/. /work/ && cd /work && sh ./run.sh" in cmd


def test_run_docker_uses_hardened_command(monkeypatch, tmp_path):
    captured = {}

    def fake_run(cmd, capture_output, timeout):
        captured["cmd"] = cmd
        captured["capture_output"] = capture_output
        captured["timeout"] = timeout
        return _CompletedProcess(returncode=0, stdout=b"ok", stderr=b"")

    monkeypatch.setattr(sandbox.subprocess, "run", fake_run)

    result = server.run_docker({"answer.c": "int main(void){return 0;}"}, "echo ok")

    assert result["passed"] is True
    assert captured["capture_output"] is True
    assert captured["timeout"] == 15
    assert "--network" in captured["cmd"]
    assert "--read-only" in captured["cmd"]
    assert "--cap-drop" in captured["cmd"]


def test_build_command_uses_configured_runtime(monkeypatch):
    monkeypatch.setenv("LUX_DOCKER_RUNTIME", "runsc")

    cmd = sandbox.DockerSandbox().build_command("/tmp/workdir")

    assert cmd[3:5] == ["--runtime", "runsc"]


def test_run_rejects_unsafe_and_oversized_inputs():
    runtime = sandbox.DockerSandbox()

    with pytest.raises(ValueError, match="inside the sandbox"):
        runtime.run({"../escape.sh": "echo bad"}, "echo ok")
    with pytest.raises(ValueError, match="too large"):
        runtime.run({"answer.sh": "x" * (sandbox.MAX_FILE_BYTES + 1)}, "echo ok")
    with pytest.raises(ValueError, match="at most"):
        runtime.run({str(index): "x" for index in range(sandbox.MAX_FILES + 1)}, "echo ok")


def test_run_records_audit_event(monkeypatch):
    events = []
    monkeypatch.setattr(sandbox.sandbox_audit, "record_execution", events.append)
    monkeypatch.setattr(sandbox.subprocess, "run", lambda *args, **kwargs: _CompletedProcess())

    result = sandbox.DockerSandbox().run({"answer.sh": "echo ok"}, "echo ok")

    assert result["passed"] is True
    assert len(events) == 1
    assert events[0]["passed"] is True
    assert "source" not in events[0]


def test_audit_logger_writes_jsonl(tmp_path):
    path = tmp_path / "audit.jsonl"

    sandbox_audit.record_execution({"job_id": "job-1", "passed": False}, str(path))

    record = json.loads(path.read_text().strip())
    assert record["job_id"] == "job-1"
    assert record["passed"] is False
    assert "at" in record
