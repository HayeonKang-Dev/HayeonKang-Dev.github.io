import os
import requests
from notion_client import Client
from notion_to_md import NotionToMarkdown

def sync():
    token = os.environ["NOTION_TOKEN"]
    database_id = os.environ["NOTION_DATABASE_ID"]
    
    # 노션 클라이언트와 마크다운 변환기 설정
    notion = Client(auth=token)
    n2m = NotionToMarkdown(notion_client=notion)
    
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
        
        # 상태 확인 (이미지처럼 '완료' 기준)
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

        # --- 핵심: 본문 추출 및 변환 ---
        md_blocks = n2m.page_to_md(page["id"])
        markdown_content = n2m.to_markdown_string(md_blocks)

        if not os.path.exists("_posts"):
            os.makedirs("_posts")
            
        filename = f"_posts/{date}-{title.replace(' ', '-')}.md"
        
        # Jekyll 형식에 맞춰 저장
        content = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {date}\n---\n\n"
        content += markdown_content # 실제 노션 본문 삽입!

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Success: {filename} with content")

if __name__ == "__main__":
    sync()