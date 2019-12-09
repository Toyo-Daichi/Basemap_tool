# 用意するデータ

*  全球数値予報モデルGPV

[京都大学生存圏研究所（RISH: Research Institute for Sustainable Humanosphere）](http://database.rish.kyoto-u.ac.jp/arch/jmadata/gpv-original.html)から取得することができます。詳しい格子情報や配信時間等は[気象行支援センター](http://database.rish.kyoto-u.ac.jp/arch/jmadata/gpv-original.html)をご覧ください。


※上記のサイトご利用時は、下記の点にご注意お願いいたします。

>教育研究機関向けにデータを提供しています。企業活動等のためにデータを頻繁に必要とされる方は、気象業務支援センターからデータを直接購入し、データ提供スキーム全体の維持発展にご協力ください。（サイトより引用）

今回使用するデータは上記のサイトで入手したデータをwgirb2を用いて東西風・南北風・鉛直風・気温・高度場のデータをbinary形式で切り出しています。

切り出したデータフォーマットをFortran90で記述しました。

```fortran:format.f90
integer, parameter :: nx = 720, ny = 361, np = 12
integer, parameter :: elem = 5

real(4)            :: gpv(elem, hgt, nx, ny)
real(4)            :: pr(hgt)

character(4)       :: elem_list(elem)

data pr / 1000., 925., 850., 700., 600., 500., 400., 300., 250., 200., 150., 100. /
data elem_list / "U   ", "V   ", "W   ", "T   ", "Z   " /

open(*, fille=*, form='unformatted', access='direct', recl=4*nx*ny*np*elem)
close(*)
```

* 台風の位置表(csv形式)

[気象庁](https://www.data.jma.go.jp/fcd/yoho/typhoon/position_table/index.html)から年度別で取得することができます。
台風発生時から温帯低気圧になるまでの情報が6時間間隔で記載されています。

# コード説明
*  weather_bin2plot.py

気象要素(東西風・南北風・鉛直風・気温・高度場)を記述するコード。

*  typhoon_csv2plot.py

気象庁から入手した台風の進路経路情報をヘキサグリッドで描画する。また特定の台風番号を記述すると、その台風の経路を記述します。

※より細かい説明はこちらのサイトで紹介しております。
https://qiita.com/Toyo_Daichi/private/0baab03f77984699d714
