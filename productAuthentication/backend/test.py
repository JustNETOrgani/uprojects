import psycopg2

try:
    conn = psycopg2.connect(
        password="S7kBHDlnRMjzicp8",
        user="postgres.bcabdfgfmxnahtokonvw" ,
        host="aws-1-eu-west-1.pooler.supabase.com" ,
        port=6543 ,
        dbname="postgres"
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")