# Project Description

Our project aims to develop an interactive attendance application tailored for educational institutions, similar to TopHat. Leveraging the precision of a Geolocation API, the app will ensure that students are within the vicinity of the lecture hall to mark attendance, enhancing the reliability of the process. Additionally, incorporating a QR code API will allow for a secondary attendance verification, wherein a QR code displayed during the lecture can be scanned by students as proof of attendance. To streamline user access, the app will integrate third-party OAuth for secure authentication using school email accounts. A robust database will be employed to maintain records of user profiles, attendance logs, class schedules, and geolocation coordinates, ensuring data integrity and easy retrieval for reporting purposes. Our solution is designed to simplify attendance tracking, reduce administrative workload, and provide a seamless user experience for both students and educators.

# Product Requirements

**Goal**: Develop an attendance app that accurately verifies the presence of students in a classroom through Geolocation and QR code scanning, with an emphasis on ease of use and security.

**Non-Goal**: The application will not serve as a multipurpose educational platform for assignments, tests, or any non-attendance related activities.

### Non-Functional Requirement 1: Usability

**Functional Requirements**:

- The app must provide a simple and intuitive user interface for both students and lecturers to engage with minimal training.
- The app must be accessible and fully functional on a variety of devices including smartphones, tablets, and computers.

### Non-Functional Requirement 2: Security

**Functional Requirements**:

- Implement OAuth 2.0 for secure authentication using school-provided email accounts to prevent unauthorized access.
- Encrypt sensitive data such as geolocation details and personal information in transit and at rest within the app’s database.

# Project Management

**Theme**: Efficient and Secure Attendance Verification

**Epic**: Attendance System Implementation

### User Story 1: As a student, I want to check into my class with one click on my phone, so that I can confirm my attendance without disrupting my focus on the lecture.

**Task**: Implement Geolocation API

**Ticket 1**: Geolocation Accuracy Improvement

- Enhance the precision of the Geolocation API to ensure it accurately reflects the students’ presence in the lecture hall.

**Ticket 2**: Geolocation User Interface Design

- Design a user-friendly interface for students to enable geolocation services and check into their classes on the app.

### User Story 2: As a faculty member, I want a simple way to generate and display a QR code for my lecture, so that I can efficiently track which students are physically present.

**Task**: Implement QR Code Generation and Scanning

**Ticket 1**: QR Code Generation Mechanism

- Develop a system for generating unique QR codes for each class session that can be displayed to students.

**Ticket 2**: QR Code Scanning Integration

- Integrate a QR code scanning function within the app that allows students to quickly scan the code displayed during the lecture for attendance.

# Database

**User Data**: Securely store student and faculty profiles with authentication details.

**Class Data**: Include course schedules, location information, and associated geolocation coordinates.

**Attendance Data**: Record attendance timestamps, methods (Geolocation or QR), attendance scores, and attendance status.

**System Logs**: Keep logs of system usage, errors, and access attempts for security and auditing purposes.