import os
import requests

def sync():
    token = os.environ["NOTION_TOKEN"]
    database_id = os.environ["NOTION_DATABASE_ID"]
    
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # 1. API 호출 시도 및 상태 확인
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ API 호출 실패! 상태 코드: {response.status_code}")
        print(f"오류 메시지: {response.text}")
        return

    results = response.json().get("results", [])
    print(f"✅ 노션에서 총 {len(results)}개의 페이지를 발견했습니다.")

    for page in results:
        try:
            props = page.get("properties", {})
            
            # 2. 제목 추출 ('제목' 혹은 'Name' 확인)
            title_prop = props.get("제목") or props.get("Name")
            if not title_prop or not title_prop.get("title"):
                continue
            title = title_prop["title"][0]["plain_text"]
            
            # 3. 상태 체크 (상태 값이 '완료'인지 확인)
            # 노션의 '상태' 속성은 status 혹은 select일 수 있습니다.
            st_data = props.get("status") or props.get("Status")
            if st_data:
                status_obj = st_data.get("status") or st_data.get("select")
                status_name = status_obj.get("name") if status_obj else ""
            else:
                status_name = ""
            
            print(f"🔍 검사 중: '{title}' (상태: {status_name})")

            if status_name != "완료":
                continue

            # 4. 날짜 추출 ('Date' 혹은 '날짜' 확인)
            date_prop = props.get("Date") or props.get("날짜")
            if not date_prop or not date_prop.get("date"):
                print(f"⚠️ '{title}'에 날짜 정보가 없어 건너뜁니다.")
                continue
            date = date_prop["date"]["start"]

            # 5. 파일 생성
            if not os.path.exists("_posts"):
                os.makedirs("_posts")
            
            # 파일 이름 정제 (특수문자 제거)
            safe_title = title.replace(" ", "-").replace("/", "-")
            filename = f"_posts/{date}-{safe_title}.md"
            
            content = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {date}\n---\n\n연동 성공!"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"🚀 파일 생성 성공: {filename}")

        except Exception as e:
            print(f"❌ 페이지 처리 중 에러 발생: {e}")

if __name__ == "__main__":
    sync()