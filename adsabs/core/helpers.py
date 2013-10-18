
from flask.globals import session, _request_ctx_stack

def set_global_messages(message, category='message'):
    """Registers a message to be available in this request.  In order 
    to remove the message from the session and to display it to the user,
    the template has to call :func:`get_request_messages`.

    :param message: the message to be included.
    :param category: the category for the message.  The following values
                     are recommended: ``'message'`` for any kind of message,
                     ``'javascript'`` for javascript to include in the 
                     page; ``'alerts'`` for alerts to be displayed at 
                     the whole website.  However any  kind of string 
                     can be used as category.
    """
    ads_global_messages = None
    if hasattr(_request_ctx_stack.top, 'ads_global_messages'):
        ads_global_messages = _request_ctx_stack.top.ads_global_messages
    if ads_global_messages is None:
        _request_ctx_stack.top.ads_global_messages = ads_global_messages = []
    ads_global_messages.append((category, message))
        


def get_global_messages(with_categories=False, category_filter=[]):
    """Pulls all flashed messages from the session and returns them.
    Further calls in the same request to the function will return
    the same messages.  By default just the messages are returned,
    but when `with_categories` is set to `True`, the return value will
    be a list of tuples in the form ``(category, message)`` instead.

    Filter the flashed messages to one or more categories by providing those
    categories in `category_filter`.  This allows rendering categories in
    separate html blocks.  The `with_categories` and `category_filter`
    arguments are distinct:

    * `with_categories` controls whether categories are returned with message
      text (`True` gives a tuple, where `False` gives just the message text).
    * `category_filter` filters the messages down to only those matching the
      provided categories.

    :param with_categories: set to `True` to also receive categories.
    :param category_filter: whitelist of categories to limit return values
    """
    ads_global_messages = None
    if hasattr(_request_ctx_stack.top, 'ads_global_messages'):
        ads_global_messages = _request_ctx_stack.top.ads_global_messages
    if ads_global_messages is None:
        _request_ctx_stack.top.ads_global_messages = ads_global_messages = []
    if category_filter:
        ads_global_messages = list(filter(lambda f: f[0] in category_filter, ads_global_messages))
    if not with_categories:
        return [x[1] for x in ads_global_messages]
    return ads_global_messages


