--- nocodb/api_integration.js (原始)


+++ nocodb/api_integration.js (修改后)
/**
 * NocoDB API Integration for SupportDesk Analytics
 *
 * This script connects the MVP_UI.html frontend with NocoDB backend.
 * Include this script after bootstrap and before your main application code.
 */

// Configuration
const NOCODB_CONFIG = {
    baseUrl: 'http://localhost:8080/api/v1',
    token: '', // Set your NocoDB API token here
    tables: {
        tickets: 'Tickets',
        categories: 'Categories',
        statuses: 'Statuses',
        priorities: 'Priorities',
        departments: 'Departments',
        employees: 'Employees',
        comments: 'Comments'
    }
};

// API Client
class NocoDBClient {
    constructor(config) {
        this.baseUrl = config.baseUrl;
        this.token = config.token;
        this.tables = config.tables;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['xc-token'] = this.token;
        }

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return response.json();
    }

    // Tickets
    async getTickets(filters = {}) {
        const params = new URLSearchParams();

        if (filters.status) {
            params.append('where', `(status_id,eq,${filters.status})`);
        }
        if (filters.priority) {
            params.append('where', `(priority_id,eq,${filters.priority})`);
        }
        if (filters.assignee) {
            params.append('where', `(assignee_id,eq,${filters.assignee})`);
        }
        if (filters.search) {
            params.append('where', `(title,like,${encodeURIComponent(filters.search)})`);
        }

        const queryString = params.toString();
        const endpoint = `/tables/${this.tables.tickets}/records${queryString ? '?' + queryString : ''}`;
        return this.request(endpoint);
    }

    async getTicket(id) {
        return this.request(`/tables/${this.tables.tickets}/records/${id}`);
    }

    async createTicket(ticketData) {
        return this.request(`/tables/${this.tables.tickets}/records`, {
            method: 'POST',
            body: JSON.stringify(ticketData)
        });
    }

    async updateTicket(id, ticketData) {
        return this.request(`/tables/${this.tables.tickets}/records/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(ticketData)
        });
    }

    // Categories
    async getCategories() {
        return this.request(`/tables/${this.tables.categories}/records`);
    }

    // Statuses
    async getStatuses() {
        return this.request(`/tables/${this.tables.statuses}/records`);
    }

    // Priorities
    async getPriorities() {
        return this.request(`/tables/${this.tables.priorities}/records`);
    }

    // Departments
    async getDepartments() {
        return this.request(`/tables/${this.tables.departments}/records`);
    }

    // Employees
    async getEmployees() {
        return this.request(`/tables/${this.tables.employees}/records`);
    }

    // Comments
    async getComments(ticketId) {
        const params = new URLSearchParams(`(ticket_id,eq,${ticketId})`);
        return this.request(`/tables/${this.tables.comments}/records?where=${params}`);
    }

    async addComment(commentData) {
        return this.request(`/tables/${this.tables.comments}/records`, {
            method: 'POST',
            body: JSON.stringify(commentData)
        });
    }

    // Dashboard Statistics
    async getDashboardStats() {
        const [tickets, categories, statuses] = await Promise.all([
            this.getTickets(),
            this.getCategories(),
            this.getStatuses()
        ]);

        const total = tickets.list?.length || 0;
        const inProgress = tickets.list?.filter(t => t.status_id === 2).length || 0;
        const resolved = tickets.list?.filter(t => t.status_id === 3).length || 0;
        const closed = tickets.list?.filter(t => t.status_id === 4).length || 0;
        const overdue = tickets.list?.filter(t => t.sla_elapsed_percent >= 100 && t.status_id !== 4).length || 0;
        const slaMet = total > 0 ? ((resolved + closed) / total * 100).toFixed(0) : 0;

        return {
            total,
            inProgress,
            slaMet,
            overdue
        };
    }
}

// Initialize client
const nocodb = new NocoDBClient(NOCODB_CONFIG);

// Demo mode - uses mock data if API is not available
let useDemoMode = false;

async function initApp() {
    try {
        // Try to connect to NocoDB
        await nocodb.getCategories();
        console.log('Connected to NocoDB');
        useDemoMode = false;
    } catch (error) {
        console.warn('NocoDB not available, using demo mode:', error);
        useDemoMode = true;
        loadDemoData();
    }
}

// Demo Data (matches the UI prototype)
const demoData = {
    stats: {
        total: 156,
        inProgress: 24,
        slaMet: 94,
        overdue: 3
    },
    tickets: [
        {
            id: 1247,
            title: 'Не работает принтер в бухгалтерии',
            status_id: 2,
            status_name: 'В работе',
            priority_id: 3,
            priority_name: 'Высокий',
            initiator_name: 'Елена Смирнова',
            department_name: 'Бухгалтерия',
            assignee_name: 'Алексей Сидоров',
            sla_elapsed_percent: 75,
            created_at: '2025-01-15T09:30:00'
        },
        {
            id: 1246,
            title: 'Настройка VPN для удалённого доступа',
            status_id: 1,
            status_name: 'Новая',
            priority_id: 2,
            priority_name: 'Средний',
            initiator_name: 'Дмитрий Волков',
            department_name: 'Отдел продаж',
            assignee_name: null,
            sla_elapsed_percent: 30,
            created_at: '2025-01-15T10:15:00'
        },
        {
            id: 1245,
            title: 'Замена картриджа в кабинете 305',
            status_id: 3,
            status_name: 'Решена',
            priority_id: 1,
            priority_name: 'Низкий',
            initiator_name: 'Ольга Новикова',
            department_name: 'HR',
            assignee_name: 'Алексей Сидоров',
            sla_elapsed_percent: 100,
            created_at: '2025-01-14T14:00:00'
        }
    ],
    categories: [
        { id: 1, name: 'Оборудование' },
        { id: 2, name: 'Программное обеспечение' },
        { id: 3, name: 'Сеть' },
        { id: 4, name: 'Доступы' },
        { id: 5, name: 'Расходные материалы' }
    ],
    statuses: [
        { id: 1, name: 'Новая', code: 'new' },
        { id: 2, name: 'В работе', code: 'in_progress' },
        { id: 3, name: 'Решена', code: 'resolved' },
        { id: 4, name: 'Закрыта', code: 'closed' }
    ],
    priorities: [
        { id: 4, name: 'Критический', level: 4 },
        { id: 3, name: 'Высокий', level: 3 },
        { id: 2, name: 'Средний', level: 2 },
        { id: 1, name: 'Низкий', level: 1 }
    ],
    departments: [
        { id: 1, name: 'Бухгалтерия' },
        { id: 2, name: 'Отдел продаж' },
        { id: 3, name: 'HR' },
        { id: 4, name: 'IT' }
    ],
    employees: [
        { id: 1, full_name: 'Иван Петров', position: 'Руководитель поддержки', avatar_initials: 'ИП' },
        { id: 2, full_name: 'Алексей Сидоров', position: 'IT-специалист', avatar_initials: 'АС' },
        { id: 3, full_name: 'Мария Козлова', position: 'Системный администратор', avatar_initials: 'МК' }
    ]
};

function loadDemoData() {
    console.log('Loaded demo data');
}

// Helper functions for UI integration
function getStatusClass(statusCode) {
    const statusMap = {
        'new': 'status-new',
        'in_progress': 'status-in-progress',
        'resolved': 'status-resolved',
        'closed': 'status-closed'
    };
    return statusMap[statusCode] || 'status-new';
}

function getPriorityClass(priorityLevel) {
    if (priorityLevel >= 3) return 'priority-high';
    if (priorityLevel === 2) return 'priority-medium';
    return 'priority-low';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export for use in MVP_UI.html
window.NocoDBClient = NocoDBClient;
window.nocodb = nocodb;
window.demoData = demoData;
window.useDemoMode = () => useDemoMode;
window.initApp = initApp;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}