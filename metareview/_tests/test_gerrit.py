import mock

from metareview import gerrit

def test_get_reviews():

    mock_request = mock.Mock()
    api = gerrit.Gerrit(requester=mock_request, end=10, cache_only=True)

    reviews = list(api.reviews())

    assert reviews == []
    assert not mock_request.call_count
