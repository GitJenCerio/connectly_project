def has_role(user, role_name):
    """
    Check if a user has a specific role (admin, user, guest).
    """
    return (
        user.is_authenticated and 
        hasattr(user, 'profile') and 
        getattr(user.profile, 'role', None) == role_name
    )
