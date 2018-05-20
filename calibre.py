'''
方針
Calibreを使い、PDF→EPUBへ変換するモジュールを作成
EPUB→PDFを作成

'''
import os
import subprocess

CALIBRE_PATH='/Applications/calibre.app/Contents/console.app/Contents/MacOS/'

def convert2epub(src_file,dest_file=None):
  dest_file = f'{os.path.splitext(src_file)[0]}_tmp.epub' if not dest_file else dest_file
  command = [f'{CALIBRE_PATH}/ebook-convert', src_file,dest_file]
  result = subprocess.run(command)
  if not result.returncode == 0:
    raise subprocess.CalledProcessError
  print("変換が完了しました")
  return dest_file

def convert_frm_epub(src_file,dest_file):
  if os.path.splitext(src_file)[1] == os.path.splitext(dest_file)[1]:
    print("変換後の拡張子が同じです")
    return None

  command = [f'{CALIBRE_PATH}/ebook-convert', src_file,dest_file]
  result = subprocess.run(command)
  if not result.returncode == 0:
    raise subprocess.CalledProcessError
  print("変換が完了しました")
  return dest_file
