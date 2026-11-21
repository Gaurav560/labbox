CREATE TABLE product (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price_paise INT NOT NULL,
    sku VARCHAR(40) NOT NULL UNIQUE
);
INSERT INTO product (name, price_paise, sku) VALUES ('Masala tea', 2000, 'TEA-1');
INSERT INTO product (name, price_paise, sku) VALUES ('Filter coffee', 3000, 'COF-1');
INSERT INTO product (name, price_paise, sku) VALUES ('Samosa', 1800, 'SAM-1');
