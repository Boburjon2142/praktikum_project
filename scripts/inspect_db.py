import sqlite3

def main():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    # List categories
    try:
        cur.execute("SELECT id, name FROM news_app_category ORDER BY id")
        categories = cur.fetchall()
        print("Categories:")
        for cid, name in categories:
            print(f" - {cid}: {name}")
    except Exception as e:
        print("Error reading categories:", e)

    # Count published news per category name
    try:
        cur.execute(
            """
            SELECT c.name, COUNT(n.id)
            FROM news_app_news n
            JOIN news_app_category c ON n.category_id = c.id
            WHERE n.status = 'PB'
            GROUP BY c.name
            ORDER BY c.name
            """
        )
        print("\nPublished news by category:")
        for name, count in cur.fetchall():
            print(f" - {name}: {count}")
    except Exception as e:
        print("Error counting news:", e)

if __name__ == "__main__":
    main()

