CREATE OR REPLACE FUNCTION has_global_permission(uid BIGINT, permission INT)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
AS
$$
DECLARE
    role_perm BIGINT;

BEGIN
    FOR role_perm IN (
        SELECT r.permissions perm FROM roles r WHERE r.id IN (
            SELECT ur.role_id from userroles ur WHERE ur.user_id = uid
        )
    ) LOOP
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
