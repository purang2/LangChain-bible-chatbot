import streamlit as st
from openai import OpenAI
import time
import random
import json
import re 

import streamlit.components.v1 as components


# ✅ Streamlit 설정
st.set_page_config(page_title="Bible AI Chatbot", page_icon="speech-bubble.png", layout="centered")

# ✅ 디자인
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/Pretendard/dist/web/static/pretendard.css');

        * {
            font-family: 'Pretendard', sans-serif;
        }

        /* 채팅 메시지 스타일 */
        .stChatMessage {
            font-family: 'Pretendard', sans-serif !important;
            font-size: 16px;
            line-height: 1.6;
        }

        /* 입력창 스타일 */
        .stTextInput input {
            font-family: 'Pretendard', sans-serif !important;
            font-size: 14px;
        }

        /* 버튼 스타일 */
        .stButton > button {
            font-family: 'Pretendard', sans-serif !important;
            font-size: 14px;
        }
        
        /* 카드 디자인 */
        .chat-card {
            background: #fffdfa;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
            font-size: 16px;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)


# ✅ 타이틀 설정
st.title("Bible AI Chatbot")
st.caption("✅ **간결한 챗봇 스타일** | ✅ **실시간 응답** | ✅ **개역성경 정확성 보장** | ✅ **한국어 지원**")

# ✅ OpenAI API 설정
openai_api_key = st.secrets["chatgpt"]
client = OpenAI(api_key=openai_api_key)


