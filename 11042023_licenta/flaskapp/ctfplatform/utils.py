import os
import psycopg2

token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkhacTVFeDFXeWxCaEs5b0NSNk03M3JydTVwRkZlbFJRMWQ2ZDdGQVoyYVUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJjdGZzcGFjZSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJjdGZwbGF0Zm9ybS1zZWNyZXQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiY3RmcGxhdGZvcm1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImZmNWZjZjgyLWY0ODktNDRkOS1iNzhlLWQyZjc0NTgyZmFhYyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpjdGZzcGFjZTpjdGZwbGF0Zm9ybXNhIn0.U1NmZEhuV5oripRApB7N8QmtKk1Omi4Hvj3JjlNJ0tO8RyTRB6_WLIlpH8ZuU4szCah6_CcmMUDnhM5qBjjE93UUiUs-EzdhzFliLuCrvnTQyioNvQzBrABl_Ubp_aNPU5U3ZPLPaHsJ5Y0B5yP7J1F4-XeKrK-YLSn3ET4s97O9r4JfbGcKG2EKy5XJtOABwzF58I1coit3s_b4KUFWEod5We9kVxCnSWCkxM_30Bs0ufpA-mWv-OD8ujPZGzsoY8NhRP3qbl3yJYNjCLeC_nILuNdc38G2oTyJDwC2XsrkOkviWThOZfNJQXAKLujIy36iSKBsNifveazPXB6K5A"

def append_new_line(file_name, text_to_append):
    with open(file_name, "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        file_object.write(text_to_append)

def get_db_connection():
    conn = psycopg2.connect(
        host="172.17.0.7",
        port=5432,
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"])

    return conn

def get_kube_SAtoken():
    return token
