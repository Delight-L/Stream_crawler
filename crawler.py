# 크롤링을 위한 라이브러리 임포트
# 크롤링 : 인터넷에 있는 정보를 긁어오는 것!
# requests : 인터넷 주소(url)에 html 파일을 요청하는 역할
import requests
# BeautifulSoup : 인터넷 주소로부터 받은 html 파일을 예쁘게 '파싱'하는 역할
from bs4 import BeautifulSoup
# 파싱한 자료를 표로 만드는 역할
import pandas as pd
# re : 정규표현식으로, 문자열을 정제하는 역할
import re
# StringIO : string으로 만들어서 I(Input), O(Output) 하는 라이브러리
from io import StringIO


# buffer(임시 데이터) 상태인 df을 encode한 후 결과를 반환해주는 코드
# 크롤링 결과물이 지금은 내 컴퓨터(로컬)에 있지만, 배포 후에는 클라우드에 존재함
# 따라서 클라우드에서 임시 파일인 buffer를 나의 로컬 컴퓨터로 다운로드 가능한 상태로 변경하는 작업
def download_to_csv(df):
    buffer = StringIO()
    df.to_csv(buffer, index = False)
    return buffer.getvalue().encode('utf-8-sig')


# 검색어, 제외할 검색어, 지역, 직무, 경력, 학력, 페이지 수
# :'자료형' : 들어올 매개변수에 입력될 자료형을 '미리 안내'할 수 있음
# = "", None 등 : 매개변수를 넣지 않았을 때 기본값(디폴트 값) 지정할 수 있음 
# 검색어(search_text)에 기본값을 지정하지 않은 이유는 반드시 넣어야 하는 정보로 지정한 것임

# url, header, parameters => requests.get(주소) 주소로 요청
# soup 객체로 파싱, 가지고 있다가 select(), 


def crawling_saramin(search_text:str,
                     except_text:str = "",
                     region:list = None,
                     category:list = None,
                     career:str = "",
                     education:str = "",
                     max_pages:int = 1):

    # 결과로 반환할 df의 '열 이름'과 '행' 리스트로 만들어 놓기
    columns = ['이름', '위치', '조건1', '조건2', '회사이름', '링크']
    rows = []

    # requests는 '검색할 페이지'에 정보를 '요청'하므로, 정보를 요청하는 웹 페이지를 지정함!
    url = "https://www.saramin.co.kr/zf_user/search"

    # 정보를 요청하는 주체가 누구인지 알려주는 역할
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    }

    # 1페이지부터 ~ max_page

    for page in range(1, max_pages+1):

        # 파라미터 정제 => 여기서 파라미터는 '검색 조건'임
        # '키'는 웹 사이트에서 지정한 '키'
        # '값'은 위에서 지정한 매개변수를 사용함
        parameters = {'searchword' : search_text,
                    'except_read' : except_text,
                    'comp_page' : page}

        # 직무
        if category:
            parameters['cat_mcd'] = category

        # 위치
        if region:
            parameters['loc_mcd'] = region

        # 경력
        if career:
            parameters['career_cd'] = career

        # 학력
        if education:
            parameters['edu_cd'] = education

        try : 

            response = requests.get(url = url,
                                    headers = headers,
                                    params = parameters,    # 조건에 대한 정보
                                    timeout = 15)           # html 정보를 반환해 줄 때까지 기다리는 시간

            # 크롤링 결과를 response로 받고,
            # response 안에 있는 text 파일을 'html.parser'로 파싱
            # 객체 soup를 생성
            soup = BeautifulSoup(response.text, 'html.parser')

            # 내가 필요한 결과의 'id' 전달, 추출
            # soup.select(구분자) : '구분자'를 보유한 모든 내용 추출
            # soup.select_one(구분자) : '구분자'를 보유한 내용 딱 하나 추출
            items = soup.select('div.item_recruit')
            
            for item in items:
                # 직무정보(job_area), 회사정보(corp_area) 가져오기
                job_area = item.select_one('div.area_job')
                corp_area = item.select_one('div.area_corp')

                # 직무정보가 없는 경우
                if not job_area:
                    # continue : 중간에 있는 한 칸의 정보가 없을 때에는 넘어가서 계속해줘~
                    continue

                # 직무정보 get!
                job_title = job_area.select_one('.job_tit').get_text(strip = True)
                condition_area = job_area.select_one('.job_condition')
                spans = condition_area.select('span')

                location = spans[0].get_text(strip = True)
                condition1 = spans[1].get_text(strip = True)

                job_sector = item.select_one('div.job_sector')
                condition2 = job_sector.get_text(strip = True)

                # 회사정보 get!
                cor_name = corp_area.select_one('strong').get_text(strip = True)

                # 링크
                link = job_area.select_one('.job_tit').select_one('.data_layer[href]')
                real_link = 'https://www.saramin.co.kr' + link.get('href')

                rows.append({
                    '이름' : job_title,
                    '위치' : location,
                    '조건1' : condition1,
                    '조건2' : condition2,
                    '회사 이름' : cor_name,
                    '링크' : link
                })

        except Exception as e:
            print(f'에러 발대 {e}')
            break

    df = pd.DataFrame(rows)
    # print(df) 위의 코드에 문제가 있을 시 print 하여 문제 해결

    return df


