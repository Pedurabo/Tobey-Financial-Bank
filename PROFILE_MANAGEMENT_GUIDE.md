# Profile Management System - User Guide

## Overview
The Profile Management System provides comprehensive user account management capabilities for the Tobey Finance Bank application. Users can view, edit, and manage their personal information, change passwords, set preferences, and track account activity.

## Features

### 1. Profile Viewing
- **Access**: Click "My Profile" in the sidebar navigation
- **Information Displayed**:
  - Personal information (name, email, employee ID)
  - Department and role information
  - Account creation date and last login
  - Associated banking account details (if applicable)

### 2. Profile Editing
- **Access**: Click "Edit Profile" button on profile page or navigate to `/profile/edit`
- **Editable Fields**:
  - First Name
  - Last Name
  - Email Address
  - Preferred Display Name
  - Phone Number
  - Emergency Contact
  - Time Zone
  - Privacy Settings
- **Read-only Fields**: Username, Employee ID, Department, Role (contact HR to change)

### 3. Password Management
- **Access**: Click "Change Password" in Quick Actions or use the modal
- **Requirements**:
  - Current password verification
  - New password minimum 6 characters
  - Password confirmation
- **Features**:
  - Real-time password strength indicator
  - Validation for password complexity
  - Secure password hashing

### 4. User Preferences
- **Access**: Click "Settings" button or preferences modal
- **Configurable Options**:
  - Theme (Light/Dark/Auto)
  - Language (English, Spanish, French, German)
  - Timezone
  - Currency Display
  - Date Format
  - Number Format
  - Notification Settings
  - Dashboard Layout

### 5. Activity Monitoring
- **Access**: Recent Activity section on profile page
- **Tracked Activities**:
  - Login attempts
  - Password changes
  - Profile updates
  - Security events
- **Information Displayed**:
  - Timestamp
  - Action type
  - IP Address
  - Status (Success/Failed)

### 6. Security Information
- **Access**: Click "Security Info" in Quick Actions
- **Information Displayed**:
  - Last password change
  - Account creation date
  - Two-factor authentication status
  - Login attempts today
  - Failed login attempts
  - Last login IP address
  - Active sessions

### 7. Data Export
- **Access**: Click "Export Data" in Quick Actions
- **Exported Data**:
  - Profile information
  - User preferences
  - Account creation details
  - Security information
- **Format**: JSON file with timestamp

## API Endpoints

### Profile Management
- `GET /profile` - View profile page
- `GET /profile/edit` - Edit profile page
- `POST /api/profile/update` - Update profile information
- `POST /api/profile/change-password` - Change password

### Preferences & Activity
- `GET /api/profile/preferences` - Get user preferences
- `POST /api/profile/preferences` - Update user preferences
- `GET /api/profile/activity` - Get user activity log

### Security & Export
- `GET /api/profile/security` - Get security information
- `GET /api/profile/export` - Export profile data

## Usage Instructions

### How to Update Your Profile
1. Navigate to your profile page by clicking "My Profile" in the sidebar
2. Click "Edit Profile" button
3. Modify the desired fields
4. Click "Save Changes"
5. Confirm the success message

### How to Change Your Password
1. Go to your profile page
2. Click "Change Password" in Quick Actions
3. Enter your current password
4. Enter your new password (minimum 6 characters)
5. Confirm your new password
6. Click "Change Password"
7. Verify the success message

### How to Set Preferences
1. Go to your profile page
2. Click "Settings" button
3. Adjust your preferences:
   - Theme and appearance
   - Language and timezone
   - Notification settings
   - Dashboard layout
4. Click "Save Preferences"

### How to View Security Information
1. Go to your profile page
2. Click "Security Info" in Quick Actions
3. Review your security details:
   - Password change history
   - Login activity
   - Two-factor authentication status
   - Active sessions

### How to Export Your Data
1. Go to your profile page
2. Click "Export Data" in Quick Actions
3. A JSON file will be automatically downloaded
4. The file contains all your profile and preference data

## Security Features

### Password Security
- Minimum 6 character requirement
- Password strength indicator
- Secure bcrypt hashing
- Current password verification for changes

### Activity Tracking
- All login attempts logged
- Profile changes tracked
- IP address recording
- Timestamp for all activities

### Data Protection
- Email validation
- Form input sanitization
- CSRF protection
- Secure session management

## Testing

### Run the Test Suite
```bash
python test_profile_management.py
```

### Test Coverage
- Profile page accessibility
- Profile editing functionality
- Password change system
- User preferences management
- Activity logging
- Security information display
- Data export functionality
- Form validation
- Multi-user role testing

## Troubleshooting

### Common Issues

**Profile Page Not Loading**
- Ensure you're logged in
- Check your internet connection
- Verify the Flask app is running

**Password Change Failed**
- Verify current password is correct
- Ensure new password meets requirements
- Check that passwords match

**Preferences Not Saving**
- Clear browser cache
- Ensure JavaScript is enabled
- Check network connectivity

**Data Export Not Working**
- Enable pop-ups in browser
- Check download permissions
- Verify browser supports file downloads

### Error Messages
- "Employee not found" - Contact system administrator
- "Invalid email format" - Use valid email address
- "Password too weak" - Use stronger password
- "Current password incorrect" - Verify your current password

## Advanced Features

### For Administrators
- Admin users can view additional security information
- HR admins can access employee management features
- Department-specific profile customizations

### Future Enhancements
- Profile picture upload
- Two-factor authentication setup
- Advanced activity filtering
- Bulk preference management
- Social login integration

## Support
For technical issues or questions about the profile management system, contact:
- IT Department: it@tobeyfinance.com
- HR Department: hr@tobeyfinance.com
- System Administrator: admin@tobeyfinance.com

## Version History
- v1.0 - Initial profile management system
- v1.1 - Added preferences and activity tracking
- v1.2 - Enhanced security features and data export
- v1.3 - Improved UI/UX and form validation

---

*Last Updated: January 2025*
*Tobey Finance Bank - Profile Management System* 