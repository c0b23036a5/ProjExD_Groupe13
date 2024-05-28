# ProjExD_Groupe13

## 概要
前回の授業で作成した鳥無双を改良する。

## 仕様を固めようそう！そう「しよう」（やったこと）
1. ボス　（若林）
    1分に一つ出現。
    おっきい。
    たくさん球を出す。
    敵の出没回数が増えるなどの難易度調整した。

3. アイテム　（田端）
   敵を撃破すると10回に一度敵の場所に星が出没する。
   星を取得すると100点追加される。

4. 音の実装　（山田）
    たまの発射音
    被弾音の追加
    BGMを再生

5. こうかとん残機　（織田）
    被弾するとハートがひとつ減る。
    画面上部にハートを表示
    被弾した時ハートの画像を変更し、被弾したことを表現している。

7. jsonファイルに最高点を記載。ワールドレコードをクラウドにアップロード　（村田）
ゲームオーバー時に最高得点も同時に表示する。
最高点を更新したら誉める。

## How_To_Play
矢印キーで鳥が動きます。
スペースキーで射撃します。
被弾するとHPが減ります３回被弾するとGameOverです
1. L-Shift＋矢印で高速移動します。
2. 左シフトで5連発射
3. R-SHIFTで無敵　スコア50消費
4. cキーでシールド展開　スコア50消費
5. enterキーでグラビティ　スコア200消費

       
## import packs
以下のパッケージを利用しています。

math,os,random,sys,time,pygame,firebase_admin

```
pip install math os random sys time pygame firebase_admin
```


## 面白コーナー
![Untitled](https://github.com/Drkoukichi/ProjExD_Groupe13/assets/78055680/2424b605-cac8-495b-bc84-ffc7c7468cb6)



