# NIRMAN 2K25 - PDA College Fest Photo Gallery

A Flask web application for sharing and downloading photos from the NIRMAN 2K25 college fest at PDA College of Engineering.

## Features

- Upload photos with automatic compression for large images
- Browse photo gallery with search and sort functionality
- Download individual photos or the entire gallery as a ZIP file
- PIN protection for website access (PIN: 2005)
- Responsive design for all devices

## Deployment on Render

1. Fork or clone this repository
2. Create a new Web Service on Render
3. Link your GitHub repository
4. Add the following environment variables:
   - `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
   - `CLOUDINARY_API_KEY`: Your Cloudinary API key
   - `CLOUDINARY_API_SECRET`: Your Cloudinary API secret
5. Deploy the application

## Local Development

1. Clone the repository
2. Create a `.env` file with your Cloudinary credentials:
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python app.py`

## Credits

Designed & Developed by Omkar Padashetty 