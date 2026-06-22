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

    # 파라미터 정제 => 여기서 파라미터는 '검색 조건'임
    # '키'는 웹 사이트에서 지정한 '키'
    # '값'은 위에서 지정한 매개변수를 사용함
    parameters = {'searchword' : search_text,
                  'except_read' : except_text,
                  'comp_page' : max_pages}

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

    df = pd.DataFrame(rows)
    print(df)

    return '사람인 결과'

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


    # 3. 회사 이름, 공고문 soup 파싱에서 추출
    items1 = soup.select('td.al_left.pd24')
    # print(items)
    
    for item in items1:
    
        cells = item.select('div.cell')
        # 회사이름
        corp_name = cells[0].get_text(strip = True)
        # 공고문
        job_title = cells[1].get_text(strip = True)


        rows.append({
            '회사이름' : corp_name,
            '공고문' : job_title
        })


    # 4. 급료, 경력, 학력, 근무 시간, 위치 soup 파싱에서 추출
    items2 = soup.select('div.flex1')

    for item in items2:
        
        # 급료
        salary = item.select_one('span.item.b1_sb').get_text(strip = True)


        members = item.select_one('li.member').select('span')
        # 경력
        career = members[0].get_text(strip = True)
        # 학력
        education = members[1].get_text(strip = True)


        times = item.select_one('li.time').select('span')
        # 주당근무요일
        days_time = times[0].get_text(strip = True)
        # 주당근무시간
        week_time = times[1].get_text(strip = True)
        # 하루근무시간
        work_time = times[2].get_text(strip = True)


        # 하루근무시간이 없는 경우
        if not work_time:
            # continue : 중간에 있는 한 칸의 정보가 없을 때에는 넘어가서 계속해줘~
            continue


        # 위치
        location = item.select_one('li.site').get_text(strip = True)


        rows.append({
            '급료' : salary,
            '경력' : career,
            '학력' : education,
            '주당근무요일' : days_time,
            '주당근무시간' : week_time,
            '하루근무시간' : work_time,
            '위치' : location
        })

    df = pd.DataFrame(rows)
    print(df)

    return '고용24 결과'


# main과 합치기 전에 위에서 만든 코드가 제대로 작동하는지 확인하기
if __name__ == '__main__':
    #crawling_saramin("빅데이터")
    crawling_work24("AI")

