# server/main.py
from aigen.pipeline import process_actions
from aigen.core.file_handler import FileHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List
import yaml, tempfile, os, io, traceback, contextlib
from fastapi.responses import JSONResponse

# TODO: import your real executor here
# from aigen.core.executor import execute_yaml_path  # or execute_from_steps

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000", "http://127.0.0.1:3000"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunReq(BaseModel):
    yaml_text: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/run")
def run_graph(req: RunReq):
    steps: List[Dict[str, Any]] = yaml.safe_load(req.yaml_text) or []

    # If your executor needs a file path:
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        yaml.safe_dump(steps, f)
        tmp = f.name

    stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            # ---- Call your real executor here ----
            # outputs = execute_yaml_path(tmp)
            instructions = FileHandler.read_yaml(tmp)
            context: Dict = {}
            process_actions(context, instructions)
            outputs = {"count": len(steps)}  # stub so UI works now

        return {
            "ok": True,
            "outputs": outputs,
            "logs": stdout_buf.getvalue(),
            "errors": stderr_buf.getvalue(),
        }
    except Exception as e:
        tb = traceback.format_exc()
        err_payload = {
            "message": str(e),
            "traceback": tb,
            "logs": stdout_buf.getvalue(),
            "stderr": stderr_buf.getvalue(),
        }
        # Return 200 so UI doesn't have to branch on HTTP error vs success
        return JSONResponse(status_code=200, content={"ok": False, "error": err_payload})
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass

class BatchReq(BaseModel):
    yaml_text: str
    var_name: str
    values: List[str]

@app.post("/batch")
def run_batch(req: BatchReq):
    results = []
    logs_all, errs_all = [], []

    for i, val in enumerate(req.values):
        # Just literal replace — works for ${var} or {{var}} if you pass correct var_name
        yaml_text_i = req.yaml_text.replace(f"${{{req.var_name}}}", val)\
                                   .replace(f"{{{{{req.var_name}}}}}", val)

        steps = yaml.safe_load(yaml_text_i) or []
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(steps, f)
            tmp = f.name

        stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                instructions = FileHandler.read_yaml(tmp)
                context: Dict[str, Any] = {}
                process_actions(context, instructions)
            results.append({"index": i, "ok": True, "outputs": context})
        except Exception as e:
            results.append({"index": i, "ok": False, "error": str(e), "traceback": traceback.format_exc()})
        finally:
            logs_all.append(stdout_buf.getvalue())
            errs_all.append(stderr_buf.getvalue())
            try:
                os.remove(tmp)
            except OSError:
                pass

    return {
        "ok": True,
        "results": results,
        "logs": "\n".join(logs_all),
        "errors": "\n".join(errs_all),
    }
