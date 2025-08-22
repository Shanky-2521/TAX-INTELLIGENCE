# Tax Intelligence - EITC Assistant

An AI-powered tax assistance system focused on Earned Income Tax Credit (EITC) eligibility and calculations, designed to help taxpayers understand their tax benefits while maintaining compliance with IRS guidelines.

## 🎯 Project Overview

Tax Intelligence is a comprehensive web application that provides:
- **EITC Eligibility Assessment**: Interactive questionnaire to determine EITC qualification
- **Real-time Tax Guidance**: AI-powered responses based on official IRS documentation
- **Multi-language Support**: English and Spanish interfaces
- **Safety-First Design**: Built-in safeguards to prevent tax misinformation
- **Admin Dashboard**: Internal tools for monitoring and quality assurance

## 🏗️ Architecture

```
Tax-Intelligence/
├── backend/                # Flask API, LLM logic, safety filters
│   ├── app.py             # Main Flask application
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic (LLM, retrieval, safety)
│   ├── models/            # Database models
│   └── config/            # Configuration files
├── frontend/              # React UI application
│   ├── src/               # React components and logic
│   ├── public/            # Static assets
│   └── package.json       # Frontend dependencies
├── knowledge_base/        # IRS EITC data, embeddings
│   ├── documents/         # Source IRS publications
│   ├── embeddings/        # Vector database
│   └── scripts/           # Data processing utilities
├── tests/                 # Comprehensive test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── deployments/           # Infrastructure as code
│   ├── docker/            # Docker configurations
│   ├── k8s/               # Kubernetes manifests
│   └── ci-cd/             # GitHub Actions workflows
├── docs/                  # Project documentation
│   ├── architecture/      # System design documents
│   ├── api/               # API documentation
│   └── user-guides/       # User documentation
└── scripts/               # Utility scripts
    ├── setup/             # Environment setup
    ├── data/              # Data processing
    └── deployment/        # Deployment utilities
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)
- OpenAI API key or local LLM setup

### Local Development Setup

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd Tax-Intelligence
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

3. **Backend Setup**
```bash
cd backend
export OPENAI_API_KEY=your_api_key_here
python app.py
```

4. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Admin Dashboard: http://localhost:3000/admin

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key
FLASK_ENV=development

# Optional
DATABASE_URL=sqlite:///tax_intelligence.db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/

# Frontend tests
cd frontend && npm test
```

## 🚢 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Cloud Deployment (AWS)
```bash
# Deploy using provided scripts
./scripts/deployment/deploy-aws.sh
```

## 📊 Monitoring & Analytics

- **Health Checks**: `/health` endpoint for system monitoring
- **Metrics**: Prometheus metrics at `/metrics`
- **Logs**: Structured logging with correlation IDs
- **Admin Dashboard**: Real-time system status and user feedback

## 🔒 Security & Compliance

- **Data Privacy**: No PII storage beyond session scope
- **Input Validation**: Comprehensive sanitization of user inputs
- **Response Filtering**: AI safety measures to prevent misinformation
- **Access Control**: Role-based permissions for admin features
- **Audit Trail**: Complete logging of all tax-related interactions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/Tax-Intelligence/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/Tax-Intelligence/discussions)

## 🎯 Roadmap

- [x] Core EITC eligibility assessment
- [x] Multi-language support (English/Spanish)
- [x] Safety and compliance framework
- [ ] Additional tax credit support (CTC, AOTC)
- [ ] Mobile application
- [ ] Advanced analytics dashboard
- [ ] Integration with tax preparation software

---

**⚠️ Important Notice**: This application provides general tax information based on IRS publications. It is not a substitute for professional tax advice. Users should consult qualified tax professionals for specific tax situations.
