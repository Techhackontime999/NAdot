# 🤝 Contributing to NAdot

Thank you for your interest in contributing to **NAdot v1.0.0**! We welcome contributions from the community to help make this professional networking platform even better.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Be respectful** and inclusive to all contributors
- **Be constructive** in discussions and feedback
- **Focus on the project** and avoid personal attacks
- **Help others** learn and grow
- **Follow the project guidelines** and standards

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Basic knowledge of Django and web development
- Familiarity with HTML, CSS, JavaScript

### Quick Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/NAdot.git
   cd NAdot/NAdot
   ```

2. **Set up development environment**
   ```bash
   # Use the deployment script
   ./deploy.sh development  # Unix/Linux/Mac
   # OR
   deploy.bat development   # Windows
   ```

3. **Create a branch for your changes**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ How to Contribute

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug fixes**
- ✨ **New features**
- 📚 **Documentation improvements**
- 🎨 **UI/UX enhancements**
- 🧪 **Tests and quality improvements**
- 🔧 **Performance optimizations**
- 🌐 **Translations and accessibility**

### Priority Areas for v1.0.0+

- **Image sharing enhancements** (primary focus)
- **Mobile responsiveness improvements**
- **Performance optimizations**
- **Security enhancements**
- **User experience improvements**
- **Documentation and tutorials**

## 💻 Development Setup

### Detailed Setup

1. **Clone and setup**
   ```bash
   git clone https://github.com/Techhackontime999/NAdot.git
   cd NAdot/NAdot
   python -m venv venv
   source venv/bin/activate  # Unix/Linux/Mac
   # OR
   venv\Scripts\activate.bat  # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run development server**
   ```bash
   python manage.py runserver
   ```

5. **Run tests**
   ```bash
   python manage.py test
   ```

### Project Structure

```
NAdot/
├── NAdot/                 # Main project directory
│   ├── core/              # Core functionality
│   ├── users/             # User management
│   ├── feed/              # Posts and content
│   ├── network/           # Networking features
│   ├── jobs/              # Job system
│   ├── messaging/         # Real-time messaging
│   ├── theme/             # UI themes
│   └── professional_network/  # Django settings
├── docs/                  # Documentation
├── tests/                 # Test files
└── requirements.txt       # Dependencies
```

## 📝 Coding Standards

### Python/Django Standards

- Follow **PEP 8** style guidelines
- Use **meaningful variable names**
- Write **docstrings** for functions and classes
- Keep functions **small and focused**
- Use **Django best practices**

### Frontend Standards

- Use **semantic HTML5**
- Follow **Tailwind CSS** conventions
- Write **accessible code** (WCAG 2.1 AA)
- Ensure **mobile responsiveness**
- Use **modern JavaScript** (ES6+)

### Example Code Style

```python
def create_post_with_image(user, content, image=None):
    """
    Create a new post with optional image attachment.
    
    Args:
        user: The user creating the post
        content: Post content text
        image: Optional image file
        
    Returns:
        Post: The created post instance
    """
    post = Post.objects.create(
        user=user,
        content=content,
        image=image
    )
    return post
```

## 📤 Submitting Changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   python manage.py test
   python check_version.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add amazing feature for image sharing"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Create a Pull Request**
   - Go to GitHub and create a PR
   - Provide a clear description
   - Reference any related issues

### Pull Request Guidelines

- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Screenshots** for UI changes
- **Test results** showing everything passes
- **Link to issues** if applicable

## 🐛 Reporting Issues

### Before Reporting

- Check if the issue already exists
- Try to reproduce the issue
- Gather relevant information

### Issue Template

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Browser: [e.g., Chrome 96, Firefox 95]
- Python version: [e.g., 3.10.1]
- Django version: [e.g., 5.2.10]
```

## 💡 Feature Requests

We love new ideas! When suggesting features:

- **Explain the use case** - Why is this needed?
- **Describe the solution** - How should it work?
- **Consider alternatives** - Are there other approaches?
- **Think about impact** - How does it fit with v1.0.0 goals?

## 🏷️ Labels and Workflow

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority-high` - Critical issues
- `v1.0.0` - Related to current version

## 🎉 Recognition

Contributors will be recognized in:

- **CHANGELOG.md** - For significant contributions
- **README.md** - In the contributors section
- **Release notes** - For major features

## 📞 Getting Help

Need help contributing?

- **GitHub Discussions** - For questions and ideas
- **Issues** - For bugs and feature requests
- **Email** - amitkumarkh010102006@gmail.com
- **Documentation** - Check the `/docs` folder

## 🙏 Thank You

Every contribution, no matter how small, helps make NAdot better for the professional community. Thank you for being part of this journey!

---

**NAdot v1.0.0** - *Connecting Professionals, One Contribution at a Time* 🌟

**Founded by**: [Techhackontime999](https://github.com/Techhackontime999)  
**Repository**: https://github.com/Techhackontime999/NAdot.git