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

    static async createManualStudents(emails) {
        const response = await fetch(API_ENDPOINTS.MANUAL_STUDENTS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                emails: emails,
            }),
        });

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
        this.isEditMode = false;
        this.originalStudents = []; // Backup for cancel functionality
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Edit mode controls
        this.domManager
            .get('EDIT_STUDENTS_BTN')
            .addEventListener('click', () => this.enterEditMode());
        this.domManager
            .get('CLEAR_STUDENTS_BTN')
            .addEventListener('click', () => this.clearAllStudents());
        this.domManager
            .get('SAVE_STUDENTS_BTN')
            .addEventListener('click', () => this.saveChanges());
        this.domManager.get('CANCEL_EDIT_BTN').addEventListener('click', () => this.cancelEdit());
        this.domManager
            .get('ADD_NEW_STUDENT_BTN')
            .addEventListener('click', () => this.addNewStudent());

        // Event delegation for dynamic student actions
        this.domManager.get('STUDENT_LIST').addEventListener('click', (e) => {
            const studentIndex = parseInt(e.target.dataset.studentIndex);

            if (e.target.classList.contains('btn-edit-student')) {
                this.editStudent(studentIndex);
            } else if (e.target.classList.contains('btn-remove-student')) {
                this.removeStudent(studentIndex);
            } else if (e.target.classList.contains('btn-save-student')) {
                this.saveStudentEdit(studentIndex);
            } else if (e.target.classList.contains('btn-cancel-student')) {
                this.cancelStudentEdit(studentIndex);
            }
        });
    }

    setStudents(students) {
        this.students = [...students]; // Create a copy
        this.originalStudents = [...students]; // Backup for cancel
        this.displayStudents();
    }

    getStudents() {
        return this.students;
    }

    displayStudents() {
        const count = this.students.length;
        this.domManager.setText('STUDENT_COUNT', `${count} students ready for team assignment`);

        if (this.isEditMode) {
            this.displayEditableStudents();
        } else {
            this.displayReadOnlyStudents();
        }

        this.domManager.show('STUDENTS_PREVIEW');
        if (count > 0) {
            this.domManager.show('TEAM_CONFIG');
        }
    }

    displayReadOnlyStudents() {
        const studentListHTML = this.students
            .map(
                (student, index) =>
                    `<div class="${CSS_CLASSES.STUDENT_ITEM}">
                        <div class="student-item-content">
                            <div class="student-info">
                                <div class="${CSS_CLASSES.MEMBER_NAME}">${index + 1}. ${
                                    student.name
                                }</div>
                                <div class="${CSS_CLASSES.MEMBER_EMAIL}">${student.email}</div>
                            </div>
                        </div>
                    </div>`
            )
            .join('');

        this.domManager.setContent('STUDENT_LIST', studentListHTML);
        this.domManager.get('STUDENT_LIST').classList.remove('edit-mode');
    }

    displayEditableStudents() {
        const studentListHTML = this.students
            .map(
                (student, index) =>
                    `<div class="${CSS_CLASSES.STUDENT_ITEM}" data-student-index="${index}">
                        <div class="student-item-content" id="student-view-${index}">
                            <div class="student-info">
                                <div class="${CSS_CLASSES.MEMBER_NAME}">${index + 1}. ${
                                    student.name
                                }</div>
                                <div class="${CSS_CLASSES.MEMBER_EMAIL}">${student.email}</div>
                            </div>
                            <div class="student-actions">
                                <button class="btn btn-icon btn-edit btn-edit-student" data-student-index="${index}" title="Edit">
                                    ✏️
                                </button>
                                <button class="btn btn-icon btn-remove btn-remove-student" data-student-index="${index}" title="Remove">
                                    🗑️
                                </button>
                            </div>
                        </div>
                        <div class="student-edit-form hidden" id="student-edit-${index}">
                            <input type="email" class="student-edit-input" value="${
                                student.email
                            }" placeholder="Enter email address" />
                            <button class="btn btn-small btn-save btn-save-student" data-student-index="${index}">
                                ✅ Save
                            </button>
                            <button class="btn btn-small btn-cancel btn-cancel-student" data-student-index="${index}">
                                ❌ Cancel
                            </button>
                        </div>
                    </div>`
            )
            .join('');

        this.domManager.setContent('STUDENT_LIST', studentListHTML);
        this.domManager.get('STUDENT_LIST').classList.add('edit-mode');
    }

    enterEditMode() {
        this.isEditMode = true;
        this.originalStudents = [...this.students]; // Backup current state
        this.displayStudents();
        this.domManager.show('EDIT_MODE_CONTROLS');
        this.domManager.hide('TEAM_CONFIG'); // Hide team config while editing
    }

    exitEditMode() {
        this.isEditMode = false;
        this.displayStudents();
        this.domManager.hide('EDIT_MODE_CONTROLS');
        if (this.students.length > 0) {
            this.domManager.show('TEAM_CONFIG'); // Show team config again
        }
    }

    saveChanges() {
        // Validate all students
        const invalidStudents = this.students.filter(
            (student) => !student.email || !student.email.includes('@')
        );

        if (invalidStudents.length > 0) {
            alert(`Please fix invalid email addresses before saving.`);
            return;
        }

        // Check for duplicates
        const emailCounts = {};
        this.students.forEach((student) => {
            const email = student.email.toLowerCase();
            emailCounts[email] = (emailCounts[email] || 0) + 1;
        });

        const duplicates = Object.keys(emailCounts).filter((email) => emailCounts[email] > 1);
        if (duplicates.length > 0) {
            alert(`Please remove duplicate email addresses: ${duplicates.join(', ')}`);
            return;
        }

        this.exitEditMode();
        StatusManager.showStatus(
            this.domManager.get('UPLOAD_STATUS'),
            STATUS_MESSAGES.UPLOAD_SUCCESS(this.students.length, 'edited list'),
            'success'
        );
    }

    cancelEdit() {
        this.students = [...this.originalStudents]; // Restore backup
        this.exitEditMode();
    }

    clearAllStudents() {
        if (confirm('Are you sure you want to clear all students? This action cannot be undone.')) {
            this.clear();
        }
    }

    addNewStudent() {
        this.students.push({ name: 'New Student', email: 'new.student@example.com' });
        this.displayStudents();
    }

    editStudent(index) {
        // Hide view mode and show edit mode for this student
        const viewElement = document.getElementById(`student-view-${index}`);
        const editElement = document.getElementById(`student-edit-${index}`);

        if (viewElement && editElement) {
            viewElement.classList.add('hidden');
            editElement.classList.remove('hidden');

            // Focus on the input field
            const input = editElement.querySelector('.student-edit-input');
            if (input) input.focus();
        }
    }

    async saveStudentEdit(index) {
        const editElement = document.getElementById(`student-edit-${index}`);
        const input = editElement.querySelector('.student-edit-input');
        const newEmail = input.value.trim();

        if (!newEmail || !newEmail.includes('@')) {
            alert('Please enter a valid email address.');
            return;
        }

        // Check for duplicates with other students
        const isDuplicate = this.students.some(
            (student, i) => i !== index && student.email.toLowerCase() === newEmail.toLowerCase()
        );

        if (isDuplicate) {
            alert('This email address already exists in the list.');
            return;
        }

        try {
            // Use API to get the proper name from email
            const data = await APIService.createManualStudents([newEmail]);

            if (data.success && data.students.length > 0) {
                this.students[index] = data.students[0];
                this.displayStudents();
            } else {
                alert('Failed to process the email address.');
            }
        } catch (error) {
            alert('Error processing email address.');
        }
    }

    cancelStudentEdit(index) {
        // Show view mode and hide edit mode for this student
        const viewElement = document.getElementById(`student-view-${index}`);
        const editElement = document.getElementById(`student-edit-${index}`);

        if (viewElement && editElement) {
            viewElement.classList.remove('hidden');
            editElement.classList.add('hidden');
        }
    }

    removeStudent(index) {
        if (confirm(`Are you sure you want to remove ${this.students[index].name}?`)) {
            this.students.splice(index, 1);
            this.displayStudents();
        }
    }

    clear() {
        this.students = [];
        this.originalStudents = [];
        this.isEditMode = false;
        this.domManager.hide('STUDENTS_PREVIEW');
        this.domManager.hide('TEAM_CONFIG');
        this.domManager.hide('RESULTS_SECTION');
        this.domManager.hide('EDIT_MODE_CONTROLS');
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

                // Check for warnings (duplicates/errors)
                if (data.warnings && data.warnings.length > 0) {
                    StatusManager.showStatus(
                        this.domManager.get('UPLOAD_STATUS'),
                        STATUS_MESSAGES.UPLOAD_SUCCESS_WITH_WARNINGS(
                            data.count,
                            fileType,
                            data.warnings
                        ),
                        'warning'
                    );
                } else {
                    StatusManager.showStatus(
                        this.domManager.get('UPLOAD_STATUS'),
                        STATUS_MESSAGES.UPLOAD_SUCCESS(data.count, fileType),
                        'success'
                    );
                }

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
 * Handles manual student entry UI and interactions
 */
class ManualEntryManager {
    constructor(domManager, studentManager) {
        this.domManager = domManager;
        this.studentManager = studentManager;
        this.setupEventListeners();
        this.setupMethodToggle();
    }

    setupEventListeners() {
        this.domManager.get('ADD_INPUT_BTN').addEventListener('click', () => this.addInputRow());
        this.domManager
            .get('CREATE_FROM_MANUAL_BTN')
            .addEventListener('click', () => this.createTeamsFromManualInput());

        // Set up event delegation for remove buttons
        this.domManager.get('MANUAL_INPUTS_CONTAINER').addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-remove-input')) {
                this.removeInputRow(e.target.closest('.manual-input-row'));
            }
        });

        // Add event listener for Enter key to add new input
        this.domManager.get('MANUAL_INPUTS_CONTAINER').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.classList.contains('manual-name-input')) {
                e.preventDefault();
                this.addInputRow();
                // Focus on the new input field
                setTimeout(() => {
                    const inputs = this.domManager
                        .get('MANUAL_INPUTS_CONTAINER')
                        .querySelectorAll('.manual-name-input');
                    const lastInput = inputs[inputs.length - 1];
                    if (lastInput) lastInput.focus();
                }, 100);
            }
        });

        // Add real-time duplicate detection
        this.domManager.get('MANUAL_INPUTS_CONTAINER').addEventListener('input', (e) => {
            if (e.target.classList.contains('manual-name-input')) {
                this.checkForDuplicates();
            }
        });
    }

    setupMethodToggle() {
        this.domManager
            .get('FILE_METHOD_BTN')
            .addEventListener('click', () => this.switchToFileMethod());
        this.domManager
            .get('MANUAL_METHOD_BTN')
            .addEventListener('click', () => this.switchToManualMethod());

        // Add keyboard navigation for tabs
        this.domManager
            .get('FILE_METHOD_BTN')
            .addEventListener('keydown', (e) => this.handleTabKeydown(e, 'file'));
        this.domManager
            .get('MANUAL_METHOD_BTN')
            .addEventListener('keydown', (e) => this.handleTabKeydown(e, 'manual'));
    }

    handleTabKeydown(event, tabType) {
        switch (event.key) {
            case 'ArrowRight':
            case 'ArrowLeft':
                event.preventDefault();
                if (tabType === 'file') {
                    this.domManager.get('MANUAL_METHOD_BTN').focus();
                } else {
                    this.domManager.get('FILE_METHOD_BTN').focus();
                }
                break;
            case 'Enter':
            case ' ':
                event.preventDefault();
                if (tabType === 'file') {
                    this.switchToFileMethod();
                } else {
                    this.switchToManualMethod();
                }
                break;
        }
    }

    switchToFileMethod() {
        // Update button states and ARIA attributes
        this.domManager.get('FILE_METHOD_BTN').classList.add('tab-button-active');
        this.domManager.get('FILE_METHOD_BTN').setAttribute('aria-selected', 'true');
        this.domManager.get('MANUAL_METHOD_BTN').classList.remove('tab-button-active');
        this.domManager.get('MANUAL_METHOD_BTN').setAttribute('aria-selected', 'false');

        // Show/hide tab panels
        this.domManager.get('FILE_UPLOAD_SECTION').classList.add('tab-panel-active');
        this.domManager.get('MANUAL_ENTRY_SECTION').classList.remove('tab-panel-active');

        // Clear any existing manual data
        this.clearManualInputs();
    }

    switchToManualMethod() {
        // Update button states and ARIA attributes
        this.domManager.get('MANUAL_METHOD_BTN').classList.add('tab-button-active');
        this.domManager.get('MANUAL_METHOD_BTN').setAttribute('aria-selected', 'true');
        this.domManager.get('FILE_METHOD_BTN').classList.remove('tab-button-active');
        this.domManager.get('FILE_METHOD_BTN').setAttribute('aria-selected', 'false');

        // Show/hide tab panels
        this.domManager.get('MANUAL_ENTRY_SECTION').classList.add('tab-panel-active');
        this.domManager.get('FILE_UPLOAD_SECTION').classList.remove('tab-panel-active');

        // Clear any existing file data and focus on first input
        this.studentManager.clear();
        StatusManager.clearStatus(this.domManager.get('UPLOAD_STATUS'));
        const firstInput = this.domManager
            .get('MANUAL_INPUTS_CONTAINER')
            .querySelector('.manual-name-input');
        if (firstInput) firstInput.focus();
    }

    addInputRow() {
        const container = this.domManager.get('MANUAL_INPUTS_CONTAINER');
        const newRow = document.createElement('div');
        newRow.className = 'manual-input-row';
        newRow.innerHTML = `
            <input type="email" class="form-input manual-name-input" placeholder="Enter student email address" />
            <button type="button" class="btn-remove-input" title="Remove">✕</button>
        `;
        container.appendChild(newRow);

        // Focus on the new input
        const newInput = newRow.querySelector('.manual-name-input');
        if (newInput) newInput.focus();

        this.updateRemoveButtonsVisibility();
    }

    removeInputRow(row) {
        const container = this.domManager.get('MANUAL_INPUTS_CONTAINER');
        const rows = container.querySelectorAll('.manual-input-row');

        // Don't allow removing the last row
        if (rows.length > 1) {
            row.remove();
            this.updateRemoveButtonsVisibility();
            this.checkForDuplicates(); // Refresh duplicate checking
        }
    }

    updateRemoveButtonsVisibility() {
        const container = this.domManager.get('MANUAL_INPUTS_CONTAINER');
        const rows = container.querySelectorAll('.manual-input-row');
        const removeButtons = container.querySelectorAll('.btn-remove-input');

        // Hide remove button if only one row exists
        removeButtons.forEach((button) => {
            button.style.display = rows.length > 1 ? 'flex' : 'none';
        });
    }

    getManualInputEmails() {
        const inputs = this.domManager
            .get('MANUAL_INPUTS_CONTAINER')
            .querySelectorAll('.manual-name-input');
        const emails = [];

        inputs.forEach((input) => {
            const email = input.value.trim();
            if (email) {
                emails.push(email);
            }
        });

        return emails;
    }

    clearManualInputs() {
        const container = this.domManager.get('MANUAL_INPUTS_CONTAINER');
        container.innerHTML = `
            <div class="manual-input-row">
                <input type="email" class="form-input manual-name-input" placeholder="Enter student email address" />
                <button type="button" class="btn-remove-input" title="Remove">✕</button>
            </div>
        `;
        this.updateRemoveButtonsVisibility();
        this.checkForDuplicates(); // Refresh duplicate checking
    }

    async createTeamsFromManualInput() {
        const emails = this.getManualInputEmails();

        if (emails.length === 0) {
            StatusManager.showStatus(
                this.domManager.get('UPLOAD_STATUS'),
                STATUS_MESSAGES.UPLOAD_ERROR('Please enter at least one student email'),
                'error'
            );
            return;
        }

        const createBtn = this.domManager.get('CREATE_FROM_MANUAL_BTN');
        const originalText = createBtn.textContent;
        createBtn.textContent = 'Creating...';
        createBtn.disabled = true;

        try {
            // Use API service to create students from emails
            const data = await APIService.createManualStudents(emails);

            if (data.success) {
                this.studentManager.setStudents(data.students);

                // Check for duplicates or errors and show appropriate warnings
                const warnings = [];
                if (data.duplicates && data.duplicates.length > 0) {
                    warnings.push(
                        `Removed ${data.duplicates.length} duplicate email${
                            data.duplicates.length !== 1 ? 's' : ''
                        }`
                    );
                }
                if (data.errors && data.errors.length > 0) {
                    warnings.push(
                        `Skipped ${data.errors.length} invalid email${
                            data.errors.length !== 1 ? 's' : ''
                        }`
                    );
                }

                if (warnings.length > 0) {
                    StatusManager.showStatus(
                        this.domManager.get('UPLOAD_STATUS'),
                        STATUS_MESSAGES.UPLOAD_SUCCESS_WITH_WARNINGS(
                            data.count,
                            'manual entry',
                            warnings
                        ),
                        'warning'
                    );
                } else {
                    StatusManager.showStatus(
                        this.domManager.get('UPLOAD_STATUS'),
                        STATUS_MESSAGES.UPLOAD_SUCCESS(data.count, 'manual entry'),
                        'success'
                    );
                }
            } else {
                StatusManager.showStatus(
                    this.domManager.get('UPLOAD_STATUS'),
                    STATUS_MESSAGES.UPLOAD_ERROR(data.error),
                    'error'
                );
            }
        } catch (error) {
            StatusManager.showStatus(
                this.domManager.get('UPLOAD_STATUS'),
                STATUS_MESSAGES.UPLOAD_FAILED(error.message),
                'error'
            );
        } finally {
            createBtn.textContent = originalText;
            createBtn.disabled = false;
        }
    }

    checkForDuplicates() {
        const inputs = this.domManager
            .get('MANUAL_INPUTS_CONTAINER')
            .querySelectorAll('.manual-name-input');
        const emailCounts = {};

        // Count occurrences of each email
        inputs.forEach((input) => {
            const email = input.value.trim().toLowerCase();
            if (email) {
                emailCounts[email] = (emailCounts[email] || 0) + 1;
            }
        });

        // Mark duplicates
        inputs.forEach((input) => {
            const email = input.value.trim().toLowerCase();
            const isDuplicate = email && emailCounts[email] > 1;

            if (isDuplicate) {
                input.classList.add('duplicate-email');
                input.title = 'Duplicate email address';
            } else {
                input.classList.remove('duplicate-email');
                input.title = '';
            }
        });
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
        this.manualEntryManager = new ManualEntryManager(this.domManager, this.studentManager);

        this.initialize();
    }

    initialize() {
        this.setupEventListeners();
        this.teamManager.updateMethodLabel();
        // Initialize the remove button visibility for manual entry
        this.manualEntryManager.updateRemoveButtonsVisibility();
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
