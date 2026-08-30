🔧 local-rag-mcp → гибридный поиск (coders.su, задание 4)

Апгрейд форка local-rag-mcp: LLM query expansion + параллельный BM25
full-text + Reciprocal Rank Fusion поверх FAISS-векторного поиска.
Спека (SDD) — 9 265 токенов (tiktoken cl100k), единый контракт:
verbatim-интерфейсы, тесты first, 5 гейтов, бюджет 5 repair-циклов.

Результат: все 5 гейтов (uv sync, ruff, pytest, build-index, bench)
прошли с первого прогона — 0/5 repair cycles. На приватном корпусе
(56 документов, 286 чанков):
- vector-only: recall@5=0.4, MRR=0.35
- hybrid:      recall@5=0.9, MRR=0.68

По пути нашёл и починил баг апстрима (ingest.py — TypeError-рекурсия
на вложенных папках) и внутреннее противоречие спеки (ruff isort vs
"не трогать" upstream-файлы) — решение согласовано с пользователем, а
не решено втихую.

Метрики:
— Исполнитель: Claude Sonnet 5
— Спека: 9 265 токенов (tiktoken cl100k), 1 промпт → 9 коммитов
— Первый прогон: успех, 0 repair cycles
— Code review: 3 находки (test coverage + мёртвый код), все
  исправлены fix/test-коммитами
— Токены in/out: 14.17M (с кэш-чтениями) / 93.1k токенов, оценка по
  публичным API-ценам ≈ $5.6 (sonnet-5 ≈ $3.9 + ревью-агенты на
  opus-4.7 ≈ $1.7), замерено по локальным транскриптам сессии

github.com/axyi/local-rag-hybrid
