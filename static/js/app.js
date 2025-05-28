/**
 * Team Picker Application
 * Modular JavaScript application following Single Responsibility Principle
 */

import {
    API_ENDPOINTS,
    FILE_CONFIG,
    UI_CONFIG,
    DEFAULTS,
    STATUS_MESSAGES,
    ELEMENT_IDS,
    CSS_CLASSES,
    ASSIGNMENT_LABELS,
    ASSIGNMENT_PLACEHOLDERS,
} from './config.js';

/**
 * Handles DOM element selection and caching
 */
class DOMManager {
    constructor() {
        this.elements = {};
        this.initializeElements();
    }

    initializeElements() {
        Object.entries(ELEMENT_IDS).forEach(([key, id]) => {
            this.elements[key] = document.getElementById(id);
        });
    }

    get(elementKey) {
        return this.elements[elementKey];
    }

    show(elementKey) {
        this.get(elementKey)?.classList.remove(CSS_CLASSES.HIDDEN);
    }

    hide(elementKey) {
        this.get(elementKey)?.classList.add(CSS_CLASSES.HIDDEN);
    }

    setContent(elementKey, content) {
        const element = this.get(elementKey);
        if (element) element.innerHTML = content;
    }

    setText(elementKey, text) {
        const element = this.get(elementKey);
        if (element) element.textContent = text;
    }

    setAttribute(elementKey, attribute, value) {
        const element = this.get(elementKey);
        if (element) element.setAttribute(attribute, value);
    }

    getValue(elementKey) {
        const element = this.get(elementKey);
        return element ? element.value : null;
    }

    setValue(elementKey, value) {
        const element = this.get(elementKey);
        if (element) element.value = value;
    }
}

/**
 * Handles status messages and notifications
 */
class StatusManager {
    static showStatus(element, message, type) {
        if (element) {
            element.innerHTML = `<div class="${CSS_CLASSES.STATUS_MESSAGE} status-${type}">${message}</div>`;
        }
    }

    static clearStatus(element) {
        if (element) {
            element.innerHTML = '';
        }
    }

    static setLoading(textElement, loadingElement, isLoading) {
        if (textElement && loadingElement) {
            if (isLoading) {
                textElement.classList.add(CSS_CLASSES.HIDDEN);
                loadingElement.classList.remove(CSS_CLASSES.HIDDEN);
            } else {
                textElement.classList.remove(CSS_CLASSES.HIDDEN);
                loadingElement.classList.add(CSS_CLASSES.HIDDEN);
            }
        }
    }
}

/**
 * Handles file operations and validation
 */
class FileManager {
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    static validateFile(file) {
        if (!file) return { valid: false, error: 'No file selected' };

        if (file.size > FILE_CONFIG.MAX_FILE_SIZE) {
            return { valid: false, error: 'File size exceeds 5MB limit' };
        }

        const extension = file.name.split('.').pop().toLowerCase();
        if (!FILE_CONFIG.SUPPORTED_EXTENSIONS.includes(extension)) {
            return { valid: false, error: 'Only .txt and .rtf files are supported' };
        }

        return { valid: true };
    }
}

/**
 * Handles API communication
 */
class APIService {
    static async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(API_ENDPOINTS.UPLOAD, {
            method: 'POST',
            body: formData,
        });

        return await response.json();
    }

    static async loadSampleData() {
        const response = await fetch(API_ENDPOINTS.SAMPLE_DATA);
        return await response.json();
    }

    static async createTeams(students, method, value) {
        const response = await fetch(API_ENDPOINTS.CREATE_TEAMS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                students: students,
                method: method,
                value: parseInt(value),
            }),
        });

        return await response.json();
    }
}

/**
 * Handles student data display and management
 */
class StudentManager {
    constructor(domManager) {
        this.domManager = domManager;
        this.students = [];
    }

    setStudents(students) {
        this.students = students;
        this.displayStudents();
    }

    getStudents() {
        return this.students;
    }

    displayStudents() {
        const count = this.students.length;
        this.domManager.setText('STUDENT_COUNT', `${count} students ready for team assignment`);

        const studentListHTML = this.students
            .map(
                (student, index) =>
                    `<div class="${CSS_CLASSES.STUDENT_ITEM}">
                <div class="${CSS_CLASSES.MEMBER_NAME}">${index + 1}. ${student.name}</div>
                <div class="${CSS_CLASSES.MEMBER_EMAIL}">${student.email}</div>
            </div>`
            )
            .join('');

        this.domManager.setContent('STUDENT_LIST', studentListHTML);
        this.domManager.show('STUDENTS_PREVIEW');
        this.domManager.show('TEAM_CONFIG');
    }

    clear() {
        this.students = [];
        this.domManager.hide('STUDENTS_PREVIEW');
        this.domManager.hide('TEAM_CONFIG');
        this.domManager.hide('RESULTS_SECTION');
    }
}

