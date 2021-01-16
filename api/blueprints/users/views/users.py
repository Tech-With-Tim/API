from .. import bp
from quart import request, jsonify
from api.models import User
from asyncpg.exceptions import CharacterNotInRepertoireError, PostgresSyntaxError


@bp.route("/", methods=["GET"])
async def overview():
    return jsonify({"get all users": "/get-all"})


@bp.route("/get-all", methods=["GET"])
async def get_users():
    # Queries
    sort_by: str = request.args.get("sort_by", default="id")
    order: str = request.args.get("order", default="ASC")
    username: str = request.args.get("username", default=None)
    discriminator: str = request.args.get("discriminator", default=None)
    type: str = request.args.get("type", default=None)
    page: int = request.args.get("page", default=0, type=int)
    limit: int = request.args.get("limit", default=100, type=int)
    users = []

    try:
        # The following if statements are to check the number of queries passed
        # and allow the user to pass any number of queries possible
        if username is None and type is None and discriminator is None:
            query = """
                    SELECT json_agg(records)
                    FROM (
                        SELECT
                                json_build_object(
                                    'id', id,
                                    'username', username,
                                    'discriminator', discriminator,
                                    'avatar', avatar,
                                    'type', type
                                ) as records
                        FROM users
                        GROUP BY id
                        ORDER BY {0} {1}
                        OFFSET $1::INT * $2::INT
                        LIMIT $2
                    ) as users;
                """.format(
                sort_by, order
            )

            users = await User.pool.fetchval(query, page, limit)

        # To check if all queries are passed
        if username is not None and type is not None and discriminator is not None:
            query = """
                SELECT json_agg(records)
                FROM (
                    SELECT
                            json_build_object(
                                'id', id::TEXT,
                                'username', username,
                                'discriminator', discriminator,
                                'avatar', avatar,
                                'type', type
                            ) as records
                    FROM users
                    WHERE username LIKE $1 AND discriminator LIKE $2 AND type LIKE $3
                    GROUP BY id
                    ORDER BY {0} {1}
                    OFFSET $4::INT * $5::INT
                    LIMIT $5
                ) as users;
            """.format(
                sort_by, order
            )

            users = await User.pool.fetchval(
                query,
                username + "%",
                discriminator + "%",
                type,
                page,
                limit,
            )

        # The next 3 if statements are to check if 2 queries are passed
        if username is not None and type is not None and discriminator is None:
            query = """
                SELECT json_agg(records)
                FROM (
                    SELECT
                            json_build_object(
                                'id', id,
                                'username', username,
                                'discriminator', discriminator,
                                'avatar', avatar,
                                'type', type
                            ) as records
                    FROM users
                    WHERE username LIKE $1 AND type LIKE $2
                    GROUP BY id
                    ORDER BY {0} {1}
                    OFFSET $3::INT * $4::INT
                    LIMIT $4::INT
                ) as users;
            """.format(
                sort_by, order
            )

            users = await User.pool.fetchval(query, username + "%", type, page, limit)

        if username is not None and type is None and discriminator is not None:
            query = """
                SELECT json_agg(records)
                FROM (
                    SELECT
                            json_build_object(
                                'id', id,
                                'username', username,
                                'discriminator', discriminator,
                                'avatar', avatar,
                                'type', type
                            ) as records
                    FROM users
                    WHERE username LIKE $1 AND discriminator LIKE $2
                    GROUP BY id
                    ORDER BY {0} {1}
                    OFFSET $3::INT * $4::INT
                    LIMIT $4
                ) as users;
            """.format(
                sort_by, order
            )

            users = await User.pool.fetchval(
                query, username + "%", discriminator + "%", page, limit
            )

        if username is None and type is not None and discriminator is not None:
            query = """
                SELECT json_agg(records)
                FROM (
                    SELECT
                            json_build_object(
                                'id', id,
                                'username', username,
                                'discriminator', discriminator,
                                'avatar', avatar,
                                'type', type
                            ) as records
                    FROM users
                    WHERE discriminator LIKE $1 AND type LIKE $2
                    GROUP BY id
                    ORDER BY {0} {1}
                    OFFSET $3::INT * $4::INT
                    LIMIT $4
                ) as users;
            """.format(
                sort_by, order
            )

            users = await User.pool.fetchval(
                query, discriminator + "%", type, page, limit
            )

        # The next 3 if statements are to check if only one query is passed
        if username is not None and discriminator is None and type is None:
            query = """
                SELECT json_agg(records)
                FROM (
                    SELECT
                            json_build_object(
                                'id', id,
                                'username', username,
                                'discriminator', discriminator,
                                'avatar', avatar,
                                'type', type
                            ) as records
                    FROM users
                    WHERE username LIKE $1
                    GROUP BY id
                    ORDER BY {0} {1}
                    OFFSET $2::INT * $3::INT
                    LIMIT $3
                ) as users;
            """.format(
                sort_by, order
            )

            users = await User.pool.fetchval(query, username + "%", page, limit)

        if discriminator is not None and username is None and type is None:
            query = """
                SELECT json_agg(records)
                FROM (
                    SELECT
                            json_build_object(
                                'id', id,
                                'username', username,
                                'discriminator', discriminator,
                                'avatar', avatar,
                                'type', type
                            ) as records
                    FROM users
                    WHERE discriminator LIKE $1
                    GROUP BY id
                    ORDER BY {0} {1}
                    OFFSET $2::INT * $3::INT
                    LIMIT $3
                ) as users;
            """.format(
                sort_by, order
            )

            users = await User.pool.fetchval(query, discriminator + "%", page, limit)

        if type is not None and username is None and discriminator is None:
            query = """
                SELECT json_agg(records)
                FROM (
                    SELECT
                            json_build_object(
                                'id', id,
                                'username', username,
                                'discriminator', discriminator,
                                'avatar', avatar,
                                'type', type
                            ) as records
                    FROM users
                    WHERE type LIKE $1
                    GROUP BY id
                    ORDER BY {0} {1}
                    OFFSET $2:INT * $3::INT
                    LIMIT $3
                ) as users;
            """.format(
                sort_by, order
            )

            users = await User.pool.fetchval(query, type, page, limit)

        if page is not None and limit is None:
            response = jsonify(
                {
                    "error": "Bad Request",
                    "message": "If the pages query is provided then limit query should also be provided.",
                    "status_code": 400,
                }
            )
            response.status_code = 400
            return response

        # To check if there are no users
        if users is None or users == []:
            return jsonify([])

        return jsonify(users)

    except (CharacterNotInRepertoireError, PostgresSyntaxError):
        response = jsonify(
            {
                "error": "Bad Request",
                "message": "Please enter a valid value for querystring.",
                "status_code": 400,
            }
        )
        response.status_code = 400
        return response
