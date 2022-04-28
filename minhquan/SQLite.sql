-- SQLite
-- DELETE FROM sale_uomcategory;
-- INSERT INTO sale_uomcategory SELECT * FROM store_uomcategory;

-- DELETE FROM sale_uom;
-- INSERT INTO sale_uom SELECT * FROM store_uom;

-- DELETE FROM sale_productcategory;
-- INSERT INTO sale_productcategory
--       (id, name, parent_id, created_date, updated_date, active, slug)
-- SELECT id, name, parent_id, created_date, updated_date, active, slug FROM store_productcategory;

-- DELETE FROM sale_product;
-- INSERT INTO sale_product
--       (id, created_date, updated_date, active, name, slug, description, image, price, category_id, uom_id)
-- SELECT id, created_date, updated_date, active, name, slug, description, image, price, category_id, uom_id FROM store_product;

-- DELETE FROM sale_partner;
-- INSERT INTO sale_partner SELECT * FROM store_partner;

-- DELETE FROM sale_couponprogram;
-- INSERT INTO sale_couponprogram SELECT * FROM store_product;

-- DELETE FROM sale_coupon;
-- INSERT INTO sale_coupon SELECT * FROM store_coupon;

-- DELETE FROM sale_couponprogram_products;
-- INSERT INTO sale_couponprogram_products SELECT * FROM store_couponprogram_products;

DELETE FROM sale_orderdetail;
DELETE FROM sale_orderdeliver;
DELETE FROM sale_order;