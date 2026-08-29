# Take-home: Domain Modelling Challenge

**Role:** Backend engineer
**Estimated time:** 2 hours

## About us

We run a food delivery platform: customers order from local restaurants and our couriers bring the food to their door. We are rebuilding our ordering service from scratch, and before anyone touches a keyboard we want to make sure the people we hire understand the business itself.

## What we want from you

Model the domain of our ordering and delivery flow. We are not asking for code, we want to see what business concepts you identify and how you structure them. Be prepared to walk us through it on a follow-up call and defend your decisions.

## How the business works

Customers order from restaurants through the app. A restaurant can be open or closed, and obviously you can only order while it's open. Each restaurant has a menu, and an order is made up of items from that restaurant's menu.

Once an order is placed it goes through a series of stages until it reaches the customer's door — from being created, to being prepared, to being handed over to a courier. Customers can cancel their orders, but only up to a point. Restaurants sometimes have to refuse orders too (for example when they are swamped or an ingredient ran out), and when that happens the customer must get their money back.

Payment is collected up front. If an order is cancelled or refused, the payment is refunded. A delivery fee applies, unless the order is big enough.

When an order is ready, one of our couriers takes it to the customer. A courier is only ever on one delivery at a time. After the food arrives, the customer can rate the experience.

## Notes

- This is a domain modelling exercise, not a coding exercise.
- If something seems ambiguous, make a reasonable assumption and write it down.
- We care more about the quality of your decisions than the completeness of the model.