/**
 * Handles team assignment configuration and display
 */
class TeamManager {
    constructor(domManager) {
        this.domManager = domManager;
        this.currentTimestamp = null;
    }

    updateMethodLabel() {
        const method = this.domManager.getValue('ASSIGNMENT_METHOD');
        const label = ASSIGNMENT_LABELS[method];
        const placeholder = ASSIGNMENT_PLACEHOLDERS[method];

        this.domManager.setText('VALUE_LABEL', label);
        this.domManager.setAttribute('ASSIGNMENT_VALUE', 'placeholder', placeholder);
    }

    displayResults(data) {
        const { teams, metadata, image_base64, download_links } = data;
        this.currentTimestamp = metadata.timestamp;

        // Update results subtitle
        const subtitle = `${metadata.num_teams} teams • ${
            metadata.total_students
        } students • ${metadata.method.replace('_', ' ')}`;
        this.domManager.setText('RESULTS_SUBTITLE', subtitle);

        // Display teams
        const teamsHTML = teams
            .map(
                (team) => `
            <div class="${CSS_CLASSES.TEAM_CARD}">
                <div class="${CSS_CLASSES.TEAM_HEADER}">
                    <div class="${CSS_CLASSES.TEAM_NUMBER}">Team ${team.team_number}</div>
                    <div class="${CSS_CLASSES.TEAM_SIZE}">${team.size} members</div>
                </div>
                <ul class="${CSS_CLASSES.TEAM_MEMBERS}">
                    ${team.members
                        .map(
                            (member) => `
                        <li class="${CSS_CLASSES.TEAM_MEMBER}">
                            <div class="${CSS_CLASSES.MEMBER_NAME}">${member.name}</div>
                            <div class="${CSS_CLASSES.MEMBER_EMAIL}">${member.email}</div>
                        </li>
                    `
                        )
                        .join('')}
                </ul>
            </div>
        `
            )
            .join('');

        this.domManager.setContent('TEAMS_CONTAINER', teamsHTML);

        // Display image
        this.domManager.setAttribute('TEAM_IMAGE', 'src', `data:image/png;base64,${image_base64}`);

        // Set download links
        this.domManager.setAttribute('DOWNLOAD_JSON', 'href', download_links.json);
        this.domManager.setAttribute('DOWNLOAD_IMAGE', 'href', download_links.image);

        // Show results
        this.domManager.show('RESULTS_SECTION');
        this.domManager
            .get('RESULTS_SECTION')
            .scrollIntoView({ behavior: UI_CONFIG.SCROLL_BEHAVIOR });
    }
}

/**
 * Handles file upload UI and interactions
 */
class FileUploadManager {
    constructor(domManager, studentManager) {
        this.domManager = domManager;
        this.studentManager = studentManager;
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.domManager.get('FILE_INPUT').addEventListener('change', () => this.handleFileSelect());
        this.domManager
            .get('REMOVE_FILE')
            .addEventListener('click', () => this.removeSelectedFile());
    }

    handleFileSelect() {
        const file = this.domManager.get('FILE_INPUT').files[0];
        const uploadBtn = this.domManager.get('UPLOAD_BTN');

        uploadBtn.disabled = !file;
        StatusManager.clearStatus(this.domManager.get('UPLOAD_STATUS'));

        if (file) {
            const validation = FileManager.validateFile(file);
            if (!validation.valid) {
                StatusManager.showStatus(
                    this.domManager.get('UPLOAD_STATUS'),
                    STATUS_MESSAGES.UPLOAD_ERROR(validation.error),
                    'error'
                );
                this.removeSelectedFile();
                return;
            }

            // Show selected file info
            this.domManager.setText('SELECTED_FILE_NAME', file.name);
            this.domManager.setText('SELECTED_FILE_SIZE', FileManager.formatFileSize(file.size));
            this.domManager.show('SELECTED_FILE');
            this.domManager.hide('FILE_UPLOAD_LABEL');
        } else {
            this.removeSelectedFile();
        }
    }

    async handleFileUpload() {
        const file = this.domManager.get('FILE_INPUT').files[0];
        if (!file) return;

        const uploadBtn = this.domManager.get('UPLOAD_BTN');
        StatusManager.setLoading(
            this.domManager.get('UPLOAD_TEXT'),
            this.domManager.get('UPLOAD_LOADING'),
            true
        );
        uploadBtn.disabled = true;

        try {
            const data = await APIService.uploadFile(file);

            if (data.success) {
                this.studentManager.setStudents(data.students);
                const fileType = data.file_type ? ` (${data.file_type} file)` : '';
                StatusManager.showStatus(
                    this.domManager.get('UPLOAD_STATUS'),
                    STATUS_MESSAGES.UPLOAD_SUCCESS(data.count, fileType),
                    'success'
                );

                this.domManager.setText('UPLOAD_TEXT', 'Upload Another File');
            } else {
                StatusManager.showStatus(
                    this.domManager.get('UPLOAD_STATUS'),
                    STATUS_MESSAGES.UPLOAD_ERROR(data.error),
                    'error'
                );
                this.removeSelectedFile();
            }
        } catch (error) {
            StatusManager.showStatus(
                this.domManager.get('UPLOAD_STATUS'),
                STATUS_MESSAGES.UPLOAD_FAILED(error.message),
                'error'
            );
            this.removeSelectedFile();
        } finally {
            StatusManager.setLoading(
                this.domManager.get('UPLOAD_TEXT'),
                this.domManager.get('UPLOAD_LOADING'),
                false
            );
            uploadBtn.disabled = false;
        }
    }

