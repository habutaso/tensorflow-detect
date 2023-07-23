# setup

1. aarch64アーキテクチャのマシンを用意する(raspberry piなど)
1. [miniforge](https://github.com/conda-forge/miniforge)をインストールする(BSDライセンスのconda環境)
1. 1で用意したマシンにこのリポジトリをクローンする
1. conda環境を作成する
```bash
cd detect
conda deactivate  # すでに環境に入っている場合は、deactivateしておく
conda create -n detect --file conda_raspberry_pi.txt
conda activate detect
```
1. Pythonの依存ライブラリインストール&tfliteファイルダウンロード
```bash
bash setup.sh
```

# run
```bash
python main.py
```

# トラブルシュート
## 1. GLIBCXX_3.4.29 not found
```bash
conda install -c conda-forge gxx_linux-64==11.1.0
```
## 2. tflite
tflite==0.4.4では正常に動かず。tflite==0.4.3を使用すること