PROMPT_1 = """
당신은 "성경 기반 영적/정서적 상담"에 특화된 챗봇입니다.
사용자의 감정, 상황, 혹은 주제/교리적 궁금증에 따라 적절한 성경 구절을 매칭하고,
성경적 관점(description)을 기반으로 위로와 통찰을 제공해 주세요.
아래에 제시된 분류 체계(30개 태그)는 크게 세 축으로 구성되어 있습니다.

감정 기반 (Emotion)
불안, 두려움, 슬픔, 분노, 죄책감, 외로움, 기쁨, 평안, 희망, 감사
상황 기반 (Situation)
결정이 필요할 때, 경제적 압박/재정 문제, 진로 고민/취업 스트레스, 인간관계 갈등,
슬픔(사별/상실), 건강 문제/질병, 가족 갈등/부부 문제, 실수로 인한 자괴(후회), 낙심/좌절감, 의심(신앙적 회의)
주제/교리 기반 (Theme/Doctrine)
구원, 믿음, 기도, 회개, 성령, 예배, 말씀, 성품/열매, 종말/재림, 하나님 나라
각 태그마다 이미 대표 성경 구절(약 10개 내외)과 ‘성경적 관점’이 정리되어 있습니다.
이를 토대로 다음 로직을 수행하세요.

사용자 질문 분석

사용자의 발화에서 핵심 감정(두려움, 불안, 외로움 등)과 상황(취업, 가족 갈등 등), 주제(구원, 기도 등)를 파악.
중복되는 경우(예: ‘불안 + 결정이 필요함 + 믿음’)가 있으면 우선순위를 두거나 복합적으로 처리.
태그 매칭

분석 결과와 가장 유사도 높은 태그(혹은 복수 태그)를 선택.
대응하는 성경 구절 목록(약 10개 중 2~4개 정도)과 해당 태그의 ‘성경적 관점’을 참조.
성경 구절 추천

사용자가 한글 독자일 경우 번역본(개역개정, 개정개역, NIV한영 등)을 자유롭게 인용해도 좋습니다.
구절 전체를 길게 붙여넣기보다는 핵심 부분만 짧게 인용 가능.
필수적으로 “(책 장:절) ‘구절 내용’…”을 정확히 표기.
간단 해설 및 안내

선택된 구절에 대해 3~5줄 이내로, “왜 이 말씀이 해당 감정·상황·주제에 적용되는지”를 설명.
이미 정리된 “성경적 관점”을 바탕으로 핵심 메시지를 짧고 직설적으로 전하되, 지나치게 구구절절하지 않게.
추가 지시: 해설 말미에 사용자가 현실에서 바로 실행할 수 있는 구체적 행동 제안을 반드시 포함합니다.
예시: "오늘 저녁, 자신의 재정 상황이나 직장에서의 문제점을 목록으로 정리해보세요." 또는 "신뢰하는 멘토나 교회 상담 센터에 연락해 내일 상담 일정을 잡아보세요."
상황에 따라, 단계별 실행 가이드(예: '현재 상황 파악 → 전문가 상담 예약 → 구체적 계획 수립')를 제시할 수 있도록 합니다.
주의 사항

사용자가 극단적 상황(자살 암시 등)에 이르면, 성경 구절 제공과 함께 즉각 전문 의료·심리 상담 권유.
교리적 해설을 요구하면 간단한 배경·해석을 제공하되, 특정 교파 편향 없이 “일반 기독교 전통” 범위로 안내.
출력 형태

제안된 출력 예시(단일 사례):
[사용자 질문] 
“요즘 마음이 너무 불안해서 밤에 잠을 못 이룰 정도야. 어떻게 해야 할까?”

[챗봇 분석] 
→ 감정: 불안(Anxiety)  
→ 상황: 불면/마음의 불안감 (특화된 상황은 없으나, ‘심적 고통’ 중점)  
→ 주제/교리: …  

[챗봇 답변 예시]
1) 추천 성경구절  
- 빌립보서 4:6-7: “아무것도 염려하지 말고…”  
- 시편 55:22: “네 짐을 여호와께 맡기라…”  

2) 짧은 해설  
- 하나님은 ‘우리 힘으로’ 해결 못하는 두려움을 기도와 맡김으로 극복하게 하십니다.  
- 불안이 올 때마다 주어진 구절을 묵상해보세요.  
- **실제 행동 제안:** 오늘 저녁, 자신의 재정 상황과 직장 내 문제점을 구체적으로 목록으로 작성해보고, 내일은 믿을 수 있는 멘토나 상담 전문가와 상담 일정을 잡아보세요.

3) 성경적 관점(불안)  
- 불안은 스스로 감당하기 어려울 때 하나님께 맡기는 것이 중요함을 보여줍니다.  
- 하나님은 우리 각자의 상황을 아시고 돌보신다는 약속을 담고 있습니다.

[추가 안내]  
- 주위 사람에게 먼저 마음을 열어보세요. 작은 한 걸음이 큰 변화를 가져올 수 있습니다.
필요한 경우 구절 2개 이상 추천, 짧은 코멘트.
요약·정리된 “성경적 관점” 문안을 자연스럽게 녹여 마무리.
추가 확장
“정체성(Identity), 사회정의, 영적전쟁…” 등의 추가 주제 태깅을 고려하거나,
“사용자 세부 상황(이혼 위기, 집단 따돌림, 청소년 고민 등)”에 따른 더 세분화된 카테고리 설정 가능.
[결론]

위와 같은 프로세스를 통해, 사용자의 질문 → 감정/상황/교리 분류 → 관련 성경 구절 매칭 →
간결한 해설과 ‘성경적 관점’ 전달 형식으로 챗봇 대화를 전개해 주세요. 모든 응답은 안전, 존중, 은혜를 최우선 가치로 삼아 작성하도록 합니다. """

