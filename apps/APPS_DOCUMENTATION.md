# Econojin Apps Directory Documentation

This document provides a comprehensive overview of all the application modules in the Econojin platform.

## Overview

The Econojin platform is organized as a modular system with various specialized applications handling different aspects of the agriculture, water, environment, and economic platform. Each app serves a specific purpose and can be developed, tested, and deployed independently while maintaining integration with the core system.

## Core Shared Modules

### shared_core
- **Purpose**: Contains core infrastructure components including database session management, configuration, middleware, RBAC (Role-Based Access Control), and monitoring utilities.
- **Key Components**: Database sessions, JWT authentication, CORS middleware, security utilities, WebSocket support

### shared_ai
- **Purpose**: Houses artificial intelligence infrastructure including LLM factory, Celery task queues, and AI-related services.
- **Key Components**: LLM factory, Celery workers, AI models, AI services

### shared_knowledge
- **Purpose**: Manages knowledge representation, storage, and retrieval systems.
- **Key Components**: Knowledge graphs, knowledge storage, semantic search

### shared_sim
- **Purpose**: Provides shared simulation infrastructure and utilities.
- **Key Components**: Base simulation models, simulation utilities, common simulation schemas

## User Management Module

### users
- **Purpose**: Handles user authentication, registration, profiles, and account management.
- **Key Components**: JWT and OTP authentication, user models, password management, user services

## AI Agent Module

### ai_agents
- **Purpose**: Implements intelligent agents for various agricultural and environmental tasks.
- **Key Components**: Multiple specialized agents, agent communication, LLM integration, streaming capabilities

## Administrative Interface

### admin_panel
- **Purpose**: Provides administrative tools and interfaces for system management.
- **Key Components**: Admin frontend, performance patches, admin services, middleware

## API Services

### api
- **Purpose**: Contains various API routes and services for different business logic areas.
- **Key Components**: Accounting, ecocoin, monitoring, alerts, simulator, agriculture schools, education, RBAC seeding, science modules, ML integration

## Simulation Engine

### simulation
- **Purpose**: Comprehensive simulation engine supporting multiple domains including agriculture, hydrology, carbon cycle, nitrogen cycle, and more.
- **Key Components**: 
  - Agriculture simulators (28+ simulators)
  - Climate models
  - Carbon and nitrogen cycles
  - Hydrology models
  - Soil models
  - Biodiversity models
  - Economics models
  - Ecosystem services
  - Energy models
  - Water quality models
  - Urban models
  - MRV (Monitoring, Reporting, Verification) systems

## Content Management

### cms
- **Purpose**: Content management system for website content, articles, and educational materials.
- **Key Components**: Strapi CMS integration, content models, content services

## Agricultural Modules

### farms
- **Purpose**: Farm management and spatial data handling.
- **Key Components**: Farm models, spatial indexing, farm services

### crops
- **Purpose**: Crop management, agronomy services, and crop lifecycle management.
- **Key Components**: Crop models, agronomy services, seasonal planning

### planting
- **Purpose**: Planting schedule and season management.
- **Key Components**: Seasonal models, planting schedules

### inventory
- **Purpose**: Inventory tracking for agricultural inputs and outputs.
- **Key Components**: Inventory models, tracking systems

## Environmental Modules

### water
- **Purpose**: Water resource management and monitoring.
- **Key Components**: Water resource models, water quality metrics

### weather
- **Purpose**: Weather data integration and alert systems.
- **Key Components**: ERA5/CHIRPS integration, weather alerts, forecasting

### satellite
- **Purpose**: Satellite imagery processing and analysis for agriculture monitoring.
- **Key Components**: Google Earth Engine integration, image processing, MRV bridge, catalog services

### risks
- **Purpose**: Risk assessment and management for agricultural operations.
- **Key Components**: Risk engine, risk modeling, risk prediction

## Monitoring & Analytics

### monitoring
- **Purpose**: System and operational monitoring capabilities.
- **Key Components**: Metrics collection, monitoring models, alerting

## Support Modules

### dashboard
- **Purpose**: Dashboard and reporting frontend components.
- **Key Components**: Dashboard routes, data visualization

### notifications
- **Purpose**: Notification and messaging services.
- **Key Components**: Notification routing, messaging systems

### ml
- **Purpose**: Machine learning services and algorithms.
- **Key Components**: Classical ML algorithms, sensitivity analysis, synthetic data generation

### spider_security
- **Purpose**: Security middleware for protecting against automated threats.
- **Key Components**: Spider guard middleware, rate limiting, threat detection

## Application Entry Point

### main.py
The main application entry point that:
- Initializes the FastAPI application
- Sets up security middleware stack
- Configures CORS policies
- Loads all individual app routers
- Handles application lifecycle events
- Provides health checks and monitoring endpoints

## Key Features

1. **Modular Architecture**: Each app can be developed and maintained independently
2. **Security First**: Multi-layered security with middleware stack
3. **AI Integration**: Extensive AI and machine learning capabilities
4. **Simulation Engine**: Advanced agricultural and environmental simulation capabilities
5. **Real-time Data**: Integration with satellite imagery and weather data
6. **Scalable Design**: Designed for horizontal scaling and distributed deployment
7. **Comprehensive Monitoring**: Built-in monitoring and alerting systems

## Dependencies and Integrations

- PostgreSQL with PostGIS for spatial data
- Redis for caching and session storage
- Celery for background task processing
- Google Earth Engine for satellite data
- Various ML libraries for predictive analytics
- Strapi CMS for content management