def crawling_work24(search_text:str,
                    except_text:str = "",
                    region:list = None,
                    category:list = None,
                    career:str = "",
                    education:str = "",
                    max_pages:int = 1):
    
    # 결과로 반환할 df의 '열 이름'과 '행' 리스트로 만들어 놓기
    columns = ['회사이름', '공고문', 
               '급료', '경력', '학력', '주당근무요일', '주당근무시간', '하루근무시간', '위치']
    rows = []
    
    # 1. requests
    url = 'https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }

    parameters = {'srcKeyword' : search_text,
                  'notSrcKeyword' : except_text,
                  'pageIndex' : max_pages,
                  'resultCnt' : 10,
                  'CodeDepth1Info' : region,
                  'occupation' : '024',
                  'careerTypes' :'',
                  'academicGbnoEdu' : ''}

    response = requests.get(url,
                            headers = headers,
                            params = parameters,
                            timeout = 15)


    # 2. soup 파싱
    soup = BeautifulSoup(response.text,
                         'html.parser')


    # 3. 회사 이름, 공고문, 급료, 경력, 학력, 근무 시간, 위치 soup 파싱에서 추출
    items1 = soup.select('div.box_table_group.gap_box08.column')
    items2 = soup.select('td.link.pd24')

    # a => items1(왼쪽 박스)
    # b => items2(오른쪽 박스)
    # zip() : for문 1개로 두 개를 묶어서 돌린다!!
    for a, b in zip(items1, items2):
    
        cells = a.select('div.cell')
        # 회사이름
        corp_name = cells[0].get_text(strip = True)
        # 공고문
        job_title = cells[1].get_text(strip = True)
        
        # 연봉
        money = b.select_one('span.item.b1_sb').get_text(strip = True)
        # 공백이 너무 많다ㅠㅠ
        # re(정규표현식)를 사용해서 공백을 지운다.
        money = re.sub(r'\s+', '', money)

        if b.select_one('ul.emp_info_dtl').has_attr('li'):
            t = ''
            work_time = b.select_one('ul.emp_info_dtl').select_one('li.time')
            
            if len(work_time) > 1:
                for i in range(len(work_time)):
                    t += work_time.select('span')[i].text

            elif len(work_time) == 1:
                t = work_time.select_one('span').text

            else:
                t = ''

            work_time = t

        else:
            work_time = '모름'

        
        link = cells[1].select_one('a').get('href')
        real_link = 'thhps://www.work24.go.kr' + link


        # members = b.select_one('li.member').select('span')
        # # 경력
        # career = members[0].get_text(strip = True)
        # # 학력
        # education = members[1].get_text(strip = True)


        # 위치
        location = b.select_one('ul.emp_info_dtl').select_one('li.seite').get_text(strip = True)
        location = re.sub(r'\s+', '', location)
        print(location)


        rows.append({
            '회사이름' : corp_name,
            '공고문' : job_title,
            '연봉' : money,
            '근무시간' : work_time,
            # '경력' : career,
            # '학력' : education,
            '위치' : location,
            '링크' : real_link
        })

    df = pd.DataFrame(rows)
    # print(df)

    return df


# main과 합치기 전에 위에서 만든 코드가 제대로 작동하는지 확인하기
# if __name__ == '__main__':
#     #crawling_saramin("빅데이터")
#     crawling_work24("AI")

