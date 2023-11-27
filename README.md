# setup

1. aarch64アーキテクチャのマシンを用意する(raspberry piなど)
1. [miniforge](https://github.com/conda-forge/miniforge)をインストールする(BSDライセンスのconda環境)
1. 1で用意したマシンにこのリポジトリをクローンする
```bash

```
1. Pythonの依存ライブラリインストール&tfliteファイルダウンロード
```bash
python -m venv venv
. venv/bin/activate
(venv) pip install -r requirements.txt
bash setup.sh
```

# run
```bash
. venv/bin/activate
python main.py
```

