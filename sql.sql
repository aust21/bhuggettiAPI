-- database: instance/database.db
-- INSERT INTO user (name, email, password, speciality, company, is_admin, profile_image, cormfirm_code, account_confirmed)                                                           
-- VALUES ('Austin', 'kngobeni223@gmail.com', 'scrypt:32768:8:1$nogyeP77LlRGULW4$70733184b08e9b78e640c391d9d33403fd90668e2c4f0639d1b510cb23a1d0fd994aa8c6ffe8f63bf76dac5b5536e3000a8505d4a22b2e009fa6cf065dd12b2c', 'Admin', 'Virtitechs',  True, 'default.png', '00000000', True);

-- DELETE FROM user
-- WHERE
--   is_admin = 0;

INSERT INTO question_fields(question_field)
VALUES ('Other');