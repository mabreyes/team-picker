# 🚀 Deployment Guide for Render.com

This guide will help you deploy the Team Picker application to Render.com, a
modern cloud platform for hosting web applications.

## 📋 Prerequisites

-   A GitHub account with this repository
-   A Render.com account (free tier available)
-   Git installed locally

## 🔧 Quick Deployment Steps

### 1. Push to GitHub

Ensure your code is pushed to a GitHub repository:

```bash
git add .
git commit -m "Add Render.com deployment configuration"
git push origin main
```

### 2. Deploy on Render.com

1. **Sign up/Login** to [Render.com](https://render.com)

2. **Create a New Web Service**:

    - Click "New +" → "Web Service"
    - Connect your GitHub repository
    - Select this repository

3. **Configure the Service**:

    - **Name**: `team-picker` (or your preferred name)
    - **Environment**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
    - **Instance Type**: `Free` (or your preferred tier)

4. **Set Environment Variables**:

    - Go to "Environment" tab
    - Add the following variables:
        - `FLASK_ENV`: `production`
        - `SECRET_KEY`: Generate a secure random string (Render can
          auto-generate this)

5. **Deploy**: Click "Create Web Service"

## 🔄 Alternative: Using render.yaml

This repository includes a `render.yaml` file for automatic configuration:

1. **Enable Blueprint**: In your Render dashboard, go to "Blueprints"
2. **Create from Repository**: Select your GitHub repository
3. **Apply**: Render will automatically create the service with the specified
   configuration

## 🌐 Configuration Files Included

### `render.yaml`

-   Automatic service configuration
-   Environment variables setup
-   Disk storage for uploads

### `gunicorn.conf.py`

-   Production-optimized server settings
-   Worker process configuration
-   Logging and security settings

### `Procfile`

-   Alternative deployment command
-   Backup for platforms that don't use render.yaml

### `runtime.txt`

-   Specifies Python version (3.11.9)

## 🔒 Environment Variables

| Variable     | Description            | Default        | Required |
| ------------ | ---------------------- | -------------- | -------- |
| `FLASK_ENV`  | Flask environment      | `development`  | Yes      |
| `SECRET_KEY` | Session encryption key | Auto-generated | Yes      |
| `PORT`       | Server port            | Set by Render  | No       |

## 📁 File Storage

The application creates two directories for file storage:

-   `uploads/`: Temporary file uploads
-   `output/`: Generated team assignments (JSON and images)

Render provides 1GB of persistent disk storage mounted at
`/opt/render/project/src/uploads`.

## 🔧 Production Optimizations

### Security

-   Environment-based secret key
-   Input validation and file type restrictions
-   Secure file upload handling

### Performance

-   Gunicorn WSGI server with 2 workers
-   Request timeout and memory management
-   Optimized matplotlib backend for server environment

### Reliability

-   Graceful error handling
-   Automatic worker recycling
-   Health check endpoints

## 🐛 Troubleshooting

### Common Issues

**1. Build Fails**

-   Check Python version compatibility
-   Verify all dependencies in `requirements.txt`
-   Review build logs in Render dashboard

**2. App Won't Start**

-   Verify the start command: `gunicorn --bind 0.0.0.0:$PORT app:app`
-   Check environment variables are set correctly
-   Review application logs

**3. File Upload Issues**

-   Ensure upload directory is writable
-   Check file size limits (16MB max)
-   Verify disk storage is properly mounted

**4. Image Generation Fails**

-   Matplotlib backend is set to 'Agg' for server environment
-   Check if all image dependencies are installed

### Debug Commands

```bash
# Local testing with production settings
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
gunicorn --bind 0.0.0.0:8000 app:app

# Test with sample data
curl -X GET http://localhost:8000/api/sample-data
```

## 📊 Monitoring

### Health Checks

-   Render automatically monitors your service
-   The app includes error handling and logging
-   Monitor logs through Render dashboard

### Performance Metrics

-   Response times and error rates available in Render dashboard
-   Application logs accessible via web interface or CLI

## 🔄 Updates and Maintenance

### Automatic Deployments

-   Enable auto-deploy in Render settings
-   Pushes to `main` branch trigger new deployments
-   Zero-downtime deployments supported

### Manual Deployments

-   Use "Manual Deploy" in Render dashboard
-   Specify branch or commit for deployment

## 💰 Cost Considerations

### Free Tier

-   Perfect for development and small-scale use
-   Includes 750 hours/month of runtime
-   Services sleep after 15 minutes of inactivity

### Paid Tiers

-   Always-on services
-   Better performance and resources
-   Custom domains and SSL certificates

## 🔗 Useful Links

-   [Render.com Documentation](https://render.com/docs)
-   [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
-   [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Render's status page
3. Consult the application logs
4. Contact Render support for platform-specific issues
