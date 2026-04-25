from typing import List, Dict, Any
from datetime import datetime
import threading

_lock = threading.Lock()

_blocked_urls: List[str] = []
_blocked_senders: List[str] = []
_alerts: List[Dict[str, Any]] = []


def add_blocked_url(url: str) -> None:
    with _lock:
        url_lower = url.strip().lower()
        if url_lower not in _blocked_urls:
            _blocked_urls.append(url_lower)


def add_blocked_sender(sender: str) -> None:
    with _lock:
        sender_lower = sender.strip().lower()
        if sender_lower not in _blocked_senders:
            _blocked_senders.append(sender_lower)


def remove_blocked_sender(sender: str) -> None:
    with _lock:
        sender_lower = sender.strip().lower()
        if sender_lower in _blocked_senders:
            _blocked_senders.remove(sender_lower)


def is_url_blocked(url: str) -> bool:
    return url.strip().lower() in _blocked_urls


def is_sender_blocked(sender: str) -> bool:
    return sender.strip().lower() in _blocked_senders


def get_blocked_urls() -> List[str]:
    return list(_blocked_urls)


def get_blocked_senders() -> List[str]:
    return list(_blocked_senders)


def add_alert(alert: Dict[str, Any]) -> None:
    with _lock:
        alert["timestamp"] = datetime.utcnow().isoformat() + "Z"
        _alerts.insert(0, alert)
        if len(_alerts) > 500:
            _alerts.pop()


def get_alerts(
    limit: int = 50,
    source_prefix: str = None,
    source_contains: str = None,
) -> List[Dict[str, Any]]:
    filtered = _alerts

    if source_prefix:
        filtered = [a for a in filtered if str(a.get("source", "")).startswith(source_prefix)]

    if source_contains:
        source_contains_lower = source_contains.lower()
        filtered = [a for a in filtered if source_contains_lower in str(a.get("source", "")).lower()]

    return filtered[:limit]


def clear_alerts(source_prefix: str = None, source_contains: str = None) -> int:
    with _lock:
        if not source_prefix and not source_contains:
            cleared = len(_alerts)
            _alerts.clear()
            return cleared

        before = len(_alerts)

        def should_delete(alert: Dict[str, Any]) -> bool:
            source = str(alert.get("source", ""))
            matches_prefix = source_prefix and source.startswith(source_prefix)
            matches_contains = source_contains and source_contains.lower() in source.lower()
            return bool(matches_prefix or matches_contains)

        _alerts[:] = [a for a in _alerts if not should_delete(a)]
        return before - len(_alerts)
