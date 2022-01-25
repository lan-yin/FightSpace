# FightSpace
My first pygame
main.py為主要遊戲的code
setup.py為將遊戲打包的code
以下紀錄setup.py創建流程：
open terminal
pip3 install py2app #我的系統裡有python2.7和python3，指定安裝在python3
py2applet --make-setup main.py   #在存放main.py的資料夾開啟terminal
terminal return: Wrote setup.py  # 創建setup.py成功
接著修改 setup.py內容（目前只能將所有圖檔音檔一一輸入，應該有更聰明的方法）
發布應用：
python3 setup.py py2app -A

app會出現在dist資料夾裡
