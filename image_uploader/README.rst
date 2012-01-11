
API仕様
========================

Request
------------------------

1. path: /upload
2. params

  a. world

    A. 1案なら必ず大文字(ユーザに任意に指定させる予定はないから)
    B. 2案なら小文字

  b. group
  c. name
  d. type(拡張子)

    A. 許可される拡張子は以下

      1. jpeg(Content-typeにも使いたいから。jpgは非推奨)
      2. gif
      3. png
      4. html
      5. css

  e. resize

- group-world-nameで一意
- nameに連番をつけるなどで対応させる
- 使用文字種のルール

  - 大文字([A-Z]{1,}[A-Z0-9\-]?)=システム的に付与(数字だけは不可)
  - 小文字([a-z0-9]{1,}[a-z0-9_]?)=ユーザ任意に付与
  - name="somecode-1"だった場合、"somecode"がユーザ任意文字、"-1"をシステム付与文字
  - name="somecode-a1"というのは、ありえない(-以降がシステム文字列だから)
  - name="somecode-A1"というのは、ありえる
  - GROUPで1つのNAMEだけでいい場合、システムが勝手に付与する

    - 例えば、sellerで1つのCSSの場合、/(SELLER)/DESIGN/COMMON.css
    - world=DESIGN, name=COMMON がシステム付与文字列
    - 商品ページHTMLは、/(SELLER)/PRODUCT/(CODE).html

      - 大文字のURLが微妙。。。
      - /PAGE-(SELLER)/(CODE).html

Uploadされるpath
------------------------

- resizeなし

  1. http://(HOST)/(HASH_A)/(HASH_B)/(GROUP)/(WORLD)/(NAME).(TYPE)
  2. http://(WORLD).(HOST)/(HASH_A)/(HASH_B)/(GROUP)/(NAME).(TYPE)

- resizeあり

  1. http://(HOST)/(HASH_A)/(HASH_B)/(GROUP)/(WORLD)/(NAME).(SIZE).(TYPE)
  2. http://(WORLD).(HOST)/(HASH_A)/(HASH_B)/(GROUP)/(NAME).(SIZE).(TYPE)

http://product.static.tanarky.com/ff/ff/seller1/code1.html
http://img.product.static.tanarky.com/ff/ff/seller1/code1-1.300x300.jpeg
http://img.product.static.tanarky.com/ff/ff/seller1/code1-1.300x300.png
http://css.static.tanarky.com/ff/ff/seller1/STYLE.css



セットアップ手順
========================

必要なもの
------------------------

1. dir.conf

  a. data directory root: /var/tanarky/leo
  b. hash seed: tanarky_secret


ln -sf `pwd`/dir_test.conf /etc/tanarky-leo/dir.conf
