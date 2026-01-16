# Alembic Database Migrations

This folder contains database migrations managed by Alembic.

## Quick Commands

### Create a new migration
```bash
# Auto-generate based on model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration manually
alembic revision -m "Description of changes"
```

### Run migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade by one revision
alembic upgrade +1

# Upgrade to specific revision
alembic upgrade <revision_id>
```

### Rollback migrations
```bash
# Downgrade by one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade to base (remove all tables)
alembic downgrade base
```

### Check status
```bash
# Show current revision
alembic current

# Show all revisions
alembic history

# Show pending migrations
alembic history --verbose
```

## Migration History

| Revision | Description |
|----------|-------------|
| 001_initial | Create users, sessions, questions, feedback tables |
| 002_add_analytics | Add user statistics and session analytics columns |
| 003_add_question_bank | Add question templates and tags tables |

## File Structure

```
alembic/
├── env.py              # Environment configuration
├── script.py.mako      # Migration template
├── README.md           # This file
└── versions/           # Migration files
    ├── 001_initial.py
    ├── 002_add_analytics.py
    └── 003_add_question_bank.py
```

## Best Practices

1. **Always test migrations** on a copy of production data
2. **Never edit** already-applied migrations
3. **Review auto-generated** migrations before applying
4. **Use descriptive names** for migration files
5. **Keep migrations small** and focused on one change
