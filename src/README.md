## src/file.py
Contém as funções responsáveis por aplicar as regras de categorização.

Responsabilidades:

carregar as regras do arquivo .json

aplicar a categorização com base no título

retornar a categoria correspondente (ou “Outros”)

Exemplo de função:

```python
def categorizar_por_titulo(titulo, regras):
    for categoria, palavras in regras.items():
        if any(p.lower() in titulo.lower() for p in palavras):
            return categoria
            return "Outros"
```