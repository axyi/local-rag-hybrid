🔧 local-rag-mcp → гибридный поиск (coders.su, задание 4)

Апгрейд форка local-rag-mcp: LLM query expansion + параллельный BM25
full-text + Reciprocal Rank Fusion поверх FAISS-векторного поиска.
Спека (SDD) — 746 строк, единый контракт: verbatim-интерфейсы, тесты
first, 5 гейтов, бюджет 5 repair-циклов.

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
— Спека: 746 строк, 1 промпт → 9 коммитов
— Первый прогон: успех, 0 repair cycles
— Code review: 3 находки (test coverage + мёртвый код), все
  исправлены fix/test-коммитами
— Токены in/out: харнесс (Claude Code CLI) их не отдаёт. Оценка по
  публичным ценам Sonnet 5 ($2 / $10 за 1M токенов): ревью-субагент
  измерен — 70.8K токенов (~$0.2); вся сессия целиком — грубая оценка
  ~$5–8

github.com/axyi/local-rag-hybrid
