TODO
------------------------

- デジタルコンテンツ専用カート?

  - 複数Line入れる必要なしかも
  - 配送先情報必要なし

- LocationとLanguage

  - Locationは、商品ごとかSellerごとか
  - 商品情報の翻訳をどうするか

- 在庫確保失敗時のリカバリー
- confirm/finishedに直接遷移できるのはどうする?
- USER cookieに住所情報など
- try except
- pure REST ?
- 商品情報変更は在庫数とは別
- 商品基本情報と詳細情報
- 外部URL（商品詳細情報）
- メール送信機能
- INDEXをどうするか

software design
------------------------

key:
  C-${userID}

val:
  {
    ${sellerID1}: {},
    ${sellerID2}: {},
    "BUYER": {
      "mail": "test@example.com",
      "note": "",
      "ship":{
        "country":"",
        "postalcode":"",
        "pref":"",
        "city":"",
        "addr1":"",
        "addr2":"",
    },
  }



