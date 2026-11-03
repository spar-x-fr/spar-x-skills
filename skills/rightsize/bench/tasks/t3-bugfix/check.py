import pathlib, shutil, subprocess, sys
shutil.copy(pathlib.Path(sys.argv[2]) / "hidden_test.py", "hidden_test.py")
run = subprocess.run([sys.executable, "-m", "unittest", "-q", "test_durations", "hidden_test"], capture_output=True, text=True)
print("pass" if run.returncode == 0 else run.stderr.strip().splitlines()[-1]); sys.exit(run.returncode)
