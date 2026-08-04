CREATE TABLE IF NOT EXISTS user_levels (
    user_id INTEGER PRIMARY KEY,
    experience INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);