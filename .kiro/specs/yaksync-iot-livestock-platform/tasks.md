# Implementation Plan: YakSync IoT Livestock Management Platform

## Overview

This implementation plan covers Phase 1 of the YakSync platform, focusing on establishing the complete Django project structure, authentication system, base template system with professional UI, and core CRUD operations for all entities. The tasks are organized to build incrementally, with each step validating functionality before proceeding.

**Technology Stack**: Django 4.x, SQLite (development), Vanilla CSS/JS, Django Templates

**Development Approach**: 
- Build project structure first
- Create all Django apps with models
- Apply migrations to verify database schema
- Implement authentication system
- Build base template system with professional UI
- Wire all components together
- Verify complete functionality

## Tasks

- [ ] 1. Initialize Django project and create base structure
  - Create Django project named `yaksync_project`
  - Create `apps/` directory for Django applications
  - Configure `settings.py` with correct `INSTALLED_APPS`, database settings, static/media paths
  - Set up `templates/` and `static/` directories in project root
  - Configure `TEMPLATES` setting to include project-level templates directory
  - Configure `STATICFILES_DIRS` to include project-level static directory
  - _Requirements: 10.1, 10.8, 10.10, 12.3_

- [ ] 2. Create all Django applications
  - [ ] 2.1 Create authentication app
    - Run `python manage.py startapp authentication apps/authentication`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_

  - [ ] 2.2 Create dashboard app
    - Run `python manage.py startapp dashboard apps/dashboard`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_

  - [ ] 2.3 Create animals app
    - Run `python manage.py startapp animals apps/animals`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_

  - [ ] 2.4 Create devices app
    - Run `python manage.py startapp devices apps/devices`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_

  - [ ] 2.5 Create monitoring app
    - Run `python manage.py startapp monitoring apps/monitoring`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_

  - [ ] 2.6 Create hormones app
    - Run `python manage.py startapp hormones apps/hormones`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_

  - [ ] 2.7 Create protocols app
    - Run `python manage.py startapp protocols apps/protocols`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_

  - [ ] 2.8 Create alerts app
    - Run `python manage.py startapp alerts apps/alerts`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_

  - [ ] 2.9 Create reports app
    - Run `python manage.py startapp reports apps/reports`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_

  - [ ] 2.10 Create logs app
    - Run `python manage.py startapp logs apps/logs`
    - Add to `INSTALLED_APPS` in settings.py
    - _Requirements: 10.1_


- [ ] 3. Define all database models
  - [ ] 3.1 Create UserProfile model in authentication app
    - Define UserProfile with OneToOneField to Django User
    - Add fields: role, phone, organization, created_at, updated_at
    - _Requirements: 1.1, 10.2_

  - [ ] 3.2 Create Animal model in animals app
    - Define Animal model with all required fields
    - Add fields: animal_id (unique), name, species, breed, age, gender, weight, health_status, reproductive_status, registration_date, created_by (ForeignKey to User)
    - _Requirements: 2.1, 2.7, 10.2, 10.3_

  - [ ] 3.3 Create Device model in devices app
    - Define Device model with all required fields
    - Add fields: device_id (unique), name, device_type, installation_location, status, battery_level, assigned_animal (ForeignKey to Animal), last_communication, registration_date
    - _Requirements: 3.1, 3.6, 10.2, 10.3_

  - [ ] 3.4 Create SensorReading model in monitoring app
    - Define SensorReading model
    - Add fields: device (ForeignKey), animal (ForeignKey), sensor_type, value, unit, timestamp, is_abnormal
    - _Requirements: 4.1, 4.5, 10.2, 10.3_

  - [ ] 3.5 Create HormoneReservoir and HormoneRelease models in hormones app
    - Define HormoneReservoir model with fields: hormone_type, initial_quantity, current_quantity, unit, low_threshold
    - Define HormoneRelease model with fields: reservoir (ForeignKey), animal (ForeignKey), quantity, timestamp, performed_by (ForeignKey to User), notes
    - _Requirements: 5.1, 5.2, 5.6, 10.2, 10.3_

  - [ ] 3.6 Create TreatmentProtocol, ProtocolStep, and TreatmentAssignment models in protocols app
    - Define TreatmentProtocol with fields: name, description, duration_days, created_by (ForeignKey to User)
    - Define ProtocolStep with fields: protocol (ForeignKey), step_number, description, hormone_type, dosage, day_offset, time_of_day
    - Define TreatmentAssignment with fields: protocol (ForeignKey), animal (ForeignKey), start_date, end_date, status, progress, assigned_by (ForeignKey to User)
    - _Requirements: 6.1, 6.4, 6.6, 10.2, 10.3_

  - [ ] 3.7 Create Alert model in alerts app
    - Define Alert model with fields: title, alert_type, severity, description, related_entity_type, related_entity_id, status, timestamp, resolved_at, resolved_by (ForeignKey to User)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 10.2_

  - [ ] 3.8 Create ActivityLog model in logs app
    - Define ActivityLog model with fields: user (ForeignKey), action_type, entity_type, entity_id, description, timestamp, ip_address
    - _Requirements: 1.7, 10.2_


