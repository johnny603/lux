import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path, PurePosixPath
from typing import Dict, Optional

import sandbox_audit


MAX_FILES = 16
MAX_FILENAME_BYTES = 255
MAX_FILE_BYTES = 256 * 1024
MAX_SCRIPT_BYTES = 64 * 1024
EXECUTION_TIMEOUT = 15


def _record_audit(event):
    try:
        sandbox_audit.record_execution(event)
    except OSError:
        pass


class DockerSandbox:
    """A small sandbox wrapper that hardens container execution for puzzle validation."""

    def build_command(self, source_dir: str) -> list[str]:
        command = [
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
            "--tmpfs",
            "/work:rw,nosuid,nodev,noexec,size=64m",
            "-v",
            f"{source_dir}:/src:ro",
            "alpine:3.20",
            "sh",
            "-c",
            "cp -R /src/. /work/ && cd /work && sh ./run.sh",
        ]
        runtime = os.getenv("LUX_DOCKER_RUNTIME")
        if runtime:
            command[3:3] = ["--runtime", runtime]
        return command

    @staticmethod
    def _safe_target(workdir: str, filename: str) -> str:
        if not isinstance(filename, str) or not filename:
            raise ValueError("filenames must be non-empty strings")
        if len(filename.encode("utf-8")) > MAX_FILENAME_BYTES:
            raise ValueError("filename is too long")
        path = PurePosixPath(filename)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("filename must stay inside the sandbox")
        root = Path(workdir).resolve()
        target = (root / Path(*path.parts)).resolve()
        if root not in target.parents:
            raise ValueError("filename must stay inside the sandbox")
        return str(target)

    def run(self, files: Dict[str, str], script: str) -> Dict[str, Optional[object]]:
        if not isinstance(files, dict) or len(files) > MAX_FILES:
            raise ValueError(f"at most {MAX_FILES} files are allowed")
        if not isinstance(script, str) or len(script.encode("utf-8")) > MAX_SCRIPT_BYTES:
            raise ValueError("sandbox script is too large")
        workdir = tempfile.mkdtemp(prefix="lux-sandbox-")
        job_id = str(uuid.uuid4())
        started = time.monotonic()
        try:
            for filename, content in files.items():
                target = self._safe_target(workdir, filename)
                if not isinstance(content, str) or len(content.encode("utf-8")) > MAX_FILE_BYTES:
                    raise ValueError("sandbox file is too large")
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "w", encoding="utf-8") as handle:
                    handle.write(content)
            with open(os.path.join(workdir, "run.sh"), "w", encoding="utf-8") as handle:
                handle.write(script)
            cmd = self.build_command(workdir)
            try:
                completed = subprocess.run(cmd, capture_output=True, timeout=EXECUTION_TIMEOUT)
                timed_out = False
            except subprocess.TimeoutExpired as error:
                result = {
                    "passed": False,
                    "exit_code": None,
                    "stdout": (error.stdout or b"").decode("utf-8", errors="ignore"),
                    "stderr": "sandbox execution timed out",
                    "command": cmd,
                    "timed_out": True,
                }
                _record_audit({
                    "job_id": job_id,
                    "runtime": os.getenv("LUX_DOCKER_RUNTIME", "runc"),
                    "duration_ms": round((time.monotonic() - started) * 1000),
                    "exit_code": None,
                    "timed_out": True,
                    "passed": False,
                })
                return result
            stdout = completed.stdout.decode("utf-8", errors="ignore")
            stderr = completed.stderr.decode("utf-8", errors="ignore")
            result = {
                "passed": completed.returncode == 0,
                "exit_code": completed.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "command": cmd,
                "timed_out": timed_out,
            }
            _record_audit({
                "job_id": job_id,
                "runtime": os.getenv("LUX_DOCKER_RUNTIME", "runc"),
                "duration_ms": round((time.monotonic() - started) * 1000),
                "exit_code": completed.returncode,
                "timed_out": timed_out,
                "passed": result["passed"],
            })
            return result
        finally:
            shutil.rmtree(workdir, ignore_errors=True)


_RUNTIME: Optional[DockerSandbox] = None


def get_runtime() -> DockerSandbox:
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = DockerSandbox()
    return _RUNTIME
