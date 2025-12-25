import os
from notion_client import Client

notion = Client(auth=os.environ["NOTION_TOKEN"])
database_id = os.environ["NOTION_DATABASE_ID"]

def sync():
    # .query() 대신 .query(**{"database_id": database_id, ...}) 형태로 호출하거나
    # 최신 라이브러리 구조에 맞춰 아래와 같이 수정합니다.
    results = notion.databases.query(
        database_id=database_id,
        filter={
            "property": "status",
            "select": {
                "equals": "Published"
            }
        }
    )["results"] # .get("results") 대신 ["results"] 사용 권장

    for page in results:
        # 안전한 제목 추출을 위해 리스트 비어있는지 체크 추가
        title_list = page["properties"]["title"]["title"]
        if not title_list:
            continue
            
        title = title_list[0]["plain_text"]
        date_prop = page["properties"]["date"]["date"]
        if not date_prop:
            continue
            
        date = date_prop["start"]
        
        filename = f"_posts/{date}-{title.replace(' ', '-')}.md"
        
        content = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {date}\n---\n\n"
        content += "노션에서 성공적으로 가져온 글입니다!"
        
        # _posts 폴더가 없을 경우를 대비해 생성 로직 추가
        if not os.path.exists("_posts"):
            os.makedirs("_posts")
            
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    sync()