import os
import requests
from notion_client import Client

notion = Client(auth=os.environ["NOTION_TOKEN"])
database_id = os.environ["NOTION_DATABASE_ID"]

def sync():
    results = notion.databases.query(
        database_id=database_id,
        filter={"property": "status", "select": {"equals": "Published"}}
    ).get("results")

    for page in results:
        title = page["properties"]["title"]["title"][0]["plain_text"]
        date = page["properties"]["date"]["date"]["start"]
        
        # 파일명 생성: 2023-10-27-제목.md
        filename = f"_posts/{date}-{title.replace(' ', '-')}.md"
        
        # 간단한 마크다운 형식 생성
        content = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {date}\n---\n\n"
        content += "노션에서 가져온 글입니다. (상세 본문 변환 로직 추가 가능)"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    sync()