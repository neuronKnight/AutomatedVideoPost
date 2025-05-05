# Video Automation System

A comprehensive, open-source solution for automating video creation and publishing across multiple social media platforms using Model Context Protocol (MCP).

## Overview

This system automatically generates video ideas based on daily festivals and holidays, creates engaging short-form videos, and publishes them to configured social media platforms—all without requiring expensive subscription services.

🏛 Architecture
The system follows a microservices architecture pattern using Model Context Protocol (MCP) for standardized communication:

┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Orchestrator   │◄────►│  MCP Services   │◄────►│   External      │
│  (Custom or n8n)│      │                 │      │   Services      │
└────────┬────────┘      └───────┬─────────┘      └────────┬────────┘
         │                       │                         │
         ▼                       ▼                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           Shared Storage                            │
└─────────────────────────────────────────────────────────────────────┘


## Features

- **Festival-Based Content Generation**: Automatically creates video ideas based on daily holidays
- **AI-Powered Video Creation**: Uses MoneyPrinterTurbo to transform ideas into complete videos
- **Multi-Platform Publishing**: Automatically publishes to TikTok, YouTube Shorts, Instagram Reels, and more
- **MCP Architecture**: Utilizes Model Context Protocol for standardized component communication
- **Environment Support**: Separate development and production configurations

## Quick Start

1. Clone the repository:

git clone <this repo>
cd video-automation-system

2. Run the setup script: make setup

3. Start the development environment: make dev

4. Access the components:
- n8n: http://localhost:5678
- MoneyPrinterTurbo UI: http://localhost:8501

## Configuration

- Development environment: `.env.dev`
- Production environment: `.env.prod`
- MoneyPrinterTurbo config: `config/moneyprinter/config.toml`

## MCP Services

The system consists of three main MCP servers:

1. **Idea Generator**: Generates video ideas based on festivals and holidays
2. **Video Generator**: Creates videos using MoneyPrinterTurbo
3. **Social Publisher**: Publishes videos across platforms using social-auto-upload

## Usage

### Basic Commands
make dev # Start development environment 
make prod # Start production environment make stop # Stop all containers 
make clean # Remove all containers and volumes 
make logs # View logs from all containers

### Creating n8n Workflows

1. Access n8n at http://localhost:5678
2. Create a new workflow
3. Add MCP client nodes to communicate with the MCP servers
4. Design your automation flow using the MCP tools


## License

This project is licensed under the MIT License.