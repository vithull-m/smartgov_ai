CREATE DATABASE IF NOT EXISTS smartgov_ai CHARACTER SET utf8mb4;
USE smartgov_ai;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('citizen','admin') DEFAULT 'citizen',
    preferred_language VARCHAR(5) DEFAULT 'en',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    age INT,
    gender VARCHAR(20),
    income FLOAT,
    occupation VARCHAR(50),
    education VARCHAR(50),
    state VARCHAR(50),
    category VARCHAR(20),
    is_student BOOLEAN DEFAULT FALSE,
    is_farmer BOOLEAN DEFAULT FALSE,
    has_disability BOOLEAN DEFAULT FALSE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    department VARCHAR(150),
    description TEXT,
    benefits TEXT,
    category VARCHAR(50),
    target_group VARCHAR(100),
    state VARCHAR(50) DEFAULT 'All India',
    official_link VARCHAR(255),
    application_deadline DATETIME NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS eligibility_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scheme_id INT NOT NULL,
    field_name VARCHAR(50) NOT NULL,
    operator VARCHAR(10) NOT NULL,
    value VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scheme_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scheme_id INT NOT NULL,
    document_name VARCHAR(150) NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS application_steps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scheme_id INT NOT NULL,
    step_number INT NOT NULL,
    instruction TEXT NOT NULL,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS saved_schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scheme_id INT NOT NULL,
    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_save (user_id, scheme_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scheme_id INT NULL,
    message VARCHAR(255) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE SET NULL
);
