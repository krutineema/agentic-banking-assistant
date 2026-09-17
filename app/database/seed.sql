-- Synthetic demo customers. Passwords are documented in README for local learning only.
INSERT OR IGNORE INTO customers (
    customer_id, username, display_name, password_salt, password_hash, password_iterations
) VALUES
(
    'cust-001', 'demo.alex', 'Alex Morgan',
    '7007581d2d0192ac2b19e1da353f5062',
    '74a65b6fe18add5e0d5c2cc3e292fc3c6aa21db8d58c886e6011aac3328050a9',
    120000
),
(
    'cust-002', 'demo.sam', 'Sam Patel',
    'c5c38a1ba05ac9305ab9bd2d67f616c0',
    '2cc0f72cc189fd0387b57ee2aabb29b27e522670369f4aa6b8cb8dcc2b8ef4f6',
    120000
);

-- Monetary values are stored in integer pence to avoid floating-point rounding.
INSERT OR IGNORE INTO accounts (
    account_id, customer_id, account_name, account_type, balance_pence, currency
) VALUES
('acc-current-001', 'cust-001', 'Everyday Current Account', 'current', 428564, 'GBP'),
('acc-savings-001', 'cust-001', 'Easy Access Savings', 'savings', 1245000, 'GBP'),
('acc-credit-001', 'cust-001', 'Rewards Credit Card', 'credit', -64322, 'GBP'),
('acc-current-002', 'cust-002', 'Everyday Current Account', 'current', 217530, 'GBP'),
('acc-savings-002', 'cust-002', 'Rainy Day Savings', 'savings', 680000, 'GBP');

INSERT OR IGNORE INTO transactions (
    transaction_id, account_id, transaction_date, merchant, amount_pence, direction, category, description
) VALUES
('txn-001', 'acc-current-001', '2026-09-14', 'Tesco', 6845, 'debit', 'groceries', 'Weekly groceries'),
('txn-002', 'acc-current-001', '2026-09-13', 'Cambridge Thai Kitchen', 4280, 'debit', 'restaurants', 'Dinner'),
('txn-003', 'acc-current-001', '2026-09-11', 'Shell', 5510, 'debit', 'transport', 'Fuel'),
('txn-004', 'acc-current-001', '2026-09-08', 'Netflix', 1799, 'debit', 'subscriptions', 'Monthly subscription'),
('txn-005', 'acc-current-001', '2026-09-05', 'Salary', 465000, 'credit', 'income', 'Monthly salary'),
('txn-006', 'acc-current-001', '2026-08-30', 'Sainsbury''s', 7420, 'debit', 'groceries', 'Groceries'),
('txn-007', 'acc-current-001', '2026-08-27', 'Pizza Express', 5800, 'debit', 'restaurants', 'Family dinner'),
('txn-008', 'acc-current-001', '2026-08-18', 'Costa Coffee', 1160, 'debit', 'restaurants', 'Coffee'),
('txn-009', 'acc-current-001', '2026-08-12', 'Tesco', 6675, 'debit', 'groceries', 'Groceries'),
('txn-010', 'acc-current-001', '2026-08-05', 'Salary', 465000, 'credit', 'income', 'Monthly salary'),
('txn-011', 'acc-current-001', '2026-07-28', 'Dishoom', 8340, 'debit', 'restaurants', 'Dinner'),
('txn-012', 'acc-current-001', '2026-07-16', 'Aldi', 5930, 'debit', 'groceries', 'Groceries'),
('txn-101', 'acc-current-002', '2026-09-14', 'Waitrose', 5125, 'debit', 'groceries', 'Groceries'),
('txn-102', 'acc-current-002', '2026-09-12', 'The Green Table', 3640, 'debit', 'restaurants', 'Dinner'),
('txn-103', 'acc-current-002', '2026-09-05', 'Salary', 390000, 'credit', 'income', 'Monthly salary'),
('txn-104', 'acc-current-002', '2026-08-22', 'Pho House', 2500, 'debit', 'restaurants', 'Lunch'),
('txn-105', 'acc-current-002', '2026-08-10', 'Morrisons', 6310, 'debit', 'groceries', 'Groceries');