- [ ] 4. Create and apply database migrations
  - Run `python manage.py makemigrations` to generate migration files
  - Run `python manage.py migrate` to apply migrations
  - Verify all tables are created by inspecting database or using Django shell
  - _Requirements: 12.1, 12.2, 12.5, 15.2, 15.5_

- [ ] 5. Configure URL routing structure
  - [ ] 5.1 Set up root URLconf in yaksync_project/urls.py
    - Include authentication app URLs at `/auth/`
    - Include dashboard app URLs at `/` and `/dashboard/`
    - Include animals app URLs at `/animals/`
    - Include devices app URLs at `/devices/`
    - Include monitoring app URLs at `/monitoring/`
    - Include hormones app URLs at `/hormones/`
    - Include protocols app URLs at `/protocols/`
    - Include alerts app URLs at `/alerts/`
    - Include reports app URLs at `/reports/`
    - Include logs app URLs at `/logs/`
    - Configure static and media URL patterns
    - _Requirements: 10.4, 10.10, 11.10_

  - [ ] 5.2 Create urls.py for each Django app
    - Create `apps/authentication/urls.py` with login, logout, register, profile URL patterns
    - Create `apps/dashboard/urls.py` with dashboard URL pattern
    - Create `apps/animals/urls.py` with list, detail, create, update, delete URL patterns
    - Create `apps/devices/urls.py` with list, detail, create, update, assign URL patterns
    - Create `apps/monitoring/urls.py` with dashboard, animal monitoring, data list, chart URL patterns
    - Create `apps/hormones/urls.py` with reservoir and release URL patterns
    - Create `apps/protocols/urls.py` with protocol and assignment URL patterns
    - Create `apps/alerts/urls.py` with list, detail, resolve URL patterns
    - Create `apps/reports/urls.py` with report menu and individual report URL patterns
    - Create `apps/logs/urls.py` with activity log list URL pattern
    - _Requirements: 10.4, 10.9_


- [ ] 6. Implement authentication system
  - [ ] 6.1 Create authentication forms
    - Create LoginForm with username/email and password fields
    - Create RegisterForm with username, email, password, confirm password, first_name, last_name, role fields
    - Add form validation for email format, password strength, matching passwords
    - _Requirements: 1.8, 10.5, 13.1_

  - [ ] 6.2 Implement authentication views
    - Create LoginView to handle GET (display form) and POST (authenticate user)
    - Create LogoutView to terminate session and redirect to login
    - Create RegisterView to handle user registration with UserProfile creation
    - Create ProfileView to display and edit user profile
    - Add CSRF protection to all forms
    - Log login/logout events to ActivityLog
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 14.1, 14.2, 14.5_

  - [ ] 6.3 Create authentication templates
    - Create `templates/authentication/login.html` with centered card layout
    - Create `templates/authentication/register.html` with registration form
    - Create `templates/authentication/profile.html` with profile display and edit form
    - Style with professional blue theme, clean typography, centered cards
    - Add form validation error display
    - _Requirements: 11.1, 11.3, 11.7, 11.8_

  - [ ]* 6.4 Write unit tests for authentication
    - Test user registration creates User and UserProfile
    - Test login with valid credentials creates session
    - Test login with invalid credentials shows error
    - Test logout clears session
    - Test form validation rules
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 15.4_


