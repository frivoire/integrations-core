import subprocess


def test_connections():
    subprocess.run(["docker", "exec", "agent", "status", "--json"], check=True)
    pass
