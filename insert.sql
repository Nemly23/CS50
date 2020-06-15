INSERT INTO tags (tag) VALUES ('BarroeArte');
INSERT INTO tags (tag) VALUES ('RodasdoSaber');
INSERT INTO tags (tag) VALUES ('Outros');

INSERT INTO images (name, tag1_id) VALUES ('Potes', 1);
INSERT INTO images  (name, tag1_id, tag2_id) VALUES ('Rodas', 2, 1);
INSERT INTO images  (name, tag1_id) VALUES ('Barco', 3);

SELECT name FROM images WHERE tag1_id = 1 OR tag2_id = 1 OR tag3_id = 1;
