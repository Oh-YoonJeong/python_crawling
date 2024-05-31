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

# 파일다운로드 함수
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

try:
    # PostgreSQL 연결
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    print("PostgreSQL database 연결 성공")

    #페이징 별로 목록 조회#
    for i in range(2301,totalPage+1):
        data = [] ;
        listPostResponse =requests.post(f"{listUrl}?page_count={i}&biz_id=acdDB&search_key=1")
        listHtml = listPostResponse.text
        listSoup = BeautifulSoup(listHtml,'html.parser')
        items = listSoup.select('tbody>.odd.gradeX>.t-left>a')
        for item in items :
            #case_no = 24347   # 특정 사건번호 테스트 시 사용
            case_no = item.attrs['href'].split("'")[1]
            #각 사건 번호로 상세 조회 크롤링#
            #상세 조회 html 크롤링#
            detailResponse = requests.get(f"{detailUrl}?case_no={case_no}")
            detailHtml = detailResponse.text
            datailSoup = BeautifulSoup(detailHtml,'html.parser')

            #hidden value#
            biz_id = datailSoup.find("input", {"id": "biz_id"}).get('value')
            accd_no = datailSoup.find("input", {"id": "accd_no"}).get('value')
            menu_id = datailSoup.find("input", {"id": "menu_id"}).get('value')
            start_ymd = datailSoup.find("input", {"id": "start_ymd"}).get('value')
            end_ymd = datailSoup.find("input", {"id": "end_ymd"}).get('value')
            search_key = datailSoup.find("input", {"id": "search_key"}).get('value')
            search_val = datailSoup.find("input", {"id": "search_val"}).get('value')
            page_count = datailSoup.find("input", {"id": "page_count"}).get('value')
            
            # 중복 사건번호 리스트
            skip_case_nos = ['27327', '10397', '24344', '23730', '22583', '19813', '23641', '20186', '15618', '22','130']

            #hidden value로 사진 조회 작업#
            picPayLoad = {
                "biz_id": biz_id,
                "accd_no": accd_no,
                "menu_id": menu_id,
                "start_ymd": start_ymd,
                "end_ymd": end_ymd,
                "search_key": search_key,
                "search_val": search_val,
                "page_count": page_count
            }
            picResponse = requests.post(picUrl,data=picPayLoad)
            picHtml = picResponse.text
            picSoup = BeautifulSoup(picHtml,'html.parser')
            
            # 필요한 데이터 추출 및 값 저장
            # 상세 데이터 추출용 tr태그들만 select
            detailData = datailSoup.select('.contentsRow>.table.table-bordered>tbody>tr>.t-left')
            
            #DB 저장할데이터 추출#
            # 사고명,발생일시,공공/민간구분,기상상태,시설물 종류,사고유형 - 인적사고, 사고유형 - 물적사고,사고분류-공종,사고분류-사고객체,사고분류-작업프로세스,사고경위,사고원인,구체적 사고원인,피해상황-사망자수,피해상황-부상자수,피해상황-피해금액,피해상황-피해내용,재발방지대책,

            #공공민간 구분 = column1
            column1 = detailData[3].text.strip()
            #발생일시 - column2
            column2 = detailData[1].text.strip()
            # 사고명 - column3
            column3 = detailData[0].text.strip()
            #시설물종류_구분1 - column4
            sago_ty= detailData[5].text.split()
            column4 =sago_ty[0]
            #시설물종류_구분2 - column5
            column5 = sago_ty[2]
            #시설물종류_구분3 - column6
            if len(sago_ty) > 5 :
                if '(' in sago_ty[4] : column6 = sago_ty[4].split('(')[0]
                else : column6 = sago_ty[4]
            else : column6=' '
            #날씨 - column7
            weather = detailData[4].select('label')
            column7 = weather[0].text.split()[2]
            #기온 - column8
            column8 = weather[1].text.split()[2][:2]
            #습도 - column9
            column9 = weather[2].text.split()[2][:2]
            #사고유형_인적사고 - column10
            column10= detailData[6].text.strip()
            #사고유형_물적사고 - column11
            column11= detailData[8].text.strip()
            #공종_구분1 - column12, 공종_구분2 - column13
            intermission_ty= detailData[9].text
            if '>' in intermission_ty : 
                spIntermission_ty = intermission_ty.split('>')
                column12 = spIntermission_ty[0].strip()
                column13 = spIntermission_ty[1].strip()
            else  : 
                column12 = " "
                column13 = " "
            print('intermission_ty : ', intermission_ty)
            #사고객체_구분1 - column14, 사고객체_구분2 - column15
            accdTarget_ty = detailData[10].text
            if '>' in accdTarget_ty : 
                spAccdTarget_ty = accdTarget_ty.split('>')
                column14 = spAccdTarget_ty[0].strip()
                column15 = spAccdTarget_ty[1].strip()
            else : 
                column14 = " "
                column15 = " "
            #작업프로세스 - column16
            column16 = detailData[11].text.strip()
            #사고경위 - column17
            column17 =  detailData[14].text.strip()
            #사고원인 - column18
            accd_cause = detailData[15].text.split()
            column18 = ''.join(accd_cause[3:])
            #구체적사고원인 - column19
            column19 = detailData[16].text.strip()
            #사망자수 - column20
            deadCnt = detailData[17].select('.form-inline > div')
            deadCnt_1 = int(deadCnt[0].text.split()[2][:1])
            deadCnt_2 = int(deadCnt[1].text.split()[2][:1])
            column20 = deadCnt_1+deadCnt_2
            #부상자수 - column21
            injuredCnt = detailData[18].select('.form-inline>div')
            injuredCnt_1 = int(injuredCnt[0].text.split()[2][:1])
            injuredCnt_2 = int(injuredCnt[1].text.split()[2][:1])
            column21 = injuredCnt_1+injuredCnt_2
            #피해금액 - column22
            column22 = detailData[19].text.strip()
            #피해내용 - column23
            column23 = detailData[20].text.strip()
            #재발방지대책 - column24
            column24 = detailData[23].text.strip()
            #사진ID - column25
            column25 = accd_no
            #사건번호 - column26
            column26 = case_no

            # PostgreSQL에 텍스트 저장
            insert_query = """
                INSERT INTO com_sago_temp (column1, column2, column3, column4, column5, column6, column7, column8,
                    column9, column10, column11, column12, column13, column14, column15, column16, column17,
                    column18, column19, column20, column21, column22, column23, column24, column25, column26)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            data_to_insert = (column1, column2, column3, column4, column5, column6, column7, column8, column9,
                        column10, column11, column12, column13, column14, column15, column16, column17, column18,
                        column19, column20, column21, column22, column23, column24, column25, column26)
            print("pageNum : ",i ,"\n", "Data to insert:", cur.mogrify(insert_query, data_to_insert).decode("utf-8"))

            # 중복 게시글일 경우 쿼리 실행 스킵
            if case_no not in skip_case_nos:
                cur.execute(insert_query, data_to_insert)

                # 사진 데이터 추출
                picInfo = picSoup.select_one('.contentsRow')
                if picInfo!= None : 
                    pictures = picSoup.select('tbody>tr>td>img')
                    column25 = accd_no #사진 조회 번호
                    pic_count = min(len(pictures), 2)  # 최대 2개까지만 처리

                    if pic_count >= 1:
                        print(f'사진 {len(pictures)}개 있다!')
                        for idx in range(pic_count):
                            print(idx)
                            picture = pictures[idx]
                            pic_src = picture.attrs['src']
                            pic_name = picture.attrs['data-filename']
                            mod_pic_name = f'{column25}_{idx}.{pic_name.split(".")[-1]}'     # 기존 안전톡과 동일하게 (확장자포함)
                            fileUrl = f'{basicUrl}{pic_src}'
                            fileDownPath = "D:\\nes\\safetytalk-web\\home\\awa-safety\\opt\\safetytalk\\safetytalk-upload\\sago"     # 내 로컬
                            filePath = "/home/awa-safety/opt/safetytalk/safetytalk-upload/sago"
                            get_download(fileUrl, mod_pic_name, fileDownPath)

                            img_res = requests.get(fileUrl)
                            fileSize = len(img_res.content)             # 이미지 파일 사이즈 추출
                            fileExt = pic_name.split('.')[-1].lower()   # 이미지 확장자 추출
                            # print(f'Image file size: {fileSize}')
                            # print(f'Image file ext: {fileExt}')

                            # 파일 공통 테이블 데이터 삽입
                            query1 = "INSERT INTO COM_FILE (FILE_ID, REG_USR_ID, REG_DT, UPD_USR_ID, UPD_DT) VALUES (%s, 'SYSTEM', now(), 'SYSTEM', now());"
                            data1 = (column25,)
                            print("Data to com_file insert:", cur.mogrify(query1, data1).decode("utf-8"))
                            if idx == 0:  # idx가 0일 때만 삽입
                                cur.execute(query1, data1)

                            # 파일 디테일 테이블 데이터 삽입
                            query2 = """
                                INSERT INTO COM_FILE_DETL (FILE_ID, FILE_NO, SYS_FILE_PATH, SYS_FILE_NM, USR_FILE_NM, FILE_EXT,
                                    FILE_SIZE, FILE_DOWN_CNT, FILE_UPLOAD_CNT, SORT_SEQ, REG_USR_ID, REG_DT, UPD_USR_ID, UPD_DT, FILE_TYPE_CD)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 0, %s, 'SYSTEM', now(), 'SYSTEM', now(), '04');
                            """
                            data2 = (column25, idx, filePath, f'{column25}_{idx}', pic_name.split(".")[0], fileExt, fileSize, idx)
                            print("Data to com_file insert:", cur.mogrify(query2, data2).decode("utf-8"))
                            cur.execute(query2, data2)
                            
                else :
                    column25 = ''
            
            # print('페이지번호 : ',i,'사건번호 : ',case_no,column1,column2,column3,column4,column5,column6,column7,column8,column9,column10,column11,column12,column13,column14,column15,column16,column17,column18,column19,column20,column21,column22,column23,column24,column25)
            # data.append([column1,column2,column3,column4,column5,column6,column7,column8,column9,column10,column11,column12,column13,column14,column15,column16,column17,column18,column19,column20,column21,column22,column23,column24,column25])
    
    # 커밋
    conn.commit()
    
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
    # 연결 닫기
    if conn:
        cur.close()
        conn.close()
        print("PostgreSQL connection is closed")

print('Crawling and saving completed.')