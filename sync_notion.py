import os
import requests

# 외부 라이브러리 대신 직접 API를 호출하는 더 강력한 방식입니다.
def sync():
    token = os.environ["NOTION_TOKEN"]
    database_id = os.environ["NOTION_DATABASE_ID"]
    
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    filter_data = {
        "filter": {
            "property": "status",
            "select": {"equals": "Published"}
        }
    }

    response = requests.post(url, headers=headers, json=filter_data)
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return

    results = response.json().get("results", [])

    for page in results:
        try:
            # 제목 추출
            properties = page.get("properties", {})
            title_data = properties.get("title", {}).get("title", [])
            if not title_data: continue
            title = title_data[0]["plain_text"]
            
            # 날짜 추출
            date_data = properties.get("date", {}).get("date", {})
            if not date_data: continue
            date = date_data["start"]

            filename = f"_posts/{date}-{title.replace(' ', '-')}.md"
            content = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {date}\n---\n\n노션 본문 연동 준비 완료!"

            if not os.path.exists("_posts"):
                os.makedirs("_posts")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Successfully created: {filename}")
        except Exception as e:
            print(f"Skipping a page due to error: {e}")

if __name__ == "__main__":
    sync()