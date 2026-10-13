import json
import os
import subprocess

import pytest

import sandbox
import sandbox_audit
import server


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

    result = server.run_docker(
        {"answer.c": "int main(void){return 0;}"},
        "echo ok",
        puzzle_id="p-101",
    )

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


def test_run_records_audit_event_fields_and_privacy(monkeypatch):
    events = []
    monkeypatch.setattr(sandbox.sandbox_audit, "record_execution", events.append)
    monkeypatch.setattr(
        sandbox.subprocess, "run", lambda *args, **kwargs: _CompletedProcess(returncode=0)
    )

    result = sandbox.DockerSandbox().run(
        {"answer.sh": "secret_solution_code"},
        "secret_script",
        puzzle_id="puzz-99",
    )

    assert result["passed"] is True
    assert len(events) == 1
    event = events[0]
    assert event["job_id"] is not None
    assert event["puzzle_id"] == "puzz-99"
    assert event["passed"] is True
    assert event["result"] == "success"
    assert event["exit_code"] == 0
    assert event["timed_out"] is False
    assert event["docker_failure"] is False
    assert event["duration_ms"] >= 0
    # Ensure raw submitted source / content is never logged
    assert "secret_solution_code" not in str(event)
    assert "secret_script" not in str(event)


def test_run_records_distinct_timeout_and_docker_failure(monkeypatch):
    events = []
    monkeypatch.setattr(sandbox.sandbox_audit, "record_execution", events.append)

    # 1. Timeout
    def fake_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["docker"], timeout=15)

    monkeypatch.setattr(sandbox.subprocess, "run", fake_timeout)
    res_timeout = sandbox.DockerSandbox().run({"f.txt": "a"}, "echo 1", puzzle_id="p-time")
    assert res_timeout["passed"] is False
    assert res_timeout["timed_out"] is True
    assert events[-1]["result"] == "timeout"
    assert events[-1]["timed_out"] is True
    assert events[-1]["docker_failure"] is False

    # 2. Docker daemon / process failure
    def fake_docker_error(*args, **kwargs):
        raise OSError("Docker daemon socket unavailable")

    monkeypatch.setattr(sandbox.subprocess, "run", fake_docker_error)
    res_err = sandbox.DockerSandbox().run({"f.txt": "a"}, "echo 1", puzzle_id="p-dock")
    assert res_err["passed"] is False
    assert res_err["docker_failure"] is True
    assert events[-1]["result"] == "docker_failure"
    assert events[-1]["timed_out"] is False
    assert events[-1]["docker_failure"] is True


def test_run_cleans_up_temp_directories(monkeypatch):
    created_dirs = []
    original_mkdtemp = sandbox.tempfile.mkdtemp

    def tracked_mkdtemp(*args, **kwargs):
        d = original_mkdtemp(*args, **kwargs)
        created_dirs.append(d)
        return d

    monkeypatch.setattr(sandbox.tempfile, "mkdtemp", tracked_mkdtemp)
    monkeypatch.setattr(
        sandbox.subprocess, "run", lambda *args, **kwargs: _CompletedProcess(returncode=0)
    )

    sandbox.DockerSandbox().run({"ok.txt": "data"}, "echo ok")
    assert len(created_dirs) == 1
    assert not os.path.exists(created_dirs[0])


def test_audit_write_failure_is_best_effort(monkeypatch):
    def failing_audit(event):
        raise OSError("disk full")

    monkeypatch.setattr(sandbox.sandbox_audit, "record_execution", failing_audit)
    monkeypatch.setattr(
        sandbox.subprocess, "run", lambda *args, **kwargs: _CompletedProcess(returncode=0)
    )

    # Should not raise exception
    res = sandbox.DockerSandbox().run({"ok.txt": "data"}, "echo ok")
    assert res["passed"] is True


def test_audit_logger_writes_jsonl(tmp_path):
    path = tmp_path / "audit.jsonl"

    sandbox_audit.record_execution({"job_id": "job-1", "passed": False}, str(path))

    record = json.loads(path.read_text().strip())
    assert record["job_id"] == "job-1"
    assert record["passed"] is False
    assert "at" in record
