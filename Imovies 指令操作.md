##  Imovies 指令操作

### 在 command line 中輸入 flask << command>>

* 操作爬蟲指令

  > ### flask crawling 
  >
  > * --type -t 指定電影類型 ( popular or top)  **required**
  > * --name -n  輸出檔案名稱 ( 不含附檔名 )  固定輸出 json 檔  **required**
  > * --detail / --no-detail  是否爬取電影詳細資料 ( 類型、名稱、預算等)  預設為 True
  > * --limit -t  爬取多少電影資料  預設為 None
  
* 將資料寫入資料庫

  >### flask  insert
  >
  >* --database  -db  指定要寫入的資料庫 ( popular, top, movies)  **reqiured**
  >* --file  -f  要寫入的資料名稱 ( 不含附檔名 )  只接收 json 格式  **reuired**



