arupaka
=======
arupakaは, VODな動画配信システムです.

普通はサーバからしか制御できないストリーミング配信をクライアントからコントロールします.

http://pic.non117.com/U/jr.png

## 動作環境
Windows, Mac OSX, Linux, etc...

[VLC](http://www.videolan.org/vlc/), Python 2.x, Django 1.xが必要.

## 導入
VLCをインストールし, PythonとDjangoを入れて下さい.

## 設定
arupaka/settings.pyを編集します.

* VLC_PATH : VLC本体のファイルパス
* MOVIE_DIR : 配信する動画の入ったディレクトリ
* OPTION : VLCの[起動オプション](http://www.videolan.org/doc/streaming-howto/en/ch04.html). 配信の詳細設定です.
* UPDATE_TIME : 動画一覧を更新する間隔. 単位は秒で.

## 使い方
1. コマンドプロンプトなどのシェルで, manage.pyのあるディレクトリに移動します.
2. $ python manage.py runserver 0.0.0.0:8000 を実行します.
3. ブラウザで, arupakaを起動したコンピュータのアドレスへアクセスします.
  * 例: http://192.168.11.2:8000
4. web UIで任意の動画を選択し, プレイリストに追加します.
5. 再生を開始したら, 同じアドレスへVLCでアクセスします.
  * 例: http://192.168.11.2:8080
6. 一時停止, シークなどの再生制御はweb UIで行います.

## 注意
* Python 2.7, Django 1.4, 1.5でデバッグしてます.
* 動画の再生を開始しないと, VLCのクライアントからアクセスできません.
* arupaka起動してから1年間サーバとして放置すると, VLCプロセスがゾンビになります.
* Windowsで動かす場合, ファイルパスの書き方(¥¥)に注意しないと上手く動きません.

