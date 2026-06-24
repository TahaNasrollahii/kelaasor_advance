from django.utils.translation import gettext_lazy as _

# =============================================================================
# Authentication Messages
# =============================================================================

# Registration
MSG_REGISTER_SUCCESS = _('User registered successfully.')

# OTP
MSG_OTP_SENT = _('OTP sent successfully.')
MSG_OTP_EXPIRED = _('OTP expired or not found.')
MSG_OTP_INVALID = _('Invalid OTP code.')
MSG_OTP_FORMAT_INVALID = _('Invalid OTP format.')
MSG_OTP_RESENT = _('Password reset OTP sent successfully.')
MSG_OTP_PASSWORD_RESET = _('Password has been reset successfully.')

# Login
MSG_LOGIN_DEACTIVATED = _('This account has been deactivated.')
MSG_LOGIN_FAILED = _('Login failed.')

# Phone validation
MSG_PHONE_REQUIRED_COUNTRY_CODE = _('Phone number must include country code (e.g. +98...)')
MSG_PHONE_INVALID_FORMAT = _('Invalid phone number format.')

# Password
MSG_PASSWORD_MISMATCH = _('Passwords do not match.')
MSG_PASSWORD_TOO_SHORT = _('Password must be at least 8 characters long.')
MSG_PASSWORD_RESET_FAILED = _('Password reset failed.')
MSG_IF_ACCOUNT_EXISTS_OTP_SENT = _('If an account with this mobile exists, an OTP has been sent.')
MSG_INVALID_CREDENTIALS = _('Invalid credentials.')


# =============================================================================
# Course Messages
# =============================================================================

MSG_COURSE_NOT_FOUND = _('Course not found.')
MSG_CATEGORY_NOT_FOUND = _('Category not found.')
MSG_INSTRUCTOR_NOT_FOUND = _('Instructor not found.')


# =============================================================================
# Purchase / Cart Messages
# =============================================================================

MSG_CART_EMPTY = _('Your cart is empty.')
MSG_CART_NO_ITEMS = _('No items found in your cart.')
MSG_COURSE_ALREADY_PURCHASED = _('Course already purchased.')
MSG_COURSE_ALREADY_IN_CART = _('Course already in cart.')
MSG_COURSE_ADDED_TO_CART = _('Course added to cart.')
MSG_PAYMENT_SUCCESSFUL = _('Payment successful.')

# Checkout validation
MSG_PARTICIPANT_REQUIRED = _('Each course must have at least one participant.')
MSG_NO_PARTICIPANTS_PROVIDED = _('No participants provided for course {course_id}.')
MSG_COURSE_NOT_IN_CART = _('Course {course_id} is not in your cart.')

# Discount codes
MSG_DISCOUNT_INVALID = _('Invalid discount code.')
MSG_DISCOUNT_NOT_VALID_FOR_COURSE = _('Discount code is not valid for this course.')
MSG_DISCOUNT_USAGE_CONDITIONS = _('Discount code is invalid or does not meet usage conditions.')
MSG_DISCOUNT_CODE_AND_COURSE_REQUIRED = _('code and course_id are required.')


# =============================================================================
# Ticket Messages
# =============================================================================

MSG_TICKET_NOT_FOUND = _('Ticket not found.')
MSG_TICKET_REPLY_UNAUTHORIZED = _('You do not have permission to reply to this ticket.')
MSG_TICKET_REPLY_SUCCESS = _('Reply posted successfully.')
MSG_TICKET_CREATED = _('Ticket created successfully.')
MSG_TICKET_UPDATED = _('Ticket updated successfully.')


# =============================================================================
# Notification Messages
# =============================================================================

MSG_NOTIFICATION_MARKED_READ = _('Notification marked as read.')


# =============================================================================
# Admin Panel Messages
# =============================================================================

MSG_USER_DELETED = _('User has been deleted.')
MSG_DISCOUNT_CREATED = _('Discount code created successfully.')
MSG_DISCOUNT_UPDATED = _('Discount code updated successfully.')
MSG_DISCOUNT_DELETED = _('Discount code deleted successfully.')


# =============================================================================
# Model Choice Labels
# =============================================================================

# Course types
COURSE_TYPE_ONLINE = _('Online')
COURSE_TYPE_OFFLINE = _('Offline')

