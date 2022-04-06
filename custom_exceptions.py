"""Here are listed all custom errors and exceptions used for the project"""
import requests


class RequestFailedException(Exception):
    """Requires Response object of a failed request. Returns custom error message."""

    def __init__(self, response: requests.Response) -> None:
        self.message = f'Your request failed with following status {response.status_code} and message: {response.content}.'
        super().__init__(self.message)


class ItemIndexError(IndexError):
    """Raise this Error if item structure is not same as in the API documentation."""

    def __init__(self, failed_item: dict, origin_e: IndexError) -> None:
        self.message = f'Oops! Something is wrong with the structure of this item: {failed_item}.\nHere is the original error: {origin_e}.'
        super().__init__(self.message)
