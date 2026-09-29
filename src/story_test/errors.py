"""Exceptions raised for problems the user can fix."""


class StoryTestError(Exception):
    """Base class for expected errors, reported without a traceback."""


class ProviderError(StoryTestError):
    """An AI provider is misconfigured or returned an unusable answer."""
