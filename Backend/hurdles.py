from Backend.database_manager import databaseManager

def get_hurdles_for_level(level):
    """
    Retrieve hurdles for a given level from the database.

    Args:
        level (int): The level for which to retrieve hurdles.

    Returns:
        list: A list of hurdle dictionaries for the given level.

    Raises:
        ValueError: If the level has no hurdles defined.
    """
    db = databaseManager()
    hurdles = db.fetch_all(
        """
        SELECT description, correct_option, result, complexity
        FROM Hurdles
        WHERE level = %s
        ORDER BY RAND()
        LIMIT 5
        """,
        (level,)
    )

    if not hurdles:
        raise ValueError(f"No hurdles defined for level {level}. Please select a valid level.")

    return [
        {
            "description": h[0],
            "correct_option": h[1],
            "result": h[2],
            "complexity": h[3]
        }
        for h in hurdles
    ]

# Example Usage:
if __name__ == "__main__":
    try:
        level = 2  # Change this to test with other levels
        hurdles = get_hurdles_for_level(level)
        print(f"Hurdles for level {level}:", hurdles)
    except ValueError as e:
        print(e)