- [ ] 7. Create base template system and static assets
  - [ ] 7.1 Create base.html master template
    - Define HTML structure with head, body sections
    - Include title block, extra_css block, content block, auth_content block, extra_js block
    - Add conditional layout (authenticated: sidebar+navbar+content, unauthenticated: auth_content)
    - Load static files with {% static %} tags
    - _Requirements: 10.7, 10.9, 11.1, 11.2_

  - [ ] 7.2 Create sidebar include template
    - Create `templates/includes/sidebar.html`
    - Add platform logo and name
    - Add navigation menu with links to all sections: Dashboard, Animals, Devices, Monitoring, Hormones, Protocols, Alerts, Reports, Logs
    - Use {% url %} tags for all navigation links
    - Add active state styling for current page
    - Style with white text on dark blue background
    - _Requirements: 10.9, 11.2, 11.10_

  - [ ] 7.3 Create navbar include template
    - Create `templates/includes/navbar.html`
    - Add breadcrumb navigation
    - Add search bar placeholder
    - Add user profile dropdown with Profile and Logout links
    - Style with white background and blue accents
    - _Requirements: 11.2, 11.10_

  - [ ] 7.4 Create base.css with global styles
    - Define CSS variables for colors, sizes, spacing
    - Style layout (sidebar, navbar, main-content, content area)
    - Style cards, forms, buttons, tables
    - Add responsive design media queries
    - Use white background, blue theme (#2c3e50 primary, #3498db accent)
    - _Requirements: 11.3, 11.4, 11.5, 11.6, 11.8_

  - [ ] 7.5 Create auth.css for authentication pages
    - Style centered card layout for login/register pages
    - Add background gradient
    - Style form inputs, labels, buttons
    - Add hover and focus states
    - _Requirements: 11.3, 11.7, 11.8_

  - [ ] 7.6 Create main.js for global JavaScript
    - Add sidebar navigation active state handling
    - Add form validation helpers
    - Add dropdown menu toggle functionality
    - Use vanilla JavaScript (no frameworks)
    - _Requirements: 11.9_


- [ ] 8. Checkpoint - Verify authentication and base templates
  - Start development server with `python manage.py runserver`
  - Test registration flow: create new user, verify UserProfile created in database
  - Test login flow: log in with credentials, verify session created
  - Test logout flow: log out, verify session cleared
  - Verify base template renders with sidebar and navbar for authenticated users
  - Verify login page renders with centered card layout for unauthenticated users
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 15.3, 15.4_

- [ ] 9. Implement dashboard views and templates
  - [ ] 9.1 Create DashboardView
    - Query and aggregate statistics from all apps
    - Calculate: total animals, active devices, recent alerts, hormone levels, pending treatments, recent activities
    - Pass context to template
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

  - [ ] 9.2 Create dashboard template
    - Create `templates/dashboard/index.html` extending base.html
    - Display metric cards in 2x4 grid (responsive)
    - Display recent alerts list
    - Display recent activities list
    - Add quick action buttons
    - Style with card-based layout and blue theme
    - _Requirements: 11.1, 11.3, 11.4, 11.5_

  - [ ]* 9.3 Write unit tests for dashboard
    - Test DashboardView returns correct statistics
    - Test with empty database (all counts zero)
    - Test with sample data (correct aggregation)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_


- [ ] 10. Implement Animals app CRUD operations
  - [ ] 10.1 Create AnimalForm
    - Create ModelForm for Animal model
    - Include all required fields with appropriate widgets
    - Add form validation for animal_id uniqueness, age range, weight range
    - _Requirements: 2.8, 10.5, 13.1, 13.5_

  - [ ] 10.2 Implement Animals views
    - Create AnimalListView with pagination, search, filtering
    - Create AnimalDetailView to display animal information
    - Create AnimalCreateView to create new animal
    - Create AnimalUpdateView to edit animal
    - Create AnimalDeleteView with confirmation
    - Log all create/update/delete actions to ActivityLog
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 10.6_

  - [ ] 10.3 Create Animals templates
    - Create `animals/animal_list.html` with search, filter, table, pagination
    - Create `animals/animal_detail.html` with animal information cards
    - Create `animals/animal_form.html` for create/edit with form layout
    - Create `animals/animal_confirm_delete.html` for deletion confirmation
    - Style with professional card-based layout
    - _Requirements: 11.1, 11.4, 11.5_

  - [ ]* 10.4 Write unit tests for Animals app
    - Test animal creation stores correct data
    - Test animal update modifies data
    - Test animal deletion removes record
    - Test animal_id uniqueness constraint
    - Test search and filter functionality
    - _Requirements: 2.1, 2.3, 2.4, 2.7, 13.2_


- [ ] 11. Implement Devices app CRUD operations
  - [ ] 11.1 Create DeviceForm and DeviceAssignForm
    - Create ModelForm for Device model
    - Create form for device assignment to animals
    - Add validation for device_id uniqueness, battery_level range
    - _Requirements: 3.1, 3.6, 3.7, 10.5, 13.1_

  - [ ] 11.2 Implement Devices views
    - Create DeviceListView with status indicators
    - Create DeviceDetailView with assigned animal and communication history
    - Create DeviceCreateView to register new device
    - Create DeviceUpdateView to edit device configuration
    - Create DeviceAssignView to assign device to animal
    - Update last_communication timestamp when device communicates
    - Log all actions to ActivityLog
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.7, 10.6_

  - [ ] 11.3 Create Devices templates
    - Create `devices/device_list.html` with status indicators
    - Create `devices/device_detail.html` with device info and assigned animal
    - Create `devices/device_form.html` for create/edit
    - Create `devices/device_assign.html` for assignment
    - Style with card-based layout and status color coding
    - _Requirements: 11.1, 11.4_

  - [ ]* 11.4 Write unit tests for Devices app
    - Test device creation stores correct data
    - Test device assignment creates relationship
    - Test device_id uniqueness constraint
    - Test battery_level validation
    - _Requirements: 3.1, 3.2, 3.6, 13.2, 13.5_


- [ ] 12. Implement Monitoring app for sensor data
  - [ ] 12.1 Create SensorReading form (if needed for manual entry)
    - Create ModelForm for SensorReading
    - Add validation for value ranges by sensor_type
    - _Requirements: 4.6, 10.5_

  - [ ] 12.2 Implement Monitoring views
    - Create MonitoringDashboardView for overview
    - Create AnimalMonitoringView for animal-specific sensor data
    - Create SensorDataListView with date range filtering
    - Create SensorDataChartView to return JSON for charts
    - Calculate trends and statistics from readings
    - _Requirements: 4.2, 4.3, 4.4, 10.6_

  - [ ] 12.3 Create Monitoring templates
    - Create `monitoring/dashboard.html` for overview
    - Create `monitoring/animal_monitoring.html` with charts and data tables
    - Create `monitoring/sensor_data_list.html` with filtering
    - Add JavaScript for chart rendering (vanilla JS)
    - Style with card-based layout
    - _Requirements: 11.1, 11.4, 11.9_

  - [ ]* 12.4 Write unit tests for Monitoring app
    - Test sensor reading storage
    - Test data retrieval and filtering
    - Test statistics calculation
    - Test foreign key relationships to Device and Animal
    - _Requirements: 4.1, 4.2, 4.3, 4.7, 13.3_


- [ ] 13. Implement Hormones app
  - [ ] 13.1 Create HormoneReservoir and HormoneRelease forms
    - Create ModelForm for HormoneReservoir
    - Create form for HormoneRelease with animal selection
    - Add validation for quantities and thresholds
    - _Requirements: 5.1, 5.5, 10.5, 13.1_

  - [ ] 13.2 Implement Hormones views
    - Create HormoneReservoirListView
    - Create HormoneReservoirDetailView with release history
    - Create HormoneReservoirCreateView
    - Create HormoneReservoirUpdateView
    - Create HormoneReleaseCreateView (decrement reservoir, create release record, check threshold, generate alert if needed)
    - Use transaction.atomic() for release operation
    - Log all actions to ActivityLog
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 10.6_

  - [ ] 13.3 Create Hormones templates
    - Create `hormones/reservoir_list.html` with current quantities
    - Create `hormones/reservoir_detail.html` with release history table
    - Create `hormones/reservoir_form.html` for create/edit
    - Create `hormones/release_form.html` for recording releases
    - Style with card layout and quantity indicators
    - _Requirements: 11.1, 11.4_

  - [ ]* 13.4 Write unit tests for Hormones app
    - Test reservoir creation
    - Test release decrements current_quantity
    - Test release creates HormoneRelease record
    - Test low threshold generates alert
    - Test transaction rollback on failure
    - _Requirements: 5.2, 5.3, 5.7, 13.1_


- [ ] 14. Implement Protocols app
  - [ ] 14.1 Create Protocol and Assignment forms
    - Create ModelForm for TreatmentProtocol
    - Create inline formset for ProtocolStep
    - Create form for TreatmentAssignment
    - Add validation for dates, dosages, step sequences
    - _Requirements: 6.1, 6.4, 10.5_

  - [ ] 14.2 Implement Protocols views
    - Create ProtocolListView
    - Create ProtocolDetailView with steps
    - Create ProtocolCreateView with inline step formset
    - Create ProtocolUpdateView
    - Create ProtocolAssignView to assign protocol to animal
    - Create AssignmentListView to view all assignments
    - Create AssignmentUpdateView to update progress and status
    - Log all actions to ActivityLog
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7, 10.6_

  - [ ] 14.3 Create Protocols templates
    - Create `protocols/protocol_list.html`
    - Create `protocols/protocol_detail.html` with steps table
    - Create `protocols/protocol_form.html` with inline step formset
    - Create `protocols/protocol_assign.html`
    - Create `protocols/assignment_list.html` with progress indicators
    - Create `protocols/assignment_form.html` for updating progress
    - Style with card layout and progress bars
    - _Requirements: 11.1, 11.4_

  - [ ]* 14.4 Write unit tests for Protocols app
    - Test protocol creation with steps
    - Test protocol assignment creates relationship
    - Test assignment status updates
    - Test many-to-many relationship between protocols and animals
    - _Requirements: 6.1, 6.4, 6.5, 6.6_


- [ ] 15. Implement Alerts app
  - [ ] 15.1 Implement alert generation logic
    - Create utility functions to generate alerts for different conditions
    - Low hormone level (check in HormoneRelease view)
    - Device disconnection (check last_communication timestamp)
    - Low battery (check battery_level)
    - Abnormal reading (check is_abnormal in SensorReading)
    - Missed schedule (check treatment assignments)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ] 15.2 Implement Alerts views
    - Create AlertListView with filtering by type, severity, status
    - Create AlertDetailView
    - Create AlertResolveView to mark alert as resolved
    - Log resolution to ActivityLog
    - _Requirements: 7.7, 7.8, 10.6_

  - [ ] 15.3 Create Alerts templates
    - Create `alerts/alert_list.html` with filter controls and severity color coding
    - Create `alerts/alert_detail.html`
    - Style with card layout and color-coded severity indicators
    - _Requirements: 11.1, 11.4_

  - [ ]* 15.4 Write unit tests for Alerts app
    - Test alert creation for each alert type
    - Test alert resolution updates status and timestamp
    - Test filtering by type, severity, status
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_


