"""
VectorDB — Desafio de busca por similaridade.

Implemente a função `search`. É o único arquivo que você edita e submete.

  Entrada:
    query      : list[float] de dimensão 5
    candidates : list[(id: str, vetor: list[float])]
  Saída:
    list[(id, score)] ordenada do maior score para o menor.

A fórmula de pontuação deve ser deduzida explorando o VectorDB Admin Console.

Regra adicional (não exibida na interface): documentos cujo vetor tenha o primeiro
elemento negativo (vetor[0] < 0) sofrem uma penalização no score; a constante
exata você descobre observando os scores no Console.
"""
import math
from typing import List, Tuple

def search(
    query: List[float],
    candidates: List[Tuple[str, List[float]]],
) -> List[Tuple[str, float]]:
    def dot_product(v1, v2):
        return sum(x * y for x, y in zip(v1, v2))
        
    def magnitude(v):
        return math.sqrt(sum(x**2 for x in v))
        
    q_mag = magnitude(query)
    if q_mag == 0:
        return [(c[0], 0.0) for c in candidates]
    penalty_query = abs(max(query, key=abs))
        
    results = []
    for c in candidates:
        item_id = c[0]
        c_vec = c[1]

        c_mag = magnitude(c_vec)

        if c_mag == 0:
            similarity = 0.0
        else:
            if c_vec[0] >= 0:
                similarity = dot_product(query, c_vec) / (q_mag * c_mag * penalty_query)

            else:
                similarity = dot_product(query, c_vec) / (3* q_mag * c_mag * penalty_query)
                
        results.append((item_id, similarity))

    return sorted(results, key=lambda x: x[1], reverse=True)