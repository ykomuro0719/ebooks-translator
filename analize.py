'''
方針
・epubファイルを展開
・textフォルダ以下のhtmlファイルを読み込み
・pタグを抽出して翻訳→置き換え
・全置換え後上書き保存
・fontsフォルダのttfファイルを置き換え
・再ZIP化
'''
from googletrans import Translator
from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import os
import zipfile
import epub
import datetime
import shutil
import re

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
    return True
  except Exception as e:
    print(e)
    return False
  finally:
    shutil.rmtree(temp_dir)
    
# 変換対象のhtmlファイルを抽出
def pickup_html(root_dir):
  files_path = []
  for file in find_all_files(root_dir):
    if os.path.isfile(file) and os.path.splitext(file)[1] == '.html':
      files_path.append(file)
  Parallel(n_jobs=16)([delayed(html_convert)(file_path) for file_path in files_path])


def html_convert(file):
  print(file)
  dest_dir = os.path.dirname(file)
  html_doc=''
  with open(file,'r') as f:
    html_doc=f.read()

  soup = BeautifulSoup(html_doc, 'html.parser')

  for pl in soup.find_all():
    line = pl.string
    if not line == None:
      if not is_valid_url(line):
        pl.string = translate(line)
        print(pl.string)

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

if __name__ == '__main__':
  epub_path = input("変換対象のepubファイルのパスを入力してください：")
  extract_epub(epub_path)