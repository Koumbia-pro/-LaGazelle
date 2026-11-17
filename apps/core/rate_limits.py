from django.core.cache import cache


def increment_rate_limit(key, timeout):
    """Atomically count attempts on the configured shared cache when supported."""
    if cache.add(key, 1, timeout=timeout):
        return 1
    try:
        return cache.incr(key)
    except ValueError:
        # The key may expire between add() and incr(). Recreate it; if another
        # request won that race, read the counter it created.
        if cache.add(key, 1, timeout=timeout):
            return 1
        return cache.get(key, 1)
