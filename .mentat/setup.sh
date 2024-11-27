apt update
apt install -y python3-venv
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
pip3 install ruff pytest