# Order statuses
ORDER_STATUS_PENDING = _('Pending')
ORDER_STATUS_PAID = _('Paid')
ORDER_STATUS_FAILED = _('Failed')

# Ticket statuses
TICKET_STATUS_OPEN = _('Open')
TICKET_STATUS_IN_PROGRESS = _('In Progress')
TICKET_STATUS_CLOSED = _('Closed')

# Ticket departments
TICKET_DEPARTMENT_SUPPORT = _('Support')
TICKET_DEPARTMENT_FINANCE = _('Finance')
TICKET_DEPARTMENT_EDUCATION = _('Education')

# Discount types
DISCOUNT_TYPE_PERCENT = _('Percent')
DISCOUNT_TYPE_FIXED = _('Fixed Amount')

# Notification types
NOTIFICATION_TYPE_ORDER = _('Order')
NOTIFICATION_TYPE_TICKET = _('Ticket')
NOTIFICATION_TYPE_DISCOUNT = _('Discount')
NOTIFICATION_TYPE_SYSTEM = _('System')


# =============================================================================
# Model Help Texts
# =============================================================================

HELP_COURSE_ACCESS_DURATION = _('Access duration after purchase (days)')
HELP_VIDEO_DURATION = _('Video duration in minutes')
HELP_DISCOUNT_MAX_USAGE = _('Maximum number of times this code can be used')
HELP_DISCOUNT_USER = _('Restricted to a specific user')
HELP_DISCOUNT_COURSE = _('Restricted to a specific course')


# =============================================================================
# Admin Panel Labels
# =============================================================================

ADMIN_USER_INFO = _('User Information')
ADMIN_PERMISSIONS = _('Permissions')
ADMIN_TIMESTAMPS = _('Timestamps')

# Admin docstrings
ADMIN_LIST_TICKETS = _('List all user tickets with optional status filter.')
ADMIN_TICKET_DETAIL = _('Retrieve ticket details including messages.')
ADMIN_TICKET_REPLY = _('Post a reply to a ticket as support staff.')
ADMIN_LIST_ORDERS = _('List all orders for admin and finance.')
ADMIN_ORDER_DETAIL = _('Retrieve details of a specific order.')
ADMIN_LIST_NOTIFICATIONS = _('List all notifications for the current user.')
ADMIN_MARK_READ = _('Mark a notification as read.')
ADMIN_LIST_USERS = _('List users with search capability.')
ADMIN_USER_DETAIL = _('View, edit, and delete user details.')
ADMIN_LIST_GROUPS = _('List groups for role assignment.')
ADMIN_LIST_DISCOUNTS = _('List and create discount codes.')
ADMIN_DISCOUNT_DETAIL = _('View, update, and delete a discount code.')
ADMIN_STATS = _('Aggregate statistics for the admin dashboard.')


# =============================================================================
# Permission Docstrings
# =============================================================================

PERM_IS_ADMIN = _('Access restricted to admin users only.')
PERM_IS_SUPPORT = _('Access for support team members.')
PERM_IS_PRODUCT_MANAGER = _('Access for course and discount managers.')
PERM_IS_INSTRUCTOR = _('Access for instructors to their own data.')
PERM_IS_ADMIN_OR_SUPPORT = _('Combined access for admin and support roles.')
PERM_IS_ADMIN_OR_PRODUCT_MANAGER = _('Combined access for admin and product manager roles.')
PERM_IS_TICKET_OWNER_OR_SUPPORT = _('Only ticket owner or support staff can access this ticket.')
PERM_IS_ENROLLED_OR_FREE = _('Access to this video requires enrollment or the video must be free.')


# =============================================================================
# Celery Task Messages
# =============================================================================

MSG_PRICE_INCREASED = _("Course '{title}' price increased from {old_price} to {new_price}.")


# =============================================================================
# Email Templates
# =============================================================================

EMAIL_TICKET_REPLY_SUBJECT = _('New reply for your ticket: {title}')
EMAIL_TICKET_REPLY_BODY = _('Hello {name},\n\nYour ticket has been replied to:\n\n{message}\n\nPlease log in to view the full conversation.')

SMS_TICKET_REPLY = _('Your ticket has been replied to: {title}\n{message}')


# =============================================================================
# API Pagination
# =============================================================================

API_PAGE_SIZE_MESSAGE = _('Page {page} of {total_pages}.')
