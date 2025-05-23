import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import secrets
import requests
from io import BytesIO
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import zipfile
import tempfile
from PIL import Image, ImageDraw, ImageFont
import functools

# Load environment variables
load_dotenv()

# Check if Cloudinary credentials are properly set
cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
api_key = os.getenv('CLOUDINARY_API_KEY')
api_secret = os.getenv('CLOUDINARY_API_SECRET')

# Configure Cloudinary with the credentials from .env file
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

# Check if credentials exist
cloudinary_configured = all([cloud_name, api_key, api_secret])

# Helper function to check allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = 'nirman2k25_secure_key_for_sessions'

# PIN protection middleware for upload page
def upload_pin_required(func):
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        if request.method == 'GET' and not session.get('upload_authorized'):
            return render_template('upload_pin.html')
        return func(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html', cloudinary_configured=cloudinary_configured)

@app.route('/verify_upload_pin', methods=['POST'])
def verify_upload_pin():
    pin = request.form.get('pin')
    if pin == '2005':
        session['upload_authorized'] = True
        return redirect(url_for('upload'))
    flash('Incorrect PIN. Please try again.', 'error')
    return render_template('upload_pin.html')

@app.route('/upload', methods=['GET', 'POST'])
@upload_pin_required
def upload():
    if request.method == 'POST':
        try:
            # Check if Cloudinary is configured
            if not cloudinary_configured:
                flash('Cloudinary is not configured. Please set up your environment variables.', 'error')
                return redirect(url_for('upload'))
            
            uploader_name = request.form.get('uploader_name')
            if not uploader_name:
                flash('Please enter your name.', 'error')
                return redirect(url_for('upload'))
            
            upload_count = 0
            error_count = 0
            
            # Check for compressed data inputs
            compressed_files = []
            for key in request.form.keys():
                if key.startswith('compressed_data_'):
                    file_id = key.replace('compressed_data_', '')
                    filename = request.form.get(f'compressed_filename_{file_id}')
                    data = request.form.get(key)
                    if data and filename:
                        compressed_files.append({
                            'id': file_id,
                            'filename': filename,
                            'data': data
                        })
            
            # Process compressed files
            for compressed_file in compressed_files:
                try:
                    # Handle compressed image data
                    data = compressed_file['data']
                    filename = compressed_file['filename']
                    
                    if data.startswith('data:image'):
                        # Extract the base64 encoded data without the data URL prefix
                        format, imgstr = data.split(';base64,')
                        ext = format.split('/')[-1]
                        
                        # Generate a unique filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_filename = f"nirman2k25_{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"
                        
                        # Upload to Cloudinary
                        upload_result = cloudinary.uploader.upload(
                            data,
                            folder="nirman2k25",
                            context=f"uploader_name={uploader_name}",
                            public_id=os.path.splitext(unique_filename)[0]
                        )
                        
                        upload_count += 1
                except Exception as e:
                    print(f"Error uploading compressed file: {str(e)}")
                    error_count += 1
            
            # Check for regular file uploads
            if 'files' in request.files:
                files = request.files.getlist('files')
                for file in files:
                    # Skip files that have already been processed as compressed data
                    is_compressed = False
                    for compressed_file in compressed_files:
                        if compressed_file['filename'] == file.filename:
                            is_compressed = True
                            break
                    
                    if is_compressed or not file or file.filename == '':
                        continue
                    
                    try:
                        if not allowed_file(file.filename):
                            error_count += 1
                            continue
                        
                        # Generate a unique filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = secure_filename(file.filename)
                        unique_filename = f"nirman2k25_{timestamp}_{uuid.uuid4().hex[:8]}.{os.path.splitext(filename)[1]}"
                        
                        # Upload to Cloudinary
                        upload_result = cloudinary.uploader.upload(
                            file,
                            folder="nirman2k25",
                            context=f"uploader_name={uploader_name}",
                            public_id=os.path.splitext(unique_filename)[0]
                        )
                        
                        upload_count += 1
                    except Exception as e:
                        print(f"Error uploading file {file.filename}: {str(e)}")
                        error_count += 1
            
            # Show appropriate messages
            if upload_count > 0:
                if upload_count == 1:
                    flash('Photo uploaded successfully!', 'success')
                else:
                    flash(f'{upload_count} photos uploaded successfully!', 'success')
                
                if error_count > 0:
                    flash(f'{error_count} photos failed to upload.', 'error')
                    
                return redirect(url_for('gallery'))
            else:
                if error_count > 0:
                    flash(f'All {error_count} photos failed to upload. Please try again.', 'error')
                else:
                    flash('No photos were uploaded. Please select at least one photo.', 'error')
                return redirect(url_for('upload'))
            
        except Exception as e:
            print(f"Error during upload: {str(e)}")
            flash(f'Error uploading photos: {str(e)}', 'error')
            return redirect(url_for('upload'))
    
    return render_template('upload.html', cloudinary_configured=cloudinary_configured)

@app.route('/gallery')
def gallery():
    if not cloudinary_configured:
        flash('Cloudinary is not properly configured. Please update your .env file with valid credentials.', 'error')
        return render_template('gallery.html', images=[], cloudinary_configured=cloudinary_configured)
        
    try:
        # Get all images from the nirman2k25 folder in Cloudinary
        result = cloudinary.api.resources(
            type='upload',
            prefix='nirman2k25/',
            max_results=100,
            context=True
        )
        
        # Extract the necessary information for each image
        images = []
        for resource in result.get('resources', []):
            # Extract uploader name from context if available
            context = resource.get('context', {})
            if isinstance(context, dict):
                custom_context = context.get('custom', {})
                if isinstance(custom_context, dict):
                    uploader_name = custom_context.get('uploader_name', 'Anonymous')
                else:
                    uploader_name = 'Anonymous'
            else:
                uploader_name = 'Anonymous'
                
            images.append({
                'public_id': resource['public_id'],
                'url': resource['url'],
                'secure_url': resource['secure_url'],
                'format': resource['format'],
                'created_at': resource['created_at'],
                'uploader_name': uploader_name,
                'filename': resource['public_id'].split('/')[-1]
            })
        
        return render_template('gallery.html', images=images, cloudinary_configured=cloudinary_configured)
    except Exception as e:
        flash(f'Error loading gallery: {str(e)}', 'error')
        return render_template('gallery.html', images=[], cloudinary_configured=cloudinary_configured)

@app.route('/download/<path:public_id>.<format>')
def download_image(public_id, format):
    try:
        # Get the image URL from Cloudinary
        url = cloudinary.utils.cloudinary_url(public_id, format=format)[0]
        
        # Download the image
        response = requests.get(url)
        if response.status_code == 200:
            # Create a BytesIO object from the content
            image_io = BytesIO(response.content)
            
            # Add watermark
            image = Image.open(image_io)
            width, height = image.size
            
            # Create transparent text layer for watermark
            txt = Image.new('RGBA', image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt)
            
            # Determine font size based on image size
            font_size = int(min(width, height) * 0.03)  # 3% of the smaller dimension
            try:
                # Try to load a font, or use default
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
                
            watermark_text = "Omkar Padashetty"
            
            # Get text size to position in bottom right
            try:
                # Use getbbox (newer method) if available
                if hasattr(font, 'getbbox'):
                    bbox = font.getbbox(watermark_text)
                    textwidth, textheight = bbox[2], bbox[3]
                # Fall back to getsize (older method)
                elif hasattr(font, 'getsize'):
                    textwidth, textheight = font.getsize(watermark_text)
                # Last resort for older PIL versions
                else:
                    textwidth, textheight = draw.textsize(watermark_text, font=font)
            except Exception:
                # If all fails, estimate size
                textwidth = len(watermark_text) * font_size * 0.6
                textheight = font_size * 1.2
            
            x = width - textwidth - 20  # 20 pixels from right edge
            y = height - textheight - 20  # 20 pixels from bottom edge
            
            # Draw watermark with 60% opacity
            draw.text((x, y), watermark_text, fill=(255, 255, 255, int(0.6 * 255)), font=font)
            
            # Combine image with watermark
            watermarked = Image.alpha_composite(image.convert('RGBA'), txt)
            watermarked = watermarked.convert('RGB')  # Convert back to RGB for JPEG compatibility
            
            # Save watermarked image to a BytesIO object
            watermarked_io = BytesIO()
            watermarked.save(watermarked_io, format=format.upper() if format.lower() != 'jpg' else 'JPEG')
            watermarked_io.seek(0)
            
            # Get the original filename
            filename = public_id.split('/')[-1] + '.' + format
            
            # Return the file
            return send_file(
                watermarked_io,
                as_attachment=True,  # This forces download instead of displaying
                download_name=filename,
                mimetype=f'image/{format}'
            )
        else:
            flash('Error downloading image.', 'error')
            return redirect(url_for('gallery'))
    except Exception as e:
        flash(f'Error downloading image: {str(e)}', 'error')
        return redirect(url_for('gallery'))

@app.route('/download_all')
def download_all():
    if not cloudinary_configured:
        flash('Cloudinary is not properly configured. Please update your .env file with valid credentials.', 'error')
        return redirect(url_for('gallery'))
    
    try:
        # Get all images from the nirman2k25 folder in Cloudinary
        result = cloudinary.api.resources(
            type='upload',
            prefix='nirman2k25/',
            max_results=500,  # Increased max results
            context=True
        )
        
        # Create a temporary directory to store downloaded images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a ZIP file
            zip_filename = os.path.join(temp_dir, 'nirman2k25_photos.zip')
            
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                # Download and add each image to the ZIP file
                for i, resource in enumerate(result.get('resources', [])):
                    public_id = resource['public_id']
                    format = resource['format']
                    
                    # Download the image
                    url = cloudinary.utils.cloudinary_url(public_id, format=format)[0]
                    response = requests.get(url)
                    
                    if response.status_code == 200:
                        # Create BytesIO object from content
                        image_io = BytesIO(response.content)
                        
                        # Add watermark
                        image = Image.open(image_io)
                        width, height = image.size
                        
                        # Create transparent text layer for watermark
                        txt = Image.new('RGBA', image.size, (255, 255, 255, 0))
                        draw = ImageDraw.Draw(txt)
                        
                        # Determine font size based on image size
                        font_size = int(min(width, height) * 0.03)  # 3% of the smaller dimension
                        try:
                            # Try to load a font, or use default
                            font = ImageFont.truetype("arial.ttf", font_size)
                        except IOError:
                            font = ImageFont.load_default()
                            
                        watermark_text = "Omkar Padashetty"
                        
                        # Get text size to position in bottom right
                        try:
                            # Use getbbox (newer method) if available
                            if hasattr(font, 'getbbox'):
                                bbox = font.getbbox(watermark_text)
                                textwidth, textheight = bbox[2], bbox[3]
                            # Fall back to getsize (older method)
                            elif hasattr(font, 'getsize'):
                                textwidth, textheight = font.getsize(watermark_text)
                            # Last resort for older PIL versions
                            else:
                                textwidth, textheight = draw.textsize(watermark_text, font=font)
                        except Exception:
                            # If all fails, estimate size
                            textwidth = len(watermark_text) * font_size * 0.6
                            textheight = font_size * 1.2
                        
                        x = width - textwidth - 20  # 20 pixels from right edge
                        y = height - textheight - 20  # 20 pixels from bottom edge
                        
                        # Draw watermark with 60% opacity
                        draw.text((x, y), watermark_text, fill=(255, 255, 255, int(0.6 * 255)), font=font)
                        
                        # Combine image with watermark
                        watermarked = Image.alpha_composite(image.convert('RGBA'), txt)
                        watermarked = watermarked.convert('RGB')  # Convert back to RGB for JPEG compatibility
                        
                        # Save watermarked image to a BytesIO object
                        watermarked_io = BytesIO()
                        watermarked.save(watermarked_io, format=format.upper() if format.lower() != 'jpg' else 'JPEG')
                        watermarked_io.seek(0)
                        
                        # Generate a filename for the image in the ZIP
                        filename = f"{i+1:03d}_{public_id.split('/')[-1]}.{format}"
                        
                        # Add the file to the ZIP
                        zipf.writestr(filename, watermarked_io.getvalue())
                
            # Create a BytesIO object to serve the ZIP file
            zip_io = BytesIO()
            with open(zip_filename, 'rb') as f:
                zip_io.write(f.read())
            zip_io.seek(0)
            
            # Delete the temporary ZIP file
            os.unlink(zip_filename)
            
            # Return the ZIP file for download
            return send_file(
                zip_io,
                as_attachment=True,
                download_name='nirman2k25_photos.zip',
                mimetype='application/zip'
            )
            
    except Exception as e:
        print(f"Error downloading all images: {str(e)}")
        flash(f'Error downloading all images: {str(e)}', 'error')
        return redirect(url_for('gallery'))

if __name__ == '__main__':
    if not cloudinary_configured:
        print("\n\033[93mWARNING: Cloudinary credentials are not properly configured!\033[0m")
        print("Please update your .env file with valid Cloudinary credentials.")
        print("You can sign up for a free account at https://cloudinary.com/\n")
    
    app.run(debug=True) 