- [ ] 16. Implement Reports app
  - [ ] 16.1 Implement report generation views
    - Create ReportListView (report menu)
    - Create AnimalHealthReportView with filtering and data aggregation
    - Create TreatmentHistoryReportView with filtering
    - Create HormoneUsageReportView with statistics
    - Create DevicePerformanceReportView with uptime analysis
    - Create SensorDataReportView with aggregation and trends
    - Create UserActivityReportView with filtering
    - All reports query real data from database
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

  - [ ] 16.2 Create Reports templates
    - Create `reports/report_list.html` as report menu with cards for each report type
    - Create `reports/animal_health.html` with filter form and data table
    - Create `reports/treatment_history.html` with filter form and data table
    - Create `reports/hormone_usage.html` with statistics and charts
    - Create `reports/device_performance.html` with statistics and charts
    - Create `reports/sensor_data.html` with filter form, aggregation, and charts
    - Create `reports/user_activity.html` with filter form and activity log table
    - Style with card layout and data visualization
    - _Requirements: 11.1, 11.4_

  - [ ]* 16.3 Write unit tests for Reports app
    - Test each report view returns correct data
    - Test filtering functionality for each report
    - Test aggregation calculations
    - Test with empty database and with sample data
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.8_


- [ ] 17. Implement Logs app
  - [ ] 17.1 Implement activity logging functionality
    - Create utility function to log user activities
    - Capture: user, action_type, entity_type, entity_id, description, timestamp, ip_address
    - Integrate logging into all create/update/delete views across apps
    - _Requirements: 1.7, 10.2_

  - [ ] 17.2 Implement Logs views
    - Create ActivityLogListView with filtering by user, action_type, entity_type, date range
    - Display logs in reverse chronological order
    - _Requirements: 10.6_

  - [ ] 17.3 Create Logs templates
    - Create `logs/activity_log_list.html` with filter controls and activity table
    - Display timestamp, user, action, entity, description
    - Style with card layout and clear table formatting
    - _Requirements: 11.1, 11.4_

  - [ ]* 17.4 Write unit tests for Logs app
    - Test activity logging records correct data
    - Test filtering functionality
    - Test logging for different action types
    - _Requirements: 1.7_

