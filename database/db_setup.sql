-- `states` table to store
CREATE TABLE IF NOT EXISTS states (
    user_id VARCHAR(256) PRIMARY KEY,
    state INT NOT NULL
);
-- `tasks` table to store tasks
CREATE TABLE IF NOT EXISTS tasks (
    user_id VARCHAR(256) NOT NULL,
    task_id INT NOT NULL,
    description VARCHAR(256) NOT NULL,
    isDone TINYINT(1) DEFAULT 0 CHECK (isDone IN (0, 1)),
    remark VARCHAR(256),
    due DATETIME,
    PRIMARY KEY (user_id, task_id)
);