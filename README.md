# BorrowEZ - Community Item Sharing Platform

BorrowEZ is a web-based application that facilitates local item sharing within residential communities. Users can lend and borrow tools, equipment, and household items conveniently while integrating location-based navigation using Google Maps.

## Features

### 🔐 User Authentication
- Secure user registration and login
- Password hashing for security
- Session management

### 🏠 Public Landing Dashboard
- Introduction to BorrowEZ concept
- Benefits and outcomes explanation
- Login and registration options

### 👤 User Dashboard
- View all available items for borrowing
- Add new items for lending
- Browse items with images and details

### 📦 Item Management
- Add items with name, category, rent amount, and location
- Upload images (10KB size limit)
- Automatic Google Maps link generation using urllib

### 🗺️ Location Features
- Google Maps integration for item locations
- Direction-based navigation between borrower and lender
- Proper URL encoding using Python's urllib module

### 🎨 Modern UI/UX
- Responsive design with Bootstrap 5
- Clean and intuitive interface
- Mobile-friendly layout

## Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Styling with custom styles
- **Bootstrap 5** - Responsive framework
- **JavaScript** - Interactive features

### Backend
- **Python Flask** - Web framework
- **MongoDB Atlas** - Cloud database
- **Werkzeug** - Security utilities

### Key Libraries
- **urllib** - Location encoding for Google Maps
- **pymongo** - MongoDB driver
- **Werkzeug Security** - Password hashing

## Installation

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BorrowEZ
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB Atlas credentials
   ```

5. **Update MongoDB connection**
   - Open `app.py`
   - Replace the `MONGO_URI` with your MongoDB Atlas connection string
   - Update the database and collection names if needed

6. **Create upload directories**
   ```bash
   mkdir -p static/uploads
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Database Schema

### Users Collection
```json
{
  "_id": ObjectId,
  "name": "string",
  "email": "string",
  "password": "hashed_string",
  "created_at": "datetime"
}
```

### Items Collection
```json
{
  "_id": ObjectId,
  "owner_id": ObjectId,
  "owner_name": "string",
  "item_name": "string",
  "category": "string",
  "rent_per_hour": "number",
  "location_name": "string",
  "google_maps_link": "string",
  "image_path": "string",
  "created_at": "datetime"
}
```

## Key Features Implementation

### Google Maps Integration
The application uses Python's `urllib` module to:
- Encode location names for safe URL usage
- Generate Google Maps search links
- Create directions links between two locations

### Image Upload
- File size validation (10KB limit)
- Supported formats: PNG, JPG, JPEG, GIF
- Secure filename handling
- Organized storage in `static/uploads`

### Security Features
- Password hashing with Werkzeug
- Session management
- Input validation
- File upload security

## Usage Guide

### For Lenders
1. Register and login to your account
2. Click "Add New Item" on the dashboard
3. Fill in item details (name, category, rent amount, location)
4. Upload an image (optional, max 10KB)
5. Your item is now available for borrowing

### For Borrowers
1. Browse available items on the dashboard
2. Click "Borrow Item" to view details
3. View item location on Google Maps
4. Enter your location to get directions
5. Contact the lender to arrange pickup

## File Structure

```
BorrowEZ/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   ├── add_item.html     # Add item form
│   ├── borrow_item.html  # Item details
│   └── directions.html   # Navigation directions
├── static/              # Static files
│   ├── css/
│   │   └── style.css    # Custom styles
│   ├── js/
│   │   └── script.js    # JavaScript functionality
│   └── uploads/         # Uploaded images
└── venv/               # Virtual environment
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.

## Future Enhancements

- Real-time chat between lenders and borrowers
- Rating and review system
- Item availability calendar
- Mobile app development
- Payment integration
- Advanced search and filtering
- Notification system

---

**BorrowEZ** - Save money, reduce waste, build community! 🌱
