import pandas as pd
import os

# Imposta il base path come la cartella dello script
base_path = os.path.dirname(os.path.abspath(__file__))

# Percorso del file CSV, unito al base path
file_path = os.path.join(base_path, '..', 'report', 'node_level_analysis.csv')

# Stampa il percorso assoluto del file
absolute_path = os.path.abspath(file_path)
print(f"Percorso assoluto del file: {absolute_path}")

# Verifica che il file esista
if os.path.exists(absolute_path):
    # Carica il file CSV in un DataFrame
    df = pd.read_csv(absolute_path)

    # Ordina il DataFrame in base alla colonna 'Degree Centrality' in ordine decrescente
    sorted_df = df.sort_values(by="Degree Centrality", ascending=False)

    # Visualizza le parole chiave ordinate per centralità
    print(sorted_df[["Node", "Degree Centrality"]])

    # Percorso di esportazione del nuovo file CSV
    output_path = os.path.join(base_path, '..', 'report', 'keywords_ordered_by_degree_centrality.csv')

    # Esporta il DataFrame ordinato in un nuovo file CSV
    sorted_df[["Node", "Degree Centrality"]].to_csv(output_path, index=False)

    print(f"File CSV esportato con successo: {os.path.abspath(output_path)}")
else:
    print(f"Il file non esiste nel percorso: {absolute_path}")
