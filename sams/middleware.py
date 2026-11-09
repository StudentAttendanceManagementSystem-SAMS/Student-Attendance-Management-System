class NoCacheAuthenticatedPagesMiddleware:
    """
    Prevent browsers and intermediary caches from storing pages that may
    contain authenticated user data. This also helps prevent stale protected
    pages from appearing after logout when the user presses Back.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Apply to all SAMS pages so previously cached login/protected pages
        # are not reused from browser history.
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response
