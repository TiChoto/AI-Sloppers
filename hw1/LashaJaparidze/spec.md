# Product Specification · Unimarket

## Problem
KIU students buying and selling used textbooks, calculators, and dorm gear lack a centralized campus marketplace, relying instead on scattered Telegram chats where details are inconsistent and prices are hard to compare.

## Proposed Solution
An AI-assisted campus marketplace API built with FastAPI that lets sellers create structured listings with explicit schema validation, ensuring valid item parameters (prices, conditions, descriptions) before publication.

## Key Endpoints & Scope
- `POST /listings/` — Create and validate new item listings. Reject non-positive or invalid prices.
- `GET /listings/` — Retrieve active item listings.
