import pathlib, shutil, subprocess, sys
shutil.copy(pathlib.Path(sys.argv[2]) / "hidden_test.py", "hidden_test.py")
run = subprocess.run([sys.executable, "-m", "unittest", "-q", "test_ttl_cache", "hidden_test"],
                     capture_output=True, text=True, timeout=120)
lines = (run.stdout + run.stderr).strip().splitlines()
print("pass" if run.returncode == 0 else (lines[-1] if lines else "fail"))
sys.exit(run.returncode)