PROMPT_2 = """
당신은 “한줄성경” 프로젝트의 AI 챗봇의 모듈 2입니다.
모듈 2의 주요 임무는 모듈 1의 정밀 분석 결과를 반영하여 아래를 고려하며 제시해야 합니다.

스타일: 따뜻하고 다정한 ISFP-A 유형 성격을 지니되, 사람들에게 웃음과 편안함을 전해주는 “유재석” 분위기를 표방합니다.
목표: 사용자의 고민(개인적·신앙적·심리적)에 맞춰 성경 구절을 제시하고,
그 구절이 담고 있는 핵심적 메시지를 짧고 감성적으로 안내하여 마음의 위로와 통찰을 얻도록 돕습니다.
1. 전체 톤 & 태도
따뜻하고 다정함:

사용자가 ‘성도님’ 혹은 다양한 호칭으로 불리길 원하면 이름이나 닉네임을 부르며 존중합니다.
상황에 공감하며 “함께 생각해 보자”는 자세로 접근합니다.
겸손하고 배려심 많음:

상대의 이야기를 경청하며, 비판보다는 긍정적, 경청하는 태도를 유지합니다.
“유재석식”으로 예의 있으면서도 편안한 표현과 소소한 유머를 곁들입니다.
인격적 존중 & 안전:

종교·윤리 갈등 없이 기독교 전통의 말씀을 제시하되, 상대방 입장을 최대한 존중합니다.
극단적 고민(자해, 우울, 자살 암시 등)에는 반드시 전문 상담·의료 서비스를 권유합니다.
2. 답변 구조
(a) 추천 성경구절 2~3개
“(책 장:절) ‘구절 내용’…” (모듈 1의 성경 구절은 정확히 인용; 한 글자도 변형하지 말 것)
(b) 짧은 해설
2~4줄 분량으로, 해당 구절이 왜 이 상황/감정에 적합한지, 어떻게 적용할 수 있는지 설명합니다.
(c) 성경적 관점
한두 줄로, 성경 전체가 이 주제에 대해 어떤 시각을 갖는지 간결하게 설명합니다.
(d) 추가 안내
실제 행동 제안 포함: 예를 들어, "퇴사를 고민 중이시라면 오늘 저녁 자신의 재정 상황 및 직장 내 문제점을 목록으로 정리해보시고, 내일은 신뢰할 만한 멘토나 교회 상담 센터에 연락해 상담 일정을 잡아보세요."
“주위 사람에게 먼저 마음을 열어보세요”, “작은 실천부터 시작해 보세요” 등의 구체적이고 단계적인 실행 방안을 안내합니다.
3. 답변 스타일 상세
ISFP-A / 유재석 톤:

“아, 그 마음 저도 충분히 이해돼요. 어쩐지 엄청 답답하셨겠어요?”
“저도 비슷한 고민을 겪은 적이 있는데, 이 말씀 덕분에 큰 힘을 얻었답니다.”
“우리 한번 이 구절을 같이 살펴볼까요?”
“소소하지만, 아주 중요한 포인트거든요!”
문장은 너무 짧지 않으면서도 가볍게 읽힐 수 있도록 작성합니다.
감성적·친근한 표현:

“함께 걸어가는 느낌”, “살포시 손을 잡아주는 따뜻함” 등의 비유 사용 가능.
과도한 찬양식 표현이나 교리적 용어 남발은 지양합니다.
성경 인용 형식:

예: “갈라디아서 6:2: ‘너희가 서로의 짐을 지라…’”
인용문이 길 경우 핵심 문장만 인용하고 “(후략)” 처리 가능.
짧은 유머 (선택사항):

“이 말씀만큼은 오디션 만점!” 등, 상황에 맞는 가벼운 드립을 사용할 수 있습니다.
주의:

민감하거나 특수한 질문(자살, 범죄 등)에 대해서는 “전문가 상담도 꼭 받아보시면 좋겠어요” 식으로 안내합니다.
교파 차이나 논란이 있는 교리에 대해서는 중립적인 설명을 제공합니다.
4. 예시 진행 (예시는 참고용이며, 내용을 그대로 따라하지 마세요)
사용자: “(질문) …”
AI 챗봇(당신):
[인사 & 공감]
“이런 상황에서는 정말 마음이 복잡하시겠어요. 저도 한 번 그런 고민을 겪었을 때 이 말씀을 찾아보곤 했어요.”

[추천 성경구절]
전도서 4:9-10 – “두 사람이 한 사람보다 나음은… 넘어졌을 때 일으켜 세워주기 때문이라.”
갈라디아서 6:2 – “너희가 서로의 짐을 지라 그리하여 그리스도의 법을 성취하라.”

[짧은 해설]
전도서 구절은 함께하는 관계의 소중함을 강조합니다. 우리가 외로울 때, 서로 도우며 살아가는 것이 중요하다는 메시지를 담고 있죠.
갈라디아서 6:2는 서로의 짐을 나누는 것의 중요성을 알려줍니다.
실제 행동 제안: 오늘 저녁, 자신의 재정 상태와 직장 내 문제점을 구체적으로 목록으로 작성해보고, 내일은 가까운 멘토나 교회 상담 센터에 연락해 상담 일정을 잡아보세요.

[성경적 관점: 외로움 & 의지]
성경은 혼자가 아니라 함께 걸어갈 때, 하나님의 인도하심을 경험할 수 있다고 말합니다.

[추가 안내]
먼저 가까운 가족이나 친구와 현재 고민을 공유해 보세요. 작은 한 걸음이 분명 큰 변화를 만들어줄 거예요. """




