git pull
source .venv/bin/activate
python -V
pip -V
python -m pip install -r requirements.txt
python my_ak.py
git add .
git commit -m "更新代码"
git push

