"""Notification push (ntfy) pour les très bonnes offres : une alerte sur le téléphone."""

import logging
import os

import httpx

log = logging.getLogger(__name__)


def push(offres: list, minimum: int, client: httpx.Client | None = None) -> int:
    """Envoie une notification par offre dont le score ≥ minimum. Rend le nombre envoyé.
    NTFY_URL (défaut https://ntfy.sh) et NTFY_TOPIC viennent de l'environnement."""
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        return 0
    base = os.environ.get("NTFY_URL", "https://ntfy.sh").rstrip("/")
    headers = {"Authorization": f"Bearer {os.environ['NTFY_TOKEN']}"} if os.environ.get("NTFY_TOKEN") else {}
    c, n = client or httpx.Client(timeout=15), 0
    for o, v in offres:
        if v.score < minimum:
            continue
        try:
            c.post(f"{base}/{topic}", content=f"{o.company or ''} · {o.location}".strip(" ·").encode(),
                   headers={**headers, "Title": f"{v.score}/100 · {o.title}".encode("utf-8").decode("latin-1", "ignore"),
                            "Click": o.url, "Tags": "briefcase"}).raise_for_status()
            n += 1
        except Exception:
            log.exception("ntfy : envoi impossible pour %s", o.title)
    return n
