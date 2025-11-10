import subprocess
import os
import logging
from typing import Dict, Any

# Initialize logger
logger = logging.getLogger("docker_build_helper")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(ch)

import os
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def _run_cmd(cmd, cwd=None) -> Dict[str, Any]:
    """Execute shell command and return structured result."""
    logger.info(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        stdout, stderr = result.stdout.strip(), result.stderr.strip()
        if result.returncode == 0:
            logger.info(f"✅ Command succeeded: {stdout[:200]}")  # truncate to avoid log spam
        else:
            logger.error(f"❌ Command failed ({result.returncode}): {stderr[:200]}")
        return {
            "returncode": result.returncode,
            "stdout": stdout,
            "stderr": stderr
        }
    except Exception as e:
        logger.exception("Command execution failed unexpectedly.")
        return {"returncode": 1, "stdout": "", "stderr": str(e)}

def build_and_push_image(
    image_tag: str,
    workspace_path: str,
    dockerfile: str = "Dockerfile"
) -> Dict[str, Any]:
    """
    Builds and pushes Docker image using the provided tag.
    - No retries (single execution).
    - Logs output clearly.
    - Returns clean structured result.
    """
    logs = []
    if not os.path.exists(workspace_path):
        msg = f"❌ Workspace not found: {workspace_path}"
        logger.error(msg)
        return {"success": False, "logs": [msg], "image_tag": image_tag}

    logger.info(f"🚀 Starting build for image: {image_tag}")
    logs.append(f"Building image in workspace: {workspace_path}")

    # --- Build ---
    build_cmd = ["docker", "build", "-f", dockerfile, "-t", image_tag, "."]
    result_build = _run_cmd(build_cmd, cwd=workspace_path)
    logs.append(result_build["stdout"])
    if result_build["returncode"] != 0:
        logs.append(f"❌ Build failed: {result_build['stderr']}")
        return {"success": False, "logs": logs, "image_tag": image_tag}

    logs.append("✅ Build successful. Proceeding to push...")

    # --- Push ---
    push_cmd = ["docker", "push", image_tag]
    result_push = _run_cmd(push_cmd)
    logs.append(result_push["stdout"])
    if result_push["returncode"] != 0:
        logs.append(f"❌ Push failed: {result_push['stderr']}")
        return {"success": False, "logs": logs, "image_tag": image_tag}

    logs.append(f"✅ Successfully pushed image: {image_tag}")
    logger.info(f"🎉 Build & Push completed successfully for {image_tag}")
    return {"success": True, "logs": logs, "image_tag": image_tag}

