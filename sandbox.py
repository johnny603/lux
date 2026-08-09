import os
import shutil
import subprocess
import tempfile
from typing import Dict, Optional


class DockerSandbox:
    """A small sandbox wrapper that hardens container execution for puzzle validation."""

    def build_command(self, source_dir: str) -> list[str]:
        return [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            "64",
            "--user",
            "65534:65534",
            "--userns",
            "host",
            "--tmpfs",
            "/work:rw,nosuid,nodev,noexec,size=64m",
            "-v",
            f"{source_dir}:/src:ro",
            "alpine:3.20",
            "sh",
            "-c",
            "cp -R /src/. /work/ && cd /work && sh ./run.sh",
        ]

    def run(self, files: Dict[str, str], script: str) -> Dict[str, Optional[object]]:
        workdir = tempfile.mkdtemp(prefix="lux-sandbox-", dir="/tmp")
        try:
            for filename, content in files.items():
                target = os.path.join(workdir, filename)
                with open(target, "w", encoding="utf-8") as handle:
                    handle.write(content)
            with open(os.path.join(workdir, "run.sh"), "w", encoding="utf-8") as handle:
                handle.write(script)
            cmd = self.build_command(workdir)
            completed = subprocess.run(cmd, capture_output=True, timeout=15)
            stdout = completed.stdout.decode("utf-8", errors="ignore")
            stderr = completed.stderr.decode("utf-8", errors="ignore")
            return {
                "passed": completed.returncode == 0,
                "exit_code": completed.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "command": cmd,
            }
        finally:
            shutil.rmtree(workdir, ignore_errors=True)


_RUNTIME: Optional[DockerSandbox] = None


def get_runtime() -> DockerSandbox:
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = DockerSandbox()
    return _RUNTIME
