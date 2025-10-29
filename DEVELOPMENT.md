# Development Notes

## Local Development Setup

This application is designed for production deployment on Linux servers with WireGuard. However, you can run it locally for development and testing.

### Prerequisites for Development

- Python 3.8 or higher
- Redis server
- (Optional) WireGuard for full functionality

### Quick Dev Setup

```bash
# Run development setup script
bash dev-setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env from example
cp .env.example .env

# Edit .env and set required values
nano .env

# Start Redis (if not running)
redis-server

# Run application
python3 app.py
```

### Running Without WireGuard

The application will run without WireGuard installed, but some features will not work:
- Adding/removing clients from WireGuard
- Viewing real-time connection statistics
- Generating peer configurations

You can still:
- Test the UI
- Test authentication and 2FA
- Create profiles
- View the interface
- Test backup/restore

### Development Mode

Set in `.env`:
```bash
FLASK_ENV=development
FLASK_DEBUG=True
```

This enables:
- Auto-reload on code changes
- Detailed error pages
- Debug toolbar

### Testing WireGuard Integration

To test WireGuard features locally (Linux/macOS):

1. Install WireGuard
2. Set up a test interface
3. Configure sudo permissions for your user
4. Update `.env` with test values

### Code Structure

```
app.py              # Main application entry point
config.py           # Configuration from environment
automation.py       # Background tasks

routes/             # All route handlers
  auth.py          # Login, 2FA, setup
  dashboard.py     # Main dashboard
  clients.py       # Client CRUD
  profiles.py      # Profile management
  usage.py         # Statistics
  settings.py      # Settings & backup
  audit.py         # Audit logs

utils/              # Utility modules
  storage.py       # File-based storage
  wireguard.py     # WireGuard operations
  auth.py          # Auth helpers
  helpers.py       # General utilities

templates/          # Jinja2 templates
  base.html        # Base template
  ...
```

### Making Changes

1. **Backend Changes**
   - Edit Python files in `routes/` or `utils/`
   - Changes auto-reload in debug mode
   - Test thoroughly before deploying

2. **Frontend Changes**
   - Edit HTML templates in `templates/`
   - CSS is inline in `base.html`
   - JavaScript is inline in individual templates

3. **Configuration Changes**
   - Update `config.py` for new settings
   - Add to `.env.example` for new variables
   - Document in README.md

### Testing Checklist

Before deploying changes:

- [ ] Test authentication flow
- [ ] Test 2FA setup
- [ ] Test client creation
- [ ] Test profile creation
- [ ] Test backup/restore
- [ ] Check audit logging
- [ ] Verify error handling
- [ ] Test on mobile viewport
- [ ] Check all links work
- [ ] Verify security features

### Common Development Tasks

#### Add a new route
1. Create function in appropriate `routes/*.py`
2. Add route decorator
3. Add to navigation in `templates/base.html`
4. Create template in `templates/`

#### Add a new setting
1. Add to `.env.example`
2. Add to `config.py`
3. Update settings display in `templates/settings/index.html`
4. Document in DEPLOYMENT.md

#### Modify database schema
Since we use JSON files, just:
1. Update data structure in `utils/storage.py`
2. Handle migration in code
3. Test with existing data

### Debugging Tips

#### Enable verbose logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check session data
```python
from flask import session
print(session)
```

#### Test Redis connection
```bash
redis-cli
> ping
> keys *
```

#### View logs
```bash
tail -f logs/wireguard_manager.log
```

### Security Testing

Before production:

1. **Authentication**
   - Test login with wrong password
   - Test 2FA with wrong code
   - Test session timeout
   - Test logout

2. **Authorization**
   - Try accessing pages without login
   - Test IP whitelist if enabled

3. **Input Validation**
   - Test with invalid inputs
   - Test with SQL injection attempts
   - Test XSS attempts

4. **File Operations**
   - Test backup creation
   - Test restore process
   - Test with corrupted files

### Performance Testing

For production readiness:

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test login page
ab -n 100 -c 10 http://127.0.0.1:5000/auth/login

# Test with authentication
ab -n 100 -c 10 -C "session=xyz" http://127.0.0.1:5000/
```

### Deployment Preparation

Before deploying to production:

1. Set `FLASK_ENV=production`
2. Set `FLASK_DEBUG=False`
3. Generate strong `SECRET_KEY`
4. Configure proper Redis URL
5. Set up HTTPS/SSL
6. Configure IP whitelist (optional)
7. Enable 2FA
8. Test backup/restore
9. Review security settings
10. Update all documentation

### Contributing

If you want to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Update documentation
6. Submit pull request

### Known Limitations

- File-based storage (not suitable for thousands of clients)
- Single-server only (no clustering)
- No real-time notifications
- No email integration
- No API (web UI only)

### Future Improvements

See PROJECT_SUMMARY.md for planned enhancements.

---

Happy developing! 🚀
