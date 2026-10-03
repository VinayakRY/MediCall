# MediCall

### Clinic Management & Patient Outreach Platform

MediCall is a full-stack clinic management platform designed to demonstrate how a spreadsheet-based clinic workflow can be transformed into a structured, authenticated, API-driven application.

The platform provides a centralized interface for managing patients, doctors, appointments, communication records, audit activity, and clinic assistance.

---

## Overview

MediCall was built as a practical full-stack application rather than a basic CRUD project.

It demonstrates:

- REST API development
- Authentication and authorization foundations
- Relational data modeling
- Database integration
- Frontend and backend communication
- Appointment and patient workflows
- Audit logging
- Patient outreach workflows
- AI-assisted clinic support
- Third-party telephony integration foundation
- Environment-based configuration

The project is intended as a **portfolio and demonstration application**.

---

## Features

### Patient Management

- Create and manage patient records
- View patient profiles
- View appointment history
- View communication history
- Archive patient records
- Centralized patient information

### Doctor Management

- Maintain doctor records
- Associate doctors with appointments
- Display doctor information within clinic workflows

### Appointment Management

- Create and manage appointments
- Associate patients with doctors
- Track appointment status
- Display upcoming appointments
- Centralized appointment overview

### Patient Outreach

- Create patient communication records
- Track outreach activity
- Support for telephony integration
- Optional Twilio integration for live calling

### Clinic Assistant

The application includes a clinic assistant interface designed to support staff with operational tasks and general health information.

The assistant is intentionally designed not to diagnose medical conditions or prescribe treatment.

### Audit Logging

Important application activity can be recorded through audit logs to provide visibility into staff operations.

### Dashboard

The dashboard provides an overview of clinic operations, including:

- Active patients
- Appointments
- Doctors
- Upcoming appointments
- Communication activity

---

## Technology Stack

### Frontend

- Python
- Streamlit
- Pandas
- Requests
- Custom CSS/UI components

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy

### Database

- SQLite for local development
- MySQL-compatible configuration for deployment

### Authentication

- JWT-based authentication
- Password hashing
- Environment-based configuration

### Integrations

- Twilio integration foundation for patient outreach

### Development

- Git
- GitHub
- REST APIs
- Environment variables

---

## Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Streamlit UI      │
                    │     Frontend        │
                    └──────────┬──────────┘
                               │
                          HTTP / REST
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │      Backend        │
                    ├─────────────────────┤
                    │ Authentication      │
                    │ Business Logic      │
                    │ API Endpoints       │
                    │ Audit Logging       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     SQLAlchemy      │
                    │        ORM          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   SQLite / MySQL    │
                    └─────────────────────┘

                    Optional Integrations
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
              Twilio                 AI Assistant