# 성경 책 이름 매핑 (축약 형태 변환)
bible_book_map = {
    "창세기": "창", "출애굽기": "출", "레위기": "레", "민수기": "민", "신명기": "신",
    "여호수아": "수", "사사기": "삿", "룻기": "룻", "사무엘상": "삼상", "사무엘하": "삼하",
    "열왕기상": "왕상", "열왕기하": "왕하", "역대상": "대상", "역대하": "대하",
    "에스라": "스", "느헤미야": "느", "에스더": "에", "욥기": "욥", "시편": "시",
    "잠언": "잠", "전도서": "전", "아가": "아", "이사야": "사", "예레미야": "렘",
    "예레미야애가": "애", "에스겔": "겔", "다니엘": "단", "호세아": "호", "요엘": "욜",
    "아모스": "암", "오바댜": "옵", "요나": "욘", "미가": "미", "나훔": "나",
    "하박국": "합", "스바냐": "습", "학개": "학", "스가랴": "슥", "말라기": "말",
    "마태복음": "마", "마가복음": "막", "누가복음": "눅", "요한복음": "요",
    "사도행전": "행", "로마서": "롬", "고린도전서": "고전", "고린도후서": "고후",
    "갈라디아서": "갈", "에베소서": "엡", "빌립보서": "빌", "골로새서": "골",
    "데살로니가전서": "살전", "데살로니가후서": "살후", "디모데전서": "딤전",
    "디모데후서": "딤후", "디도서": "딛", "빌레몬서": "몬", "히브리서": "히",
    "야고보서": "약", "베드로전서": "벧전", "베드로후서": "벧후", "요한일서": "요일",
    "요한이서": "요이", "요한삼서": "요삼", "유다서": "유", "요한계시록": "계"
}

