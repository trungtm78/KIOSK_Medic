-- Initialize additional schemas for MedicAgent services
CREATE DATABASE IF NOT EXISTS `medicagent-directory-db`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS `medicagent-queue-db`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

  CREATE DATABASE IF NOT EXISTS `chat_service`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS `medicagent-admin-db`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Ensure application user exists and has access
CREATE USER IF NOT EXISTS 'medicagent'@'%' IDENTIFIED BY 'medicagent_password';
CREATE USER IF NOT EXISTS 'chat_user'@'%' IDENTIFIED BY 'chat_password';

GRANT ALL PRIVILEGES ON `medicagent-directory-db`.* TO 'medicagent'@'%';
GRANT ALL PRIVILEGES ON `medicagent-queue-db`.* TO 'medicagent'@'%';
GRANT ALL PRIVILEGES ON `chat_service`.* TO 'medicagent'@'%';
GRANT ALL PRIVILEGES ON `medicagent-admin-db`.* TO 'medicagent'@'%';

GRANT ALL PRIVILEGES ON `medicagent-directory-db`.* TO 'chat_user'@'%';
GRANT ALL PRIVILEGES ON `medicagent-queue-db`.* TO 'chat_user'@'%';
GRANT ALL PRIVILEGES ON `chat_service`.* TO 'chat_user'@'%';
GRANT ALL PRIVILEGES ON `medicagent-admin-db`.* TO 'chat_user'@'%';

FLUSH PRIVILEGES;
