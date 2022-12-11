---
layout: default
title: "Overview"
description: "Short-links and Link Collections"
nav_order: 1
---
# API Overview
- [Swagger UI](https://terryjharrison.github.io/see-this-api/swagger-ui/)
- All REST resources follow the same format:
  - `GET` to retrieve data
  - `POST` to create new unowned entries
    - Does not require authentication 
  - `PUT` to create new owned entries
  - `PATCH` to update existing entries
  - `DELETE` to remove data