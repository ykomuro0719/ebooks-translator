'''
方針
・epubファイルを展開
・フォルダ以下のhtmlファイルを読み込み
・文字要素を抽出して翻訳→置き換え
・全置換え後上書き保存
・再ZIP化
'''
from googletrans import Translator
from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import os
import sys
import zipfile
import datetime
import shutil
import re
import calibre

def extract_epub(epub_path):
  if not zipfile.is_zipfile(epub_path):
    print("変換可能なepubファイルではありません")
    return False

  time = datetime.datetime.now().strftime('%Y%m%d_%H%M_%s')
  temp_dir = f'{os.path.basename(os.path.splitext(epub_path)[0])}_{time}'
  
  try:
    os.mkdir(temp_dir)

    book = zipfile.ZipFile(epub_path,'r')
    book.extractall(temp_dir)
    pickup_html(temp_dir)
    dest_name = f'[translated]{os.path.basename(os.path.splitext(epub_path)[0])}'
    shutil.make_archive(dest_name, 'zip', root_dir=temp_dir)
    os.rename(f'{dest_name}.zip',f'{dest_name}.epub')
    print(f'{dest_name}.epub　翻訳が完了しました。')
    return f'{dest_name}.epub'
  except Exception as e:
    print(e)
    return False
  finally:
    shutil.rmtree(temp_dir)
    
# 変換対象のhtmlファイルを抽出
def pickup_html(root_dir):
  files_path = []
  for file in find_all_files(root_dir):
    if os.path.isfile(file) and os.path.splitext(file)[1] in ['.html','.xhtml']:
      files_path.append(file)
  Parallel(n_jobs=64)([delayed(html_convert)(file_path) for file_path in files_path])


def html_convert(file):
  print(file)
  dest_dir = os.path.dirname(file)
  html_doc=''
  with open(file,'r') as f:
    html_doc=f.read()

  soup = BeautifulSoup(html_doc, 'html.parser')

  for pl in soup.find_all():
    try:
      if not pl.text == None:
        if not is_valid_url(pl.text) and not pl.find('img'):
          if pl.string == None:
            pl.string = translate(pl.text)
          else:
            pl.string = translate(pl.string)
          print(pl.string)
    except Exception as e:
      print("翻訳エラー発生。スキップします")

  html_doc = soup.prettify(formatter=None)

  with open(f'{dest_dir}/{os.path.basename(file)}','w') as f:
    f.write(html_doc)
    f.close()

def translate(text):
  translator = Translator()
  result = translator.translate(text, dest='ja')
  return result.text

def is_valid_url(url):
    regex1 = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    regex2 = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url is not None and regex1.search(url) or regex2.search(url)

def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)

def setup(src,dest_ext):
  src_ext = os.path.splitext(src)[1]
  src_base = os.path.splitext(src)[0]

  if src_ext == '.epub' and dest_ext == '.epub':
    extract_epub(src)

  elif src_ext == '.epub' and dest_ext != '.epub':
    translated = extract_epub(src)
    translated_base = os.path.splitext(translated)[0]
    calibre.convert_frm_epub(translated,f'{translated_base}{dest_ext}')

  elif src_ext != '.epub' and dest_ext == '.epub':
    converted = calibre.convert2epub(src,f'{src_base}.epub')
    extract_epub(converted)

  elif src_ext != '.epub' and dest_ext != '.epub':
    converted = calibre.convert2epub(src,f'{src_base}.epub')
    translated = extract_epub(converted)
    translated_base = os.path.splitext(translated)[0]
    calibre.convert_frm_epub(translated,f'{translated_base}{dest_ext}')

  return None

if __name__ == '__main__':
  argvs = sys.argv
  if len(argvs) == 1:
    src_path = input("変換対象のファイルのパスを入力してください：")
    print("出力形式を選択してください")
    ext_no = input("0:PDF 1:EPUB 2:MOBI：")
    if not int(ext_no) in [0,1,2]:
      print("適切な入力でありません")
      exit()
    else:
      ext = ['.pdf','.epub','.mobi']
      setup(src_path,ext[int(ext_no)])

  else:
    for arg in argvs:
      ext = os.path.splitext(arg)[0]
      if ext in ['.pdf','.epub','.mobi']:
        setup(arg,ext)
      else:
        print("適切な入力でありません")
        exit()