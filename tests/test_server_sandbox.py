import server
import sandbox


class _CompletedProcess:
    def __init__(self, returncode=0, stdout=b"", stderr=b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_build_docker_command_hardens_sandbox():
    cmd = server.build_docker_command("/tmp/workdir")

    assert cmd[:3] == ["docker", "run", "--rm"]
    assert "--network" in cmd and cmd[cmd.index("--network") + 1] == "none"
    assert "--read-only" in cmd
    assert "--cap-drop" in cmd and cmd[cmd.index("--cap-drop") + 1] == "ALL"
    assert "--security-opt" in cmd
    assert "--pids-limit" in cmd and cmd[cmd.index("--pids-limit") + 1] == "64"
    assert "--user" in cmd and cmd[cmd.index("--user") + 1] == "65534:65534"
    assert "--userns" in cmd
    assert "--tmpfs" in cmd
    assert "/work:rw,nosuid,nodev,noexec,size=64m" in cmd
    assert "-v" in cmd and cmd[cmd.index("-v") + 1] == "/tmp/workdir:/src:ro"
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