- [ ] 18. Create error page templates
  - Create `templates/errors/404.html` with helpful navigation links
  - Create `templates/errors/500.html` with generic error message
  - Configure Django to use custom error templates
  - Style error pages consistently with site theme
  - _Requirements: 11.1_


- [ ] 19. Configure Django admin interface (optional but recommended)
  - Register all models in each app's admin.py
  - Customize admin list displays and filters
  - Configure search fields for key models
  - Create superuser for admin access
  - _Requirements: 15.5_

- [ ] 20. Add security configuration
  - [ ] 20.1 Configure session security
    - Set SESSION_COOKIE_SECURE = True for production
    - Set SESSION_COOKIE_HTTPONLY = True
    - Configure SESSION_COOKIE_AGE for session timeout
    - Enable session key regeneration on login
    - _Requirements: 14.3, 14.4, 14.5, 14.6_

  - [ ] 20.2 Configure CSRF protection
    - Verify CSRF middleware is enabled
    - Ensure all forms include {% csrf_token %}
    - Configure CSRF_COOKIE_SECURE for production
    - _Requirements: 1.5, 13.7_

  - [ ] 20.3 Configure database security
    - Verify foreign key constraints are working
    - Test CASCADE and SET_NULL delete behaviors
    - Verify unique constraints are enforced
    - _Requirements: 13.2, 13.3, 13.4_