    async loadSampleData() {
        StatusManager.setLoading(
            this.domManager.get('UPLOAD_TEXT'),
            this.domManager.get('UPLOAD_LOADING'),
            true
        );

        try {
            const data = await APIService.loadSampleData();

            if (data.success) {
                this.studentManager.setStudents(data.students);
                StatusManager.showStatus(
                    this.domManager.get('UPLOAD_STATUS'),
                    STATUS_MESSAGES.SAMPLE_LOADED(data.count),
                    'success'
                );
            }
        } catch (error) {
            StatusManager.showStatus(
                this.domManager.get('UPLOAD_STATUS'),
                STATUS_MESSAGES.SAMPLE_FAILED(error.message),
                'error'
            );
        } finally {
            StatusManager.setLoading(
                this.domManager.get('UPLOAD_TEXT'),
                this.domManager.get('UPLOAD_LOADING'),
                false
            );
        }
    }

    removeSelectedFile() {
        this.domManager.get('FILE_INPUT').value = '';
        this.domManager.get('UPLOAD_BTN').disabled = true;
        this.domManager.setText('UPLOAD_TEXT', 'Upload File');
        this.studentManager.clear();
        StatusManager.clearStatus(this.domManager.get('UPLOAD_STATUS'));
        this.domManager.hide('SELECTED_FILE');
        this.domManager.show('FILE_UPLOAD_LABEL');
    }
}

/**
 * Main Application Controller
 * Coordinates all managers and handles application lifecycle
 */
class TeamPickerApp {
    constructor() {
        this.domManager = new DOMManager();
        this.studentManager = new StudentManager(this.domManager);
        this.teamManager = new TeamManager(this.domManager);
        this.fileUploadManager = new FileUploadManager(this.domManager, this.studentManager);

        this.initialize();
    }

    initialize() {
        this.setupEventListeners();
        this.teamManager.updateMethodLabel();
    }

    setupEventListeners() {
        // File upload events
        this.domManager
            .get('UPLOAD_BTN')
            .addEventListener('click', () => this.fileUploadManager.handleFileUpload());

        this.domManager
            .get('SAMPLE_BTN')
            .addEventListener('click', () => this.fileUploadManager.loadSampleData());

        // Team configuration events
        this.domManager
            .get('ASSIGNMENT_METHOD')
            .addEventListener('change', () => this.teamManager.updateMethodLabel());

        this.domManager.get('CREATE_TEAMS_BTN').addEventListener('click', () => this.createTeams());
    }

    async createTeams() {
        const students = this.studentManager.getStudents();
        if (!students.length) return;

        const createBtn = this.domManager.get('CREATE_TEAMS_BTN');
        StatusManager.setLoading(
            this.domManager.get('CREATE_TEXT'),
            this.domManager.get('CREATE_LOADING'),
            true
        );
        createBtn.disabled = true;
        StatusManager.clearStatus(this.domManager.get('TEAM_STATUS'));

        try {
            const method = this.domManager.getValue('ASSIGNMENT_METHOD');
            const value = this.domManager.getValue('ASSIGNMENT_VALUE');

            const data = await APIService.createTeams(students, method, value);

            if (data.success) {
                this.teamManager.displayResults(data);
                StatusManager.showStatus(
                    this.domManager.get('TEAM_STATUS'),
                    STATUS_MESSAGES.TEAMS_SUCCESS(data.teams.length),
                    'success'
                );
            } else {
                StatusManager.showStatus(
                    this.domManager.get('TEAM_STATUS'),
                    STATUS_MESSAGES.TEAMS_ERROR(data.error),
                    'error'
                );
            }
        } catch (error) {
            StatusManager.showStatus(
                this.domManager.get('TEAM_STATUS'),
                STATUS_MESSAGES.TEAMS_FAILED(error.message),
                'error'
            );
        } finally {
            StatusManager.setLoading(
                this.domManager.get('CREATE_TEXT'),
                this.domManager.get('CREATE_LOADING'),
                false
            );
            createBtn.disabled = false;
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TeamPickerApp();
});
