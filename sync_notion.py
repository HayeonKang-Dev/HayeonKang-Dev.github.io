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
    
    # 필터를 빼고 모든 데이터를 가져와서 파이썬에서 거르는 방식
    response = requests.post(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return

    results = response.json().get("results", [])
    print(f"Total pages found in Notion: {len(results)}")

    for page in results:
        try:
            props = page.get("properties", {})
            
            # 1. 상태(status) 확인 - '완료'인 것만 처리
            # 노션의 '상태' 속성은 구조가 복잡하므로 안전하게 추출
            status_obj = props.get("status", {}).get("status") or props.get("status", {}).get("select")
            status_name = status_obj.get("name") if status_obj else ""
            
            if status_name != "완료":
                continue

            # 2. 제목 추출
            title_list = props.get("제목", {}).get("title", [])
            if not title_list: continue
            title = title_list[0]["plain_text"]
            
            # 3. 날짜 추출
            date_obj = props.get("Date", {}).get("date", {})
            if not date_obj: continue
            date = date_obj.get("start")

            if not date: continue

            # 파일 생성 및 저장
            if not os.path.exists("_posts"):
                os.makedirs("_posts")
                
            filename = f"_posts/{date}-{title.replace(' ', '-')}.md"
            content = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {date}\n---\n\n본문 내용 테스트"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Successfully created: {filename}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    sync()