import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib import request
import os
import psycopg2

# PostgreSQL 서버 연결
db_config = {
    'host': '222.234.222.229',
    'database': 'fsms',
    'user': 'fsmsapp',
    'password': 'dkswjsxhr#2022!',
    'port': '15432'  
}

# 변수선언
column1 = column2 = column3 = column4 = column5 = column6 = column7 = column8 = column9 = column10 = ''
column11 = column12 = column13 = column14 = column15 = column16 = column17 = column18 = column19 = ''
column20 = column21 = column22 = column23 = column24 = column25 = ''

#파일다운로드 함수
def get_download(url, fname, directory):
   try:
       os.chdir(directory)
       request.urlretrieve(url, fname)
       print('다운로드 완료\n')
   except HTTPError as e:
       print('error')
       return 

#목록 조회 html 크롤링#
totalPage = 2392
basicUrl = "https://www.csi.go.kr"
listUrl = f"{basicUrl}/acd/acdCaseList.do"    #목록조회url
detailUrl = f"{basicUrl}/acd/acdCaseView.do"  #상세조회url
picUrl = f"{basicUrl}/acd/photoInc.do"        #상세-사진조회url

list_search_param = {}

case_no_list = []

try:
    # PostgreSQL 연결
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    print("PostgreSQL database 연결 성공")

    #페이징 별로 목록 조회#
    for i in range(1801,totalPage+1):
        print("페이지:", i)
        data = [] ;
        listPostResponse =requests.post(f"{listUrl}?page_count={i}&biz_id=acdDB&search_key=1")
        listHtml = listPostResponse.text
        listSoup = BeautifulSoup(listHtml,'html.parser')
        items = listSoup.select('tbody>.odd.gradeX>.t-left>a')
        
        for item in items :
            #case_no = 26275   # 특정 사건번호 테스트 시 사용
            case_no = item.attrs['href'].split("'")[1]
           
            # 중복 사건번호 리스트
            skip_case_nos = ['27327', '10397', '24344', '23730', '22583', '19813', '23641', '20186', '15618', '22','130']
            #skip_case_nos = []

            # 중복 게시글일 경우 쿼리 실행 스킵
            if case_no not in skip_case_nos:
                # 페이지, 사건번호 딕셔너리
                data = {"page": i, "case_no": case_no}
                case_no_list.append(data)

    
    print("크롤링 결과 개수:", len(case_no_list))
    # print("--------------크롤링 결과 시작--------------")
    # print(case_no_list)
    # print("--------------크롤링 결과 끝--------------\n")


    #쿼리 결과와 비교
    # PostgreSQL에 텍스트 저장
    cur.execute("SELECT COLUMN26 FROM COM_SAGO_TEMP;")
    rows = cur.fetchall()

    db_case_no_list = []

    for row in rows :
        db_case_no_list.append(row[0])
    

    for i in range(0, len(db_case_no_list)):
        for case in case_no_list:
            if(db_case_no_list[i] == case["case_no"]):
                case_no_list.remove(case)
                break


    #DB에 없는 case_no만 남음
    print("--------------DB 대조 결과 시작--------------")

    for case in case_no_list:
        print(case)

    print("--------------DB 대조 결과 끝--------------")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
    # 연결 닫기
    if conn:
        cur.close()
        conn.close()
        print("PostgreSQL connection is closed")

print('Crawling and saving completed.')