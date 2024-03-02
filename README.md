# 対応環境
1. raspberry pi
1. Mac (M1)
  - raspberry piでコードを書くのは非効率であるため、開発環境を選択できるようにしている
  - importで読み込まれるライブラリはrapsberry piと異なる
    - RPi.GPIO -> Mock.GPIO
    - tflite-runtime -> tensowflow-macos, tensorflow-metal(GPU利用)

# ランタイム
Python3.9

# セットアップ方法

## raspberry pi
```shell
python --version # 3.9.x
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Mac (M1)
前提としてconda環境があることとする
```shell
conda create -n cv python=3.9
conda activate cv
conda install -c conda-forge opencv
pip install -r requirements-mac.txt
```

# run
```bash
python app/main.py
```