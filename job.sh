cd /Users/zhengu/trade/em_data
git pull
source .venv/bin/activate
python -V
pip -V
pip install -r requirements.txt
proxyoff
python my_ak.py
git add .
git commit -m "更新代码"
git push

# 添加定时任务，每天17点执行job.sh
(crontab -l 2>/dev/null; echo "0 17 * * * source $(pwd)/job.sh >> $(pwd)/em_data.log 2>&1 ") | crontab -
