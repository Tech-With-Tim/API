CREATE OR REPLACE FUNCTION has_permissions(uid BIGINT, permission INT)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
AS
$$
DECLARE
    role_perm BIGINT;

BEGIN
    FOR role_perm IN (
        SELECT r.permissions perm
        FROM roles r
        WHERE r.id IN (
            SELECT ur.role_id
            from userroles ur
            WHERE ur.user_id = uid
        )
    )
        LOOP
            -- Check if the user has global `Administrator` permission.
            IF (role_perm & 1) = 1 THEN
                RETURN true;
                -- Check if the user has the provided permission.
            ELSIF (role_perm & (1 << permission)) = (1 << permission) THEN
                RETURN true;
            END IF;
        END LOOP;
    RETURN false;
END;
$$;

CREATE OR REPLACE FUNCTION move_roles(pos int, role_id bigint, userid bigint = NULL, old_pos int = NULL)
    RETURNS VOID
    LANGUAGE plpgsql
AS
$$
DECLARE
    _role        RECORD;
    old_pos      int :=
        CASE
            WHEN old_pos IS NULL THEN
                (SELECT position
                 from roles
                 WHERE id = role_id)
            ELSE old_pos END;
    current_pos  int := old_pos;
    user_highest int := (
        SELECT min(position)
        FROM roles,
             userroles
        WHERE roles.id = userroles.role_id
          AND user_id = userid
    );
BEGIN
    IF userid IS NOT NULL THEN
        IF old_pos <= user_highest THEN
            RAISE EXCEPTION 'Missing Permission' USING ERRCODE = '22000';
        END IF;

        IF pos <= user_highest THEN
            RAISE EXCEPTION 'Missing Permission' USING ERRCODE = '22000';
        END IF;
    END IF;
    UPDATE roles SET position = 0 WHERE id = role_id;

    IF old_pos > pos THEN
        FOR _role in (
            SELECT *
            FROM roles
            WHERE position >= pos
              AND position <= current_pos
              AND id != role_id
            ORDER BY position
                DESC
        )
            LOOP
                UPDATE roles
                SET position = current_pos
                WHERE id = _role.id;
                current_pos := current_pos - 1;
            END LOOP;
    ELSEIF pos > old_pos THEN
        FOR _role in (
            SELECT *
            FROM roles
            WHERE position <= pos
              AND position >= current_pos
              AND id != role_id
            ORDER BY position
        )
            LOOP
                UPDATE roles SET position = current_pos WHERE id = _role.id;
                current_pos := current_pos + 1;
            END LOOP;
    END IF;
    UPDATE roles SET position = pos WHERE id = role_id;
END;
$$;

CREATE OR REPLACE FUNCTION add_role_to_member(roleid bigint, member_id bigint, userid bigint = NULL)
    RETURNS VOID
    LANGUAGE plpgsql
AS
$$
DECLARE
    role_position int := (SELECT position
                          FROM roles
                          WHERE id = roleid);
    user_highest  int := (
        SELECT min(position)
        FROM roles,
             userroles
        WHERE roles.id = userroles.role_id
          AND user_id = userid
    );
BEGIN
    IF userid IS NOT NULL THEN
        IF role_position <= user_highest THEN
            RAISE EXCEPTION 'Missing Permission' USING ERRCODE = '22000';
        END IF;
    END IF;

    INSERT INTO userroles (user_id, role_id) VALUES (member_id, roleid);
END;
$$;

CREATE OR REPLACE FUNCTION remove_role_from_member(roleid bigint, member_id bigint, userid bigint = NULL)
    RETURNS VOID
    LANGUAGE plpgsql
AS
$$
DECLARE
    role_position int := (
        SELECT position
        FROM roles
        WHERE id = roleid
    );
    user_highest  int := (
        SELECT min(position)
        FROM roles,
             userroles
        WHERE roles.id = userroles.role_id
          AND user_id = userid
    );
BEGIN
    IF userid IS NOT NULL THEN
        IF role_position <= user_highest THEN
            RAISE EXCEPTION 'Missing Permission' USING ERRCODE = '22000';
        END IF;
    END IF;

    DELETE FROM userroles WHERE user_id = member_id AND role_id = roleid;
END;
$$;

CREATE OR REPLACE FUNCTION delete_role(roleid bigint, userid bigint = NULL)
    RETURNS VOID
    LANGUAGE plpgsql
AS
$$
DECLARE
    _role         RECORD;
    role_position INT := (
        SELECT position
        FROM roles
        WHERE id = roleid
    );
    user_highest  int := (
        SELECT min(position)
        FROM roles,
             userroles
        WHERE roles.id = userroles.role_id
          AND user_id = userid
    );
BEGIN
    IF userid IS NOT NULL THEN
        IF role_position <= user_highest THEN
            RAISE EXCEPTION 'Missing Permission' USING ERRCODE = '22000';
        END IF;

        IF (SELECT base FROM roles WHERE id = roleid) = TRUE THEN
            RAISE EXCEPTION 'You can not delete a base role' USING ERRCODE = '22000';
        end if;
    END IF;

    DELETE FROM roles WHERE id = roleid;

    FOR _role IN (
        SELECT id, position
        FROM roles
        WHERE position > role_position
        ORDER BY position
    )
        LOOP
            UPDATE roles SET position = role_position WHERE id = _role.id;
            role_position := _role.position;
        END LOOP;
END;
$$;
