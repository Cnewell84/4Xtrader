def read_secret(secret_name):
    """
    Read a Docker secret from the secrets directory.
    
    Args:
        secret_name (str): Name of the secret to read
        
    Returns:
        str: The secret value
    """
    try:
        with open(f'/run/secrets/{secret_name}', 'r') as secret_file:
            return secret_file.read().strip()
    except FileNotFoundError:
        raise ValueError(f"Secret {secret_name} not found") 