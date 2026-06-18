# 스트림릿 페이지
import streamlit as st

# 레이아웃(웹 페이지의 생김새)
# 스트림릿 웹 페이지의 '헤더' 역할
st.set_page_config(page_title = '채용공고 자동 크롤링 서비스',
                   layout = 'wide')

st.title('채용 공고 조회 서비스')
st.write('''이 서비스는 사람인과 고용24 페이지에 검색어를 입력하여 자동으로 공고를 크롤링하도록 만든 서비스입니다. 
         크롤링된 내용은 하단의 표에서 확인 가능하며, csv파일로 다운로드 받아 엑셀로 열어보실 수 있습니다.''')

# 공고를 조회할 사이트를 선택
site_select = st.radio('크롤링 할 사이트 검색', ['사람인', '고용24'], horizontal = True)

# with st.sidebar:
#     st.write('사이드 확장')

with st.expander('상세 검색 조건', expanded = True):
    col1, col2 = st.columns(2)

    with col1:
        search_text = st.text_input('검색어 입력', placeholder = '예시) 파이썬, 인공지능 등')

        except_text = st.text_input('제외할 검색어', placeholder = '예시) 빈번한 야간 근무, 잦은 출장 등')

        max_pages = st.number_input('크롤링 페이지 수',
                                    min_value = 1,
                                    max_value = 30)

    with col2:
        if site_select == '사람인':
            # 사람인 사이트에서 '지역'을 의미하는 코드만 분리
            loc_options = {
                "전체": None,
                "서울": "101000",
                "경기": "102000",
                "인천": "108000",
                "부산": "106000",
                "대구": "104000",
                "광주": "103000",
                "대전": "105000"
            }

            selected_location = st.multiselect('지역을 선택하세요',
                                               # 딕셔너리인 loc_options의 '키'만 모아서 리스트로 만듦
                                               list(loc_options.keys()),
                                               default = ['전체'])
            
            # st.write(selected_location)
            # 크롤링 진행할 때 사용하기 위해 문자열 추출
            # selectes_location으로 '서울', '경기', '부산' 등 '지역명'을 추출
            # loc_options는 딕셔너리이므로, loc_options['지역명'] => 값을 내놓음
            # x는 '서울', '경기', '부산' 같은 '지역명'을 의미하고,
            # if 조건문을 붙인 이유는 '지역명'이 없는 '지역'이라면 추가 안 되도록 하기 위함
            locations = [loc_options[x] for x in selected_location if loc_options[x]]


            # 직무 검색
            cat_options = {
                "전체": None,
                "IT개발·데이터": "2",
                "경영·사무": "3",
                "마케팅·홍보": "4",
                "디자인": "9",
                "영업": "5"
            }

            selected_category = st.multiselect('직무를 선택하세요', 
                                               list(cat_options.keys()),
                                               default = ['IT개발·데이터'])
            
            categories = [cat_options[x] for x in selected_category if cat_options[x]]


            # 경력
            career_option = {'전체' : '0', '신입' : '1', '경력' : '2', '신입/경력' : '3'}

            selected_career = st.selectbox('경력을 선택하세요', 
                                           list(career_option.keys()))
            
            career = career_option[selected_career]


            # 학력
            edu_option = {'전체' : '0', '고졸' : '1', '대졸(2, 3년)' : '2', '대졸(4년)' : '3',
                          '석사' : '4', '박사' : '5'}
            
            selected_edu = st.selectbox('학력을 선택하세요', 
                                        list(edu_option.keys()))
            
            edu = edu_option[selected_edu]

        # 고용24의 경우
        else:
            # 지역
            region = st.text_input('지역 코드를 입력하세요', value = '11000', 
                                   help = '지역 코드를 알 수 없는 관계로 서울로 제한')
            
            
            # 직무
            occupation = st.text_input('직종 코드를 입력하세요', value = '024',
                                       help = '직종 코드 제한')
            

            # 경력
            career_options = {"전체": "A", "신입": "N", "경력": "E", "관계없음": "Z"}
            
            career = st.selectbox('경력을 선택하세요', list(career_options.keys()))

            career = career_options[career]


            # 학력
            edu_options = {"전체": "noEdu", "중졸이하": "01,02", "고졸": "03", "대졸(2~3년)": "04", 
                           "대졸(4년)": "05", "석사": "06", "박사": "07", "학력무관": "00"}

            edu = st.selectbox('학력을 선택하세요', list(edu_options.keys()))
            
            edu = edu_options[edu]

            



