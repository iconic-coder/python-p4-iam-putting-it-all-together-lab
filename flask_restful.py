"""Minimal local stub of the `flask_restful` package used by tests.

This project expects `from flask_restful import Resource` in `server/app.py`.
Providing a tiny shim here keeps tests runnable without installing external
dependencies. It intentionally implements only what's needed by the tests
and the application skeleton in this repo.
"""

import flask


class Resource:
    """Base Resource shim. Real `flask_restful.Resource` adds routing helpers
    and request dispatching; tests in this exercise only need the name to be
    importable and usable as a base class for resource classes.
    """
    pass


class Api:
    """A minimal `Api` shim that wires Resource classes to Flask routes.

    add_resource(resource_cls, route, endpoint=...) will register a URL
    rule on the provided Flask app and dispatch HTTP methods to the
    corresponding Resource methods (get/post/put/delete/patch).
    """
    def __init__(self, app=None):
        self.app = app

    def add_resource(self, resource, route, endpoint=None):
        endpoint_name = endpoint or getattr(resource, '__name__', None) or route

        def view_func(**kwargs):
            res = resource()
            method = flask.request.method.lower()
            handler = getattr(res, method, None)
            if handler is None:
                return ('', 405)
            return handler(**kwargs)

        # allow common HTTP methods
        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']

        self.app.add_url_rule(route, endpoint_name, view_func, methods=methods)
