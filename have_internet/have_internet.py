try:
    import httplib
except:
    import http.client as httplib

def have_internet(uri="8.8.8.8") -> bool:
    conn = httplib.HTTPSConnection(uri, timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if have_internet():
        print("Internet is available :-)")
    else:
        print("No internet available :-(")
