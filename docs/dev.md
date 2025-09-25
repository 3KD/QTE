# Dev notes

## Smoke/batch
```bash
python3 tests_qte.py
python3 paper_batch.py
python3 paper_multi.py
python3 special_values_table.py
```

## Cache API
```python
import series_encoding as se
se.qte_cache_clear()
print('cache cleared')
```

## Env
- `QTE_POLYLOG_BACKEND={auto,mp,series}`
- `QTE_CACHE=1`
