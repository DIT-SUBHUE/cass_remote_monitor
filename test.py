import requests

anos = range(1997, 2005)
resultados = {}

for ano in anos:
    url = f"https://servicodados.ibge.gov.br/api/v2/censos/nomes/ranking?sexo=M&ano={ano}&localidade=BR"
    resp = requests.get(url).json()
    nomes = [item['nome'] for item in resp[0]['res'][:5]]  # top 5 nomes
    resultados[ano] = nomes

# Exibir o resumo
for ano, nomes in resultados.items():
    print(f"{ano}: {', '.join(nomes)}")
