INSERT INTO users (email, password, first_name, last_name, zip_code, location, match_radius, profile_img_file_name, hobbies, interests)
VALUES
    ('user1@example.com', 'password1', 'John', 'Doe', '02215', ST_SetSRID(ST_Point(-71.0589 + (random() - 0.5) / 7, 42.3601 + (random() - 0.5) / 7), 4326),
        FLOOR(RANDOM() * 5 + 1), 'profile_image.jpg', 'Hobbies', 'Interests'),
    ('user2@example.com', 'password2', 'Jane', 'Smith', '02130', ST_SetSRID(ST_Point(-71.0589 + (random() - 0.5) / 7, 42.3601 + (random() - 0.5) / 7), 4326),
        FLOOR(RANDOM() * 5 + 1), 'profile_image.jpg', 'Hobbies', 'Interests'),
    ('user3@example.com', 'password3', 'Mark', 'Johnson', '02119', ST_SetSRID(ST_Point(-71.0589 + (random() - 0.5) / 7, 42.3601 + (random() - 0.5) / 7), 4326),
        FLOOR(RANDOM() * 5 + 1), 'profile_image.jpg', 'Hobbies', 'Interests'),
    ('user4@example.com', 'password4', 'Sarah', 'Williams', '02199', ST_SetSRID(ST_Point(-71.0589 + (random() - 0.5) / 7, 42.3601 + (random() - 0.5) / 7), 4326),
        FLOOR(RANDOM() * 5 + 1), 'profile_image.jpg', 'Hobbies', 'Interests'),
    ('user5@example.com', 'password5', 'David', 'Brown', '02114', ST_SetSRID(ST_Point(-71.0589 + (random() - 0.5) / 7, 42.3601 + (random() - 0.5) / 7), 4326),
        FLOOR(RANDOM() * 5 + 1), 'profile_image.jpg', 'Hobbies', 'Interests'),
    ('user6@example.com', 'password6', 'Amy', 'Taylor', '02135', ST_SetSRID(ST_Point(-71.0589 + (random() - 0.5) / 7, 42.3601 + (random() - 0.5) / 7), 4326),
        FLOOR(RANDOM() * 5 + 1), 'profile_image.jpg', 'Hobbies', 'Interests');


INSERT INTO users (email, password, first_name, last_name, zip_code, match_radius, profile_img_file_name, hobbies, interests)
VALUES
    ('user1@example.com', 'password1', 'John', 'Doe', '02215',FLOOR(RANDOM() * 5 + 1), '', 'Hobbies', 'Interests'),
    ('user2@example.com', 'password2', 'Jane', 'Smith', '02130',FLOOR(RANDOM() * 5 + 1), '', 'Hobbies', 'Interests'),
    ('user3@example.com', 'password3', 'Mark', 'Johnson', '02119',FLOOR(RANDOM() * 5 + 1), '', 'Hobbies', 'Interests'),
    ('user4@example.com', 'password4', 'Sarah', 'Williams', '02199',FLOOR(RANDOM() * 5 + 1), '', 'Hobbies', 'Interests'),
    ('user5@example.com', 'password5', 'David', 'Brown', '02114',FLOOR(RANDOM() * 5 + 1), '', 'Hobbies', 'Interests'),
    ('user6@example.com', 'password6', 'Amy', 'Taylor', '02135',FLOOR(RANDOM() * 5 + 1), '', 'Hobbies', 'Interests');
