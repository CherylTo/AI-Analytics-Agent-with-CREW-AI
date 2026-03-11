# AI Analytics Report

**Question:** Which states have the most orders?

## SQL Query
```sql
SELECT customer_state AS state, COUNT(order_id) AS total_orders FROM analytics_orders GROUP BY customer_state ORDER BY total_orders DESC LIMIT 20
```

## Data Sample
|    | state   |   total_orders |
|---:|:--------|---------------:|
|  0 | SP      |          49865 |
|  1 | RJ      |          15425 |
|  2 | MG      |          13718 |
|  3 | RS      |           6538 |
|  4 | PR      |           5988 |

## Chart Metadata
- **chart_type:** bar
- **title:** Which states have the most orders?
- **x_field:** state
- **y_field:** total_orders
- **table_enabled:** True

## Summary
The state 'SP' has the highest number of total orders at 49,865, significantly ahead of 'RJ' with 15,425 and 'MG' with 13,718. Other states follow with substantially fewer orders.

## Key Takeaway
Focus on optimizing resources and marketing efforts in 'SP' where the order volume is the highest.

