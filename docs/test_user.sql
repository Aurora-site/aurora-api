-- insert test user
INSERT into customers (
    token,
    locale,
    city_id
)
VALUES (
    'test_token',
    'en',
    1
);


-- DELETE test user
DELETE FROM customers WHERE token = 'test_token';

-- insert test subscription
INSERT into subscriptions (
    id,
    cust_id,
    alert_probability,
    sub_type,
    geo_push_type
)
VALUES (
    '37bdb5b0-8cd9-4543-826a-8bc88a94dcaf',
    (SELECT id FROM customers WHERE token = 'test_token'),
    50,
    1,
    'SELECTED'
);

-- delete test subscription
DELETE FROM subscriptions WHERE id = '37bdb5b0-8cd9-4543-826a-8bc88a94dcaf';
