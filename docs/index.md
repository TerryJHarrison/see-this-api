---
layout: default
title: "Overview"
description: "Short-links and Link Collections"
nav_order: 1
---
# API Overview
- [Swagger UI](./swagger-ui/)
- [OpenAPI Specifications](./openapi.json)
- All REST resources follow the same format:
  - `GET` requests to retrieve data
  - `POST` requests to create new unowned entries
    - Requests do not require authentication 
  - `PUT` requests to create new owned entries
  - `PATCH` requests to update existing entries
  - `DELETE` requests to remove data