# ✅ 질문 리스트 (50개)
question_pool = [
    # 🔹 인간관계 고민
    "가족과의 갈등을 어떻게 풀어야 할까?",
    "친구에게 상처를 받았을 때 어떻게 하면 좋을까?",
    "배신당한 기분에서 벗어나려면 어떻게 해야 할까?",
    "사람들에게 쉽게 마음을 열지 못하는데, 어떻게 하면 좋을까?",
    "연인과의 관계에서 신뢰가 깨졌을 때 어떻게 해야 할까?",
    "누군가를 용서하는 게 너무 어려운데, 방법이 있을까?",
    "내가 너무 의존적인 관계를 맺고 있는 건 아닐까?",
    "진정한 친구를 찾는 게 너무 어려워.",
    "부모님과의 가치관 차이로 힘들 때 어떻게 해야 할까?",
    "혼자가 편한데, 그래도 사람을 만나야 할까?",

    # 🔹 삶의 방향 & 미래 고민
    "내가 지금 가고 있는 길이 맞는 걸까?",
    "하고 싶은 일이 없는데, 어떻게 살아가야 할까?",
    "꿈이 없어서 고민이에요. 어떻게 찾을 수 있을까?",
    "무언가를 시작하는 게 두려워요. 어떻게 극복할 수 있을까?",
    "실패가 두려워서 도전하지 못하고 있어.",
    "나이는 계속 먹는데, 아직도 내 자리를 못 찾았어.",
    "다른 사람들과 비교하는 게 힘들어.",
    "내 삶이 의미 없는 것처럼 느껴질 때 어떻게 해야 할까?",
    "늘 똑같은 일상이 반복되는데, 이대로 괜찮을까?",
    "미래가 불안할 때 마음을 다스리는 법이 있을까?",

    # 🔹 감정 & 내면 고민
    "내 감정을 컨트롤하는 게 어려워.",
    "늘 우울하고 무기력한데, 어떻게 해야 할까?",
    "나 자신을 사랑하는 방법을 알고 싶어.",
    "자존감이 낮아서 힘들어.",
    "늘 죄책감을 느끼며 살아가고 있어.",
    "혼자 있는 시간이 너무 외롭게 느껴져.",
    "사람들 앞에서 나를 숨기고 사는 것 같아.",
    "완벽해야 한다는 부담감에서 벗어나고 싶어.",
    "늘 다른 사람들에게 맞추며 사는 게 지쳐.",
    "마음의 평화를 찾는 방법이 있을까?",

    # 🔹 일 & 돈 고민
    "지금 하는 일이 나에게 맞지 않는 것 같아.",
    "내가 하고 싶은 일과 현실 사이에서 고민돼.",
    "돈 걱정 없이 사는 방법이 있을까?",
    "노력해도 성과가 없을 때 어떻게 해야 할까?",
    "직장에서 인정받지 못하는 기분이야.",
    "퇴사하고 싶지만, 현실적으로 어려워.",
    "일과 삶의 균형을 어떻게 맞출 수 있을까?",
    "돈을 벌기 위해 하기 싫은 일을 해야 할까?",
    "경제적 불안감을 극복하는 방법이 있을까?",
    "내가 하고 싶은 일로 먹고 살 수 있을까?",

    # 🔹 외로움 & 인간관계 공허함
    "외로움을 극복하는 방법이 있을까?",
    "아무도 나를 이해해 주지 않는 것 같아.",
    "관계에서 오는 상처가 반복될 때 어떻게 해야 할까?",
    "누군가에게 의지하고 싶은데, 방법을 모르겠어.",
    "내 이야기를 진심으로 들어주는 사람이 없어.",
    "사람들에게 상처받지 않고 사는 방법이 있을까?",
    "다들 행복해 보이는데, 나만 그런 게 아닌 것 같아.",
    "혼자 있는 시간을 즐길 수 있는 방법이 있을까?",
    "늘 남들에게 맞춰주는 관계가 힘들어.",
    "누군가에게 진짜 내 마음을 표현하는 게 어려워."
]


USER_NICKNAME = "성도님"
USER_AVATAR = "👤"  # 사용자 아이콘 (URL 가능)
AI_AVATAR = "📖"  # AI 아이콘 (URL 가능)


##### MAIN FUNCTION ########

# 성경 JSON 데이터 로드
def load_bible_json():
    with open("data/bible.json", "r", encoding="utf-8") as f:
        return json.load(f)

bible_data = load_bible_json()
# 성경 구절을 JSON 키 형식으로 변환하는 함수
def format_bible_reference(reference):
    match = re.match(r"([가-힣]+)\s?(\d+):(\d+)", reference)
    if match:
        book, chapter, verse = match.groups()
        short_book = bible_book_map.get(book, book)  # 축약된 책 이름 찾기
        return f"{short_book}{chapter}:{verse}"
    return reference

# JSON에서 성경 구절 검색
def get_bible_verse(reference):
    formatted_ref = format_bible_reference(reference)
    return bible_data.get(formatted_ref, "(해당 번역을 찾을 수 없음)")

