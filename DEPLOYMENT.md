# Forbes Capital - Render Deployment Guide

## Prerequisites
- Git repository with your Django project
- Render account (free tier available)

## Deployment Steps

### 1. Prepare Your Repository
Make sure all files are committed to your Git repository:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create a Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Web Service"
3. Connect your Git repository
4. Configure the service:
   - **Name**: `forbes-capital` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn fc.wsgi:application`
   - **Plan**: Free (or paid plan for production)

### 3. Set Environment Variables

In your Render service settings, add these environment variables:

**Required Variables:**
```
DJANGO_SECRET_KEY=your-super-secret-key-here-generate-a-new-one
DEBUG=False
EMAIL_HOST_PASSWORD=your-email-password
```

**Optional Variables (Render sets some automatically):**
```
ALLOWED_HOSTS=your-app-name.onrender.com
RENDER_EXTERNAL_HOSTNAME=your-app-name.onrender.com
```

### 4. Database Setup

Render will automatically create a PostgreSQL database if you add one:
1. In your service, go to "Environment"
2. Add a PostgreSQL database
3. Render will automatically set the `DATABASE_URL` environment variable

### 5. Generate a Strong Secret Key

Generate a new Django secret key for production:
```python
import secrets
print(secrets.token_urlsafe(50))
```

### 6. Custom Domain (Optional)

If you have a custom domain:
1. Add it in Render's "Custom Domains" section
2. Update `ALLOWED_HOSTS` environment variable to include your domain
3. Update CORS settings if needed

## Post-Deployment

### Create Superuser
After deployment, create an admin user:
1. Go to your Render service shell
2. Run: `python manage.py createsuperuser`

### Upload Media Files
For user uploads (profile pictures), consider using:
- Cloudinary
- AWS S3
- Render's persistent disk (paid plans)

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `DJANGO_SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (False for production) | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Auto-set by Render |
| `EMAIL_HOST_PASSWORD` | Email password | Yes |
| `ALLOWED_HOSTS` | Allowed hostnames | Auto-set by Render |
| `RENDER_EXTERNAL_HOSTNAME` | External hostname | Auto-set by Render |

## Troubleshooting

### Common Issues:

1. **Static files not loading**: Check WhiteNoise configuration
2. **Database errors**: Ensure PostgreSQL database is connected
3. **Email not working**: Verify email credentials
4. **CORS errors**: Update CORS_ALLOWED_ORIGINS in settings

### Logs:
Check Render logs in your service dashboard for debugging.

## Security Notes

- Never commit `.env` files or sensitive data
- Use strong, unique secret keys
- Keep dependencies updated
- Monitor your application logs