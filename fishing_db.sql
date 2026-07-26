CREATE TABLE IF NOT EXISTS islands (
    island_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fishes (
    fish_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fish_name TEXT NOT NULL,
    rarity INTEGER DEFAULT 0,
    ave_size DOUBLE DEFAULT 0.0, 
    emote_file TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_discord_id INTEGER DEFAULT 0,
    last_island INTEGER DEFAULT 1,
    total_fish INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_fish (
    user_id INTEGER,
    fish_id INTEGER,
    quantity INTEGER DEFAULT 0,
    largest_roll DOUBLE DEFAULT 0.0,
    PRIMARY KEY (user_id, fish_id),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    FOREIGN KEY (fish_id) REFERENCES fishes(fish_id)
);

CREATE TABLE IF NOT EXISTS fish_islands (
    fish_id INTEGER,
    island_id INTEGER,
    PRIMARY KEY (fish_id, island_id),
    FOREIGN KEY (fish_id) REFERENCES fishes(fish_id),
    FOREIGN KEY (island_id) REFERENCES islands(island_id)
);