"""storage.py - tiny persistence layer.

The original Flask app used SQLite. A PyScript site has no server, so data is
kept as JSON in the browser's localStorage (shop data) and sessionStorage
(staff login). If storage is blocked we fall back to memory so the site still works.
"""
import json

try:
    from pyscript import window
except Exception:  # running outside the browser (unit tests)
    window = None

_mem = {}


def _area(session):
    if window is None:
        return None
    try:
        return window.sessionStorage if session else window.localStorage
    except Exception:
        return None


def get(key, default=None, session=False):
    area = _area(session)
    try:
        raw = area.getItem(key) if area is not None else _mem.get((session, key))
    except Exception:
        raw = _mem.get((session, key))
    if raw is None:
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def put(key, value, session=False):
    raw = json.dumps(value)
    area = _area(session)
    try:
        if area is not None:
            area.setItem(key, raw)
            return
    except Exception:
        pass
    _mem[(session, key)] = raw


def remove(key, session=False):
    area = _area(session)
    try:
        if area is not None:
            area.removeItem(key)
    except Exception:
        pass
    _mem.pop((session, key), None)