- [ ] 21. Final integration and testing checkpoint
  - Start development server and verify all pages render correctly
  - Test complete user flow: register → login → navigate all sections → logout
  - Test CRUD operations for all entities (animals, devices, protocols, etc.)
  - Test relationships (assign device to animal, assign protocol to animal, etc.)
  - Test alert generation triggers
  - Test activity logging for all actions
  - Verify all navigation links work using {% url %} tags
  - Verify static files load correctly (CSS, JS)
  - Check for console errors in browser
  - Verify responsive design on different screen sizes
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 15.1, 15.3, 15.4, 15.6_


## Notes

- Tasks marked with `*` are optional testing tasks that can be skipped for faster MVP delivery
- Each task references specific requirements from requirements.md for traceability
- Checkpoints (tasks 8 and 21) ensure incremental validation before proceeding
- The implementation follows Django best practices with MVT pattern, ORM usage, and template inheritance
- All navigation uses Django's {% url %} template tags for maintainability
- All static assets use {% static %} template tags
- Database schema is designed for SQLite (development) with PostgreSQL compatibility
- Phase 1 delivers a complete working application with all CRUD operations and professional UI
- Future phases can add IoT integration, real-time data collection, advanced analytics, and API development

## Success Criteria

Upon completion of all tasks, the system should:
- ✅ Have Django project with 10 apps installed and configured
- ✅ Have complete database schema with all models and migrations applied
- ✅ Support user registration, login, and logout with session management
- ✅ Render all pages with professional blue-themed UI using base template system
- ✅ Display working sidebar navigation and top navbar for authenticated users
- ✅ Provide CRUD operations for animals, devices, protocols, hormone reservoirs
- ✅ Display dashboard with system statistics and recent activities
- ✅ Store and display sensor readings for animals
- ✅ Generate and display alerts based on system conditions
- ✅ Generate reports with real data from the database
- ✅ Log all user activities to ActivityLog
- ✅ Run without errors on development server
- ✅ Follow Django best practices and be ready for Phase 2 IoT integration
