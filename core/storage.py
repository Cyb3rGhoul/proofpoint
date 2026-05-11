from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import EvidenceItem


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "proofprint.sqlite"


def init_db(path: Path = DB_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evidence (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                source_type TEXT NOT NULL,
                filename TEXT,
                raw_text TEXT NOT NULL,
                created_on TEXT NOT NULL,
                extracted_json TEXT NOT NULL
            )
            """
        )


def save_evidence(items: list[EvidenceItem], path: Path = DB_PATH) -> None:
    init_db(path)
    with sqlite3.connect(path) as connection:
        connection.executemany(
            """
            INSERT OR REPLACE INTO evidence
            (id, title, source_type, filename, raw_text, created_on, extracted_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item.id,
                    item.title,
                    item.source_type,
                    item.filename,
                    item.raw_text,
                    item.created_on,
                    json.dumps(item.extracted),
                )
                for item in items
            ],
        )


def load_evidence(path: Path = DB_PATH) -> list[EvidenceItem]:
    init_db(path)
    with sqlite3.connect(path) as connection:
        rows = connection.execute(
            "SELECT id, title, source_type, filename, raw_text, created_on, extracted_json FROM evidence ORDER BY created_on, id"
        ).fetchall()
    return [
        EvidenceItem(
            id=row[0],
            title=row[1],
            source_type=row[2],
            filename=row[3] or "",
            raw_text=row[4],
            created_on=row[5],
            extracted=json.loads(row[6] or "{}"),
        )
        for row in rows
    ]
