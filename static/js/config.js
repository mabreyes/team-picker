/**
 * Application Configuration
 * Contains all constants, API endpoints, and configuration settings
 */

// API Endpoints
export const API_ENDPOINTS = {
    UPLOAD: '/api/upload',
    SAMPLE_DATA: '/api/sample-data',
    CREATE_TEAMS: '/api/create-teams',
};

// File Configuration
export const FILE_CONFIG = {
    ACCEPTED_TYPES: '.txt,.rtf',
    MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
    SUPPORTED_EXTENSIONS: ['txt', 'rtf'],
};

// UI Configuration
export const UI_CONFIG = {
    ANIMATION_DURATION: 200,
    SCROLL_BEHAVIOR: 'smooth',
    MAX_STUDENTS_DISPLAY: 200,
    STUDENT_LIST_MAX_HEIGHT: '200px',
};

// Default Values
export const DEFAULTS = {
    ASSIGNMENT_METHOD: 'by_count',
    ASSIGNMENT_VALUE: 4,
    MIN_ASSIGNMENT_VALUE: 1,
};

// Status Messages
export const STATUS_MESSAGES = {
    UPLOAD_SUCCESS: (count, fileType) =>
        `✅ Successfully loaded ${count} students${fileType ? ` (${fileType} file)` : ''}`,
    UPLOAD_ERROR: (error) => `❌ ${error}`,
    UPLOAD_FAILED: (error) => `❌ Upload failed: ${error}`,
    SAMPLE_LOADED: (count) => `✅ Loaded ${count} sample students`,
    SAMPLE_FAILED: (error) => `❌ Failed to load sample data: ${error}`,
    TEAMS_SUCCESS: (count) => `✅ Successfully created ${count} teams`,
    TEAMS_ERROR: (error) => `❌ ${error}`,
    TEAMS_FAILED: (error) => `❌ Failed to create teams: ${error}`,
};

// DOM Element IDs
export const ELEMENT_IDS = {
    // File Upload
    FILE_INPUT: 'fileInput',
    UPLOAD_BTN: 'uploadBtn',
    SAMPLE_BTN: 'sampleBtn',
    UPLOAD_TEXT: 'uploadText',
    UPLOAD_LOADING: 'uploadLoading',
    UPLOAD_STATUS: 'uploadStatus',
    FILE_UPLOAD_LABEL: 'fileUploadLabel',
    SELECTED_FILE: 'selectedFile',
    SELECTED_FILE_NAME: 'selectedFileName',
    SELECTED_FILE_SIZE: 'selectedFileSize',
    REMOVE_FILE: 'removeFile',

    // Students Preview
    STUDENTS_PREVIEW: 'studentsPreview',
    STUDENT_COUNT: 'studentCount',
    STUDENT_LIST: 'studentList',

    // Team Configuration
    TEAM_CONFIG: 'teamConfig',
    ASSIGNMENT_METHOD: 'assignmentMethod',
    ASSIGNMENT_VALUE: 'assignmentValue',
    VALUE_LABEL: 'valueLabel',
    CREATE_TEAMS_BTN: 'createTeamsBtn',
    CREATE_TEXT: 'createText',
    CREATE_LOADING: 'createLoading',
    TEAM_STATUS: 'teamStatus',

    // Results
    RESULTS_SECTION: 'resultsSection',
    RESULTS_SUBTITLE: 'resultsSubtitle',
    TEAMS_CONTAINER: 'teamsContainer',
    TEAM_IMAGE: 'teamImage',
    DOWNLOAD_JSON: 'downloadJson',
    DOWNLOAD_IMAGE: 'downloadImage',
};

// CSS Classes
export const CSS_CLASSES = {
    HIDDEN: 'hidden',
    LOADING: 'loading',
    STATUS_MESSAGE: 'status-message',
    STATUS_SUCCESS: 'status-success',
    STATUS_ERROR: 'status-error',
    STATUS_WARNING: 'status-warning',
    STUDENT_ITEM: 'student-item',
    MEMBER_NAME: 'member-name',
    MEMBER_EMAIL: 'member-email',
    TEAM_CARD: 'team-card',
    TEAM_HEADER: 'team-header',
    TEAM_NUMBER: 'team-number',
    TEAM_SIZE: 'team-size',
    TEAM_MEMBERS: 'team-members',
    TEAM_MEMBER: 'team-member',
};

// Assignment Method Labels
export const ASSIGNMENT_LABELS = {
    by_count: 'Number of Teams',
    by_size: 'Team Size',
};

// Assignment Method Placeholders
export const ASSIGNMENT_PLACEHOLDERS = {
    by_count: 'e.g., 6',
    by_size: 'e.g., 4',
};
