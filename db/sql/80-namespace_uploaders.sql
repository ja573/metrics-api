INSERT INTO namespace_uploader (domain_name, uploader_id) VALUES
('readership.openbookpublishers.com', (SELECT uploader_id FROM uploader WHERE uploader_name = 'Open Book Publishers')),
('downloads.openbookpublishers.com', (SELECT uploader_id FROM uploader WHERE uploader_name = 'Open Book Publishers')),
('readership.operas.eu', (SELECT uploader_id FROM uploader WHERE uploader_name = 'Open Book Publishers')),
('downloads.operas.eu', (SELECT uploader_id FROM uploader WHERE uploader_name = 'Open Book Publishers'));
