import os
import requests
from notion2md.exporter.block import StringExporter

def sync():
    token = os.environ["NOTION_TOKEN"]
    database_id = os.environ["NOTION_DATABASE_ID"]
    
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    results = response.json().get("results", [])

    for page in results:
        props = page.get("properties", {})
        
        # 상태 확인
        st_data = props.get("status") or props.get("Status")
        status_name = ""
        if st_data:
            status_obj = st_data.get("status") or st_data.get("select")
            status_name = status_obj.get("name") if status_obj else ""
        
        if status_name != "완료":
            continue

        # 제목 및 날짜 추출
        title_prop = props.get("제목") or props.get("Name")
        title = title_prop["title"][0]["plain_text"]
        
        date_prop = props.get("Date") or props.get("날짜")
        if not date_prop or not date_prop.get("date"): continue
        date = date_prop["date"]["start"]

        # --- notion2md를 사용한 본문 추출 ---
        # StringExporter를 사용하여 페이지 ID를 마크다운 문자열로 변환합니다.
        markdown_content = StringExporter(block_id=page["id"]).export()

        if not os.path.exists("_posts"):
            os.makedirs("_posts")
            
        filename = f"_posts/{date}-{title.replace(' ', '-')}.md"
        
        content = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {date}\n---\n\n"
        content += markdown_content

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Success: {filename}")

if __name__ == "__main__":
    sync()