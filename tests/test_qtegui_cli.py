import subprocess, sys, json

def run(args):
    return subprocess.run([sys.executable, "-m", "qtegui"] + args, capture_output=True, text=True)

def test_help():
    r = run(["-h"])
    assert r.returncode == 0
    assert "qtegui" in r.stdout

def test_list_json_shape():
    r = run(["list"])
    assert r.returncode == 0
    # should be valid JSON
    j = json.loads(r.stdout)
    assert isinstance(j, dict)
