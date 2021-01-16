# import pytest
# from api import app as quart_app
# from quart.testing import QuartClient


# @pytest.fixture(name="app")
# def _test_app() -> QuartClient:
#     return quart_app.test_client()


# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "query_strings, status_code",
#     [
#         (
#             {
#                 "username": "DemoUser",
#                 "discriminator": "3",
#                 "type": "ADMIN",
#                 "order": "DESC",
#             },
#             200,
#         ),
#         (
#             {
#                 "username": "DemoUser",
#                 "limit": 5,
#                 "page": 2,
#                 "order": "DESC",
#             },
#             200,
#         ),
#         (
#             {
#                 "discriminator": "3",
#                 "type": "ADMIN",
#                 "order": "DESC",
#                 "limit": 10,
#             },
#             200,
#         ),
#         (
#             {
#                 "username": "DemoUser",
#                 "limit": 5,
#                 "page": 2,
#                 "order": "DESC",
#             },
#             200,
#         ),
#         (
#             {
#                 "username": "%00",
#                 "discriminator": "%00",
#                 "type": "%00",
#             },
#             400,
#         ),
#         (
#             {
#                 "discriminator": "%00",
#             },
#             400,
#         ),
#         (
#             {
#                 "type": "%00",
#             },
#             400,
#         ),
#     ],
# )
# async def test_get_all_users(app: QuartClient, query_strings: dict, status_code: int):
#     # TODO: Add db fixture after takos pull request merged
#     response = await app.get("/users/get-all", query_string=query_strings)
#     assert response.status_code == status_code
#     assert response.content_type == "application/json"