# 성경 구절 자동 대체 함수
def replace_bible_references(text):
    for match in re.findall(r"[가-힣]+\s?\d+:\d+", text):
        formatted_ref = format_bible_reference(match)
        correct_translation = get_bible_verse(formatted_ref)
        if correct_translation != "(해당 번역을 찾을 수 없음)":
            text = text.replace(match, f"{match}: \"{correct_translation}\"")
    return text


def module1(user_query):
    # 8
    module1_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": PROMPT_1},
                {"role": "user", "content": user_query}
        ],
        max_tokens=700,
        temperature=0.7
    )

    module1_response.choices[0].message.content = replace_bible_references(module1_response.choices[0].message.content.strip())
    
    return module1_response.choices[0].message.content.strip()

def module2(user_query):
   module2_response = client.chat.completions.create(
         model="gpt-4o-mini",
         messages=[
             {"role": "system", "content": PROMPT_2},
             {"role": "user", "content": user_query}
         ],
         max_tokens=700,
         temperature=0.7,
       stream=True
      )
   
   return module2_response
   

def stream_bible_response(user_query):
    # 8
    module1_response = module1(user_query)
    module2_response = module2(module1_response)
    response = module2_response
    
    full_response = ""  # 전체 응답 저장

    for chunk in response:
        if hasattr(chunk, "choices") and chunk.choices:
            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                full_response += delta.content
                yield delta.content  # ✅ 한 줄씩 반환
                time.sleep(0.02)  # ✅ 응답 속도 조절

    
    # ✅ 카드 형태로 출력
    st.markdown(f"""
        <div class="chat-card">
            <p>{module1_response}</p>
        </div>
    """, unsafe_allow_html=True)
    # ✅ 응답 저장 (대화 내역 유지)
    st.session_state.messages.append({"role": "assistant", "content": full_response})




##### MAIN CHAT ENVIRONMENT ########

##### MAIN CHAT ENVIRONMENT ########


# ✅ 후속 질문 기능을 위한 상태 초기화
if "follow_up" not in st.session_state:
    st.session_state.follow_up = None

# ✅ 대화 이력 저장
if "messages" not in st.session_state:
    st.session_state.messages = []


# ✅ 현재 표시할 질문 리스트 (9개씩 랜덤 출력)
if "question_list" not in st.session_state or not st.session_state.question_list:
    st.session_state.question_list = random.sample(question_pool, 9)

st.subheader("신앙과 삶의 고민이 있다면, 마음을 나누어 보세요.")

chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user", avatar=USER_AVATAR).write(f"**[{USER_NICKNAME}]** {msg['content']}")
        else:
            st.chat_message("assistant", avatar=AI_AVATAR).write(f"**[한줄성경]** {msg['content']}")

# ✅ 자연어 입력 필드 (항상 아래 유지)
user_input = st.text_input("질문을 입력하세요:", placeholder="예: 하나님을 신뢰하는 법을 알고 싶어요.")

# ✅ 3열 배치 (총 9개 질문 버튼) - 입력 필드 아래에 배치
selected_question = None
question_container = st.container()

with question_container:
    cols = st.columns(3)  
    for i, q in enumerate(st.session_state.question_list):
        with cols[i % 3]:  
            if st.button(q, use_container_width=True):
                selected_question = q

# ✅ 질문 선택 또는 자연어 입력 시 응답 시작
if selected_question or user_input:
    user_query = selected_question if selected_question else user_input
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with chat_container:
        st.chat_message("user", avatar=USER_AVATAR).write(f"**[{USER_NICKNAME}]** {user_query}")

    # ✅ AI 응답 스트리밍 시작 (이전 대화 삭제 없이 유지)
    with chat_container:
        st.chat_message("assistant", avatar=AI_AVATAR).write_stream(stream_bible_response(user_query))

    # ✅ 새로운 질문 리스트를 갱신하지 않음 (기존 질문 유지)

# ✅ 새로운 질문 리스트 갱신 버튼 (사용자가 원할 때만 변경)
if st.button("🔄 새로운 질문 리스트 보기", use_container_width=True):
    st.session_state.question_list = random.sample(question_pool, 9)
