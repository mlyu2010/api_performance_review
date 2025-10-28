# Production Deployment Guide

This guide covers deploying the Agents & Tasks API to production environments.

## Prerequisites

- Docker & Docker Compose installed
- Production server with:
  - Minimum 2GB RAM
  - 2+ CPU cores
  - 20GB disk space
- Domain name (recommended)
- SSL/TLS certificate (recommended via Let's Encrypt)



## Pre-Deployment Checklist

Before deploying to production, ensure you have:

- Generated a strong `SECRET_KEY` (64+ characters)
- Set up a production database with strong credentials
- Configured `ALLOWED_ORIGINS` (never use `*` in production)
- Set `ENVIRONMENT=production` in your .env file
- Reviewed all environment variables in `.env.production.example`
- Set up SSL/TLS certificates (e.g., via Let's Encrypt)
- Configured proper firewall rules
- Set up automated backups for the database
- Configured log aggregation (optional but recommended)
- Set up monitoring and alerting

