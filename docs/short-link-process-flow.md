---
layout: default
title: "Short-link Process Flow"
description: "Process flows for actions related to short-links"
nav_order: 2
---
# Short-link Process Flow
## Create short-link
{% mermaid %}
graph TD;
    A[User submits new short-link];
    B[API request to /links submitted with short-link data];
    C[Short-link data is saved to DynamoDB on AWS];
    A --> B;
    B --> C;
{% endmermaid %}

## Redirect using short-link
{% mermaid %}
graph TD;
    D[Consumer uses short-link key via React application];
    E[API request to /links submitted to retrieve short-link data];
    F[URL for consumer to redirect to returned to React application];
    G[React application uses URL to generate and return a 300 redirect response];
    D --> E;
    E --> F;
    F --> G;
{% endmermaid %}