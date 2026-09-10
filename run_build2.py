import os 
base = r"C:/Users/luizi/agente_convert_moeda_fintech" 
def w(path, content): 
    import os 
    path = os.path.join(base, path) 
    os.makedirs(os.path.dirname(path), exist_ok=True) 
    with open(path, "w", encoding="utf-8") as f: f.write(content) 
    print(f"Written: {path}") 
if __name__ == "__main__": 
