---
作成日: 2026-09-10
更新日: 2026-09-10
タグ:
  - SQLite
  - SQL
  - データベース
状態: 完了
---

# SQLiteで完全一致する行を抽出して一括削除するSQL

## 概要

SQLiteのテーブルから、指定した値と完全一致する行を検索するSQLと、検索条件をそのまま使って該当行を一括削除するSQLを整理する。

## 結論

1列の完全一致なら `WHERE 列名 = ?` を使う。複数列の値がすべて一致する行なら、各列を `AND` でつなぐ。

```sql
-- 抽出
SELECT *
FROM table_name
WHERE column_a = ?
  AND column_b = ?;

-- 削除（同じ条件の行をすべて削除）
DELETE FROM table_name
WHERE column_a = ?
  AND column_b = ?;
```

削除前に同じ `WHERE` 条件で `SELECT` を実行して対象を確認し、必要ならトランザクション内で削除する。`NULL` は `=` では一致判定できないため、`IS NULL` を使う。

## 詳細

### 1列の値が完全一致する行を抽出する

```sql
SELECT *
FROM users
WHERE email = 'user@example.com';
```

アプリケーションから値を渡す場合は、文字列をSQLへ連結せず、プレースホルダーへバインドする。

```sql
SELECT *
FROM users
WHERE email = ?;
```

`LIKE '%値%'` は部分一致なので、完全一致には使わない。`=` で比較する場合も、前後の空白を自動的に除去するわけではないため、保存値と検索値を意図せず変換しない。

### 複数列がすべて一致する行を抽出する

```sql
SELECT *
FROM products
WHERE product_code = 'A001'
  AND product_name = 'サンプル'
  AND price = 1000;
```

「テーブルの1行全体が完全一致」を条件にする場合は、比較したい列をすべて列挙する。主キーが分かる場合は、誤削除を避けるため主キーで対象を特定する方が安全なことがある。

### 完全一致する行を一括削除する

削除前に対象件数と内容を確認する。

```sql
SELECT COUNT(*) AS target_count
FROM products
WHERE product_code = 'A001'
  AND product_name = 'サンプル'
  AND price = 1000;

SELECT *
FROM products
WHERE product_code = 'A001'
  AND product_name = 'サンプル'
  AND price = 1000;
```

確認後、同じ条件で一括削除する。

```sql
DELETE FROM products
WHERE product_code = 'A001'
  AND product_name = 'サンプル'
  AND price = 1000;
```

`WHERE` 句を省略するとテーブルの全行が削除されるため、完全一致の削除では省略しない。

### 削除を取り消せる形で実行する

```sql
BEGIN TRANSACTION;

DELETE FROM products
WHERE product_code = 'A001'
  AND product_name = 'サンプル'
  AND price = 1000;

-- 対象が正しければ
COMMIT;

-- 間違っていれば、COMMITの代わりに実行
-- ROLLBACK;
```

SQLiteでは `BEGIN` から `COMMIT` または `ROLLBACK` までを明示的なトランザクションにできる。削除結果を確認してから `COMMIT` する運用が安全である。

### `NULL` を含む行を比較する

`NULL` は通常の値ではなく、「不明・値なし」を表すため、次の条件では一致しない。

```sql
-- 不適切
WHERE note = NULL
```

`NULL` と一致させる場合は次のように書く。

```sql
WHERE note IS NULL
```

「値が指定値、かつ別の列がNULL」のように条件が混在する場合は、列ごとに `=` と `IS NULL` を使い分ける。

```sql
WHERE product_code = ?
  AND note IS NULL;
```

### 重複データを抽出する

重複とみなす列を `GROUP BY` に列挙し、`HAVING COUNT(*) > 1` で2行以上あるグループに絞る。主キーや登録日時など、重複判定に含めない列は列挙しない。

```sql
SELECT
    product_code,
    product_name,
    price,
    COUNT(*) AS duplicate_count
FROM products
GROUP BY product_code, product_name, price
HAVING COUNT(*) > 1;
```

重複グループに属する実際の行を一覧する場合は、次のように結合する。`NULL` を含む列を重複判定に使う場合でも、`GROUP BY` では同じグループとして扱われる。

```sql
SELECT p.*
FROM products AS p
JOIN (
    SELECT product_code, product_name, price
    FROM products
    GROUP BY product_code, product_name, price
    HAVING COUNT(*) > 1
) AS d
  ON p.product_code = d.product_code
 AND p.product_name = d.product_name
 AND p.price = d.price;
```

ただし、この結合例は判定列に `NULL` があると通常の `=` では結合できない。`NULL` も同じ値として扱う必要がある場合は、SQLiteの `IS` を使う。

```sql
  ON p.product_code IS d.product_code
 AND p.product_name IS d.product_name
 AND p.price IS d.price
```

### 重複を1件残して余分な行を一括削除する

通常のSQLiteテーブルには `rowid` があるため、`rowid` が最も小さい1件を残し、それ以外を削除できる。ここでは `product_code`、`product_name`、`price` の組み合わせを重複判定のキーとする。

まず削除対象だけを確認する。

```sql
SELECT *
FROM products
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM products
    GROUP BY product_code, product_name, price
);
```

内容が正しいことを確認した後、同じ条件で削除する。

```sql
BEGIN TRANSACTION;

DELETE FROM products
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM products
    GROUP BY product_code, product_name, price
);

-- 削除対象が正しければ
COMMIT;

-- 間違っていれば、COMMITの代わりに実行
-- ROLLBACK;
```

この方法では各重複グループの代表1件を残す。残す行を登録日時などで選びたい場合は、`MIN(rowid)` ではなく、主キーと `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` を使って残す順序を明示する。

`WITHOUT ROWID` テーブルやビューには `rowid` がないため、この方法は使えない。その場合は主キーを使い、SQLiteのウィンドウ関数で削除対象を選ぶ。

## 参考資料

- [SQLite Documentation: SELECT](https://sqlite.org/lang_select.html)
  - 参照日: 2026-09-10
  - `SELECT` が行を問い合わせる文であることと、`WHERE` を含む構文を確認した。
- [SQLite Documentation: DELETE](https://sqlite.org/lang_delete.html)
  - 参照日: 2026-09-10
  - `DELETE FROM` と `WHERE` 条件による削除構文を確認した。
- [SQLite Documentation: SQL Language Expressions](https://sqlite.org/lang_expr.html)
  - 参照日: 2026-09-10
  - 比較演算子、`IS`、`IS NULL`、バインドパラメーターを含む式の構文を確認した。
- [SQLite Documentation: Transactions](https://sqlite.org/lang_transaction.html)
  - 参照日: 2026-09-10
  - `BEGIN`、`COMMIT`、`ROLLBACK` と、削除が書き込みトランザクションであることを確認した。

## 更新履歴

- 2026-09-10: 重複行の抽出と代表1件を残す一括削除を追記
- 2026-09-10: SQLiteの完全一致検索、一括削除、NULL比較、トランザクションを整理した初版を作成
