import json
import pandas as pd

# Caminho para o arquivo JSON de publicações
publications_file = "data/publications.json"

# Carregar dados de publicações
def load_publications(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "publications" in data:
        data = data["publications"]
    else:
        raise ValueError("O arquivo JSON não contém a chave 'publications'.")
    return data

# Extrair relação entre autores e keywords
def extract_author_keyword_relations(publications):
    relations = []
    for pub in publications:
        authors = pub.get("authors", [])
        keywords = pub.get("keywords", [])
        for author in authors:
            for keyword in keywords:
                relations.append({"author": author, "keyword": keyword})
    return relations

# Carregar publicações
publications = load_publications(publications_file)

# Gerar relação autor-keyword
author_keyword_relations = extract_author_keyword_relations(publications)

# Converter em DataFrame
df_relations = pd.DataFrame(author_keyword_relations)

# Salvar para CSV
output_file = "report/author_keyword_relations.csv"
df_relations.to_csv(output_file, index=False)

print(f"Relação entre autores e keywords salva em: {output_file}")