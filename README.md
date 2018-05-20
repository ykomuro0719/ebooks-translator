# EBooks Translator

---

## Summary
インターネット上の翻訳機能を利用し、電子書籍を翻訳するスクリプトです

## Requirement
* Python 3.6~
* calibre(https://calibre-ebook.com/) ※calibre CLIが利用可能なこと
* OSX

## Supported Format
* epub
* mobi
* pdf

## Setup
* install calibre https://calibre-ebook.com/

```shell
git clone https://github.com/ykomuro0719/ebooks-translator.git
cd ebooks-translator
pip install -r requirements.txt
```

## Usage
```shell
python analize.py
> 変換対象のepubファイルのパスを入力してください:PATH_TO_EPUB
> 出力形式を選択してください
> 0:PDF 1:EPUB 2:MOBI：
```