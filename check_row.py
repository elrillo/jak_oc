import psycopg2

DB_URL = "postgresql://postgres.tbniuckpxxzphturwnaj:KgjE5iLuevSXBHWU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

def check():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT texto_mocion FROM textos_pdf WHERE n_boletin = '6909-07'")
    row = cur.fetchone()
    print(repr(row[0]))

if __name__ == '__main__':